"""Foreground, authenticated loopback adapter; all product behavior stays engine-owned."""

import argparse
import hmac
import json
import re
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.metadata import version
from io import BufferedIOBase
from pathlib import Path, PureWindowsPath
from threading import Timer
from time import monotonic
from typing import Any, cast
from uuid import UUID

from personalstyle.config import load_config
from personalstyle.feedback import FeedbackInput, record_feedback
from personalstyle.generation import MAX_REQUEST_BYTES, RewriteRequest, generate_pair
from personalstyle.learning import evaluate_context_preferences
from personalstyle.provider import GenerationError, ModelProvider
from personalstyle.storage import ExampleInput, ExampleStore, StoreError
from personalstyle.verification import deterministic_failures, verify_pair

PROTOCOL_VERSION = "1.0"
CAPABILITIES = ("handshake", "rewrite", "example.write", "feedback.write", "preference.evaluate")
MAX_BODY_BYTES = MAX_REQUEST_BYTES + 4096
MAX_HEADER_BYTES = 8192
ENGINE_CODES = frozenset({
    "INVALID_REQUEST", "INVALID_EXAMPLE", "INVALID_FEEDBACK", "IDEMPOTENCY_CONFLICT",
    "VERIFIED_SOURCE_INVALID", "FEEDBACK_SOURCE_INVALID", "PREFERENCE_SOURCE_INVALID",
    "STORAGE_BOUNDARY_INVALID", "STORAGE_MIGRATION_REQUIRED", "DATABASE_UNAVAILABLE_OR_CORRUPT",
    "TRANSACTION_FAILED", "PERSISTENCE_VERIFICATION_FAILED", "NO_ELIGIBLE_EXAMPLES",
    "PROFILE_RESOURCE_LIMIT", "PROFILE_SOURCE_INVALID", "PROFILE_VERSION_INCOMPATIBLE",
    "MODEL_CALL_BUDGET_EXHAUSTED", "MODEL_IDENTITY_MISMATCH", "MODEL_UNAVAILABLE", "MODEL_INCOMPATIBLE",
    "MODEL_PREPARATION_TIMEOUT", "MODEL_RUNTIME_UNAVAILABLE", "MODEL_RESPONSE_INVALID",
    "GENERATION_RESOURCE_LIMIT", "PERSONALIZATION_CONTEXT_LIMIT", "PERSONALIZATION_SOURCE_CHANGED",
    "VERIFIER_RESPONSE_INVALID", "GENERATION_ATTEMPTS_EXHAUSTED", "VERIFICATION_REPEATED_FAILURE",
    "IDENTICAL_REPAIR", "CONTEXT_INAPPROPRIATE", "MEANING_CHANGED", "REQUIRED_FACTS_CHANGED",
    "REQUIRED_INFORMATION_MISSING", "STRUCTURAL_CONSTRAINT_FAILED", "USER_CONSTRAINT_FAILED",
    "VERIFICATION_INPUT_INVALID",
})


class ProtocolError(ValueError):
    def __init__(self, code: str, status: int = 400, engine_code: str | None = None):
        super().__init__(code)
        self.code, self.status = code, status
        self.engine_code = engine_code if engine_code in ENGINE_CODES else None


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("REQUEST_MALFORMED")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ProtocolError("REQUEST_MALFORMED")


def _json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_object, parse_constant=_nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise ProtocolError("REQUEST_MALFORMED") from None


def _validate(envelope: Any) -> tuple[str, Any]:
    """Validate wire shape and reuse authoritative pure input validators before dispatch."""
    if not isinstance(envelope, dict) or not {
        "protocol_version", "client_version", "client_kind", "requested_capability", "payload",
    } <= envelope.keys():
        raise ProtocolError("REQUEST_MALFORMED")
    protocol, client = envelope["protocol_version"], envelope["client_version"]
    if (
        type(protocol) is not str or len(protocol) > 32
        or re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", protocol) is None
        or type(client) is not str or len(client) > 32
        or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", client) is None
    ):
        raise ProtocolError("REQUEST_MALFORMED")
    if protocol.split(".")[0] != "1":
        raise ProtocolError("PROTOCOL_MAJOR_INCOMPATIBLE", 409)
    if envelope["client_kind"] not in ("desktop", "cli"):
        raise ProtocolError("ORIGIN_CALLER_REJECTED", 403)
    capability = envelope["requested_capability"]
    if type(capability) is not str or capability not in CAPABILITIES:
        raise ProtocolError("CAPABILITY_UNSUPPORTED", 422)
    data = envelope["payload"]
    if not isinstance(data, dict):
        raise ProtocolError("REQUEST_MALFORMED")
    try:
        if capability == "handshake":
            if data:
                raise ProtocolError("REQUEST_MALFORMED")
            return capability, protocol
        if capability == "rewrite":
            if data.keys() != {"original", "intent", "context", "constraints"} or type(data["constraints"]) is not list:
                raise ProtocolError("REQUEST_MALFORMED")
            rewrite = RewriteRequest(**{**data, "constraints": tuple(data["constraints"])})
            rewrite.validate()
            deterministic_failures(rewrite, rewrite.original)
            return capability, rewrite
        if capability == "example.write":
            example = ExampleInput(**data)
            example.validate()
            return capability, example
        if capability == "feedback.write":
            if data.keys() != {"run_id", "event"} or str(UUID(data["run_id"])) != data["run_id"]:
                raise ProtocolError("REQUEST_MALFORMED")
            event = FeedbackInput(**data["event"])
            event.validate()
            return capability, (data["run_id"], event)
        if data.keys() != {"context"} or type(data["context"]) is not str or re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", data["context"]) is None:
            raise ProtocolError("REQUEST_MALFORMED")
        return capability, data["context"]
    except (TypeError, ValueError, AttributeError):
        raise ProtocolError("REQUEST_MALFORMED") from None


class EngineSession:
    """One engine/store per process; retain one live verified source, never client flags."""

    def __init__(self, settings: dict[str, Any], store: ExampleStore, credential: str,
                 provider: ModelProvider | None = None):
        if type(credential) is not str or re.fullmatch(r"[A-Za-z0-9_-]{43}", credential) is None:
            raise ProtocolError("AUTHENTICATION_INVALID", 401)
        if settings["versions"]["protocol"] != PROTOCOL_VERSION:
            raise ProtocolError("PROTOCOL_MAJOR_INCOMPATIBLE", 409)
        self._authorization = ("Bearer " + credential).encode("ascii")
        self.settings, self.store, self.provider = settings, store, provider
        self._verified: dict[str, Any] | None = None

    def execute(self, capability: str, data: Any) -> Any:
        if capability == "handshake":
            return {"engine_version": version("personalstyle"), "protocol_version": PROTOCOL_VERSION,
                    "requested_protocol_version": data, "supported_capabilities": CAPABILITIES,
                    "compatibility": "compatible"}
        if capability == "rewrite":
            pair = generate_pair(data, self.settings, self.store, provider=self.provider)
            result = verify_pair(data, pair, self.settings, self.store, provider=self.provider)
            if result["state"] != "SUCCEEDED":
                raise ProtocolError("ENGINE_OPERATION_FAILED", 422, result["failure_code"])
            self._verified = result
            return result
        if capability == "example.write":
            example = self.store.add(data)
            return {"id": example["id"], "record_version": example["record_version"]}
        if capability == "feedback.write":
            run_id, event = data
            if self._verified is None or self._verified["run_id"] != run_id:
                raise ProtocolError("SOURCE_RUN_UNAVAILABLE", 409)
            feedback = record_feedback(self.store, self._verified, event)
            return {"id": feedback["event"]["id"], "classification": feedback["classification"],
                    "record_version": feedback["record_version"], "profile_version": feedback["profile_version"]}
        return evaluate_context_preferences(self.store, data)


class _HeaderBudget:
    def __init__(self, stream: BufferedIOBase):
        self.stream, self.remaining = stream, MAX_HEADER_BYTES

    def readline(self, size: int = -1) -> bytes:
        line = self.stream.readline(min(size, self.remaining + 1) if size >= 0 else self.remaining + 1)
        self.remaining -= len(line)
        if self.remaining < 0:
            raise ProtocolError("REQUEST_RESOURCE_LIMIT", 413)
        return line

    def __getattr__(self, name: str) -> Any:
        return getattr(self.stream, name)


class EngineServer(HTTPServer):
    request_queue_size = 1

    def __init__(self, session: EngineSession, port: int = 0):
        self.session = session
        super().__init__(("127.0.0.1", port), _Handler)

    def handle_error(self, request: Any, client_address: Any) -> None:
        pass  # Never let socket/server diagnostics expose a request or exception contents.


class _Handler(BaseHTTPRequestHandler):
    server: EngineServer
    server_version, sys_version = "PersonalStyle", ""

    def setup(self) -> None:
        super().setup()
        self.request_version = "HTTP/1.0"
        self.rfile = cast(BufferedIOBase, _HeaderBudget(self.rfile))
        seconds = min(60, self.server.session.settings["harness"]["timeout_seconds"])
        self._deadline = monotonic() + seconds
        self.connection.settimeout(seconds)
        self._timer = Timer(seconds, self._expire)
        self._timer.daemon = True
        self._timer.start()

    def _expire(self) -> None:
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def finish(self) -> None:
        self._timer.cancel()
        super().finish()

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _reply(self, status: int, value: dict[str, Any]) -> None:
        payload = json.dumps({"protocol_version": PROTOCOL_VERSION, **value}, ensure_ascii=False).encode()
        self.close_connection = True
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        self._reply(code, {"ok": False, "error": {"code": "REQUEST_RESOURCE_LIMIT" if code == 431 else "REQUEST_MALFORMED"}})

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except ProtocolError as error:
            self._reply(error.status, {"ok": False, "error": {"code": error.code}})
        except (OSError, ValueError):
            self.close_connection = True

    def do_POST(self) -> None:
        try:
            if "Origin" in self.headers:
                raise ProtocolError("ORIGIN_CALLER_REJECTED", 403)
            auth = self.headers.get_all("Authorization", [])
            if not auth:
                raise ProtocolError("AUTHENTICATION_REQUIRED", 401)
            if len(auth) != 1 or not hmac.compare_digest(auth[0].encode("latin-1"), self.server.session._authorization):
                raise ProtocolError("AUTHENTICATION_INVALID", 401)
            lengths = self.headers.get_all("Content-Length", [])
            if (
                self.path != "/v1" or len(lengths) != 1
                or re.fullmatch(r"0|[1-9][0-9]{0,5}", lengths[0]) is None
                or any(h in self.headers for h in ("Transfer-Encoding", "Content-Encoding", "Expect"))
                or self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json"
            ):
                raise ProtocolError("REQUEST_MALFORMED")
            length = int(lengths[0])
            if length > MAX_BODY_BYTES:
                raise ProtocolError("REQUEST_RESOURCE_LIMIT", 413)
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ProtocolError("REQUEST_MALFORMED")
            capability, data = _validate(_json(raw))
            if monotonic() >= self._deadline:
                raise ProtocolError("REQUEST_RESOURCE_LIMIT", 408)
            self._timer.cancel()  # Ingress ceiling must not shorten legitimate engine operations.
            result = self.server.session.execute(capability, data)
            self._reply(200, {"ok": True, "result": result})
        except (StoreError, GenerationError) as error:
            self._reply(422, {"ok": False, "error": {"code": "ENGINE_OPERATION_FAILED",
                         "engine_code": str(error) if str(error) in ENGINE_CODES else "ENGINE_OPERATION_FAILED"}})
        except ProtocolError as error:
            value = {"code": error.code}
            if error.engine_code is not None:
                value["engine_code"] = error.engine_code
            self._reply(error.status, {"ok": False, "error": value})
        except Exception as error:
            raise ProtocolError("ENGINE_OPERATION_FAILED", 500) from error


def main() -> None:
    parser = argparse.ArgumentParser(description="PersonalStyle foreground loopback engine")
    parser.add_argument("--config", type=Path, default=Path("personalstyle.toml"))
    parser.add_argument("--port", type=int, default=0)
    options = parser.parse_args()
    server = None
    try:
        startup = sys.stdin.buffer.readline(256)
        value = _json(startup)
        if len(startup) >= 256 or not isinstance(value, dict) or value.keys() != {"credential"}:
            raise ProtocolError("AUTHENTICATION_INVALID", 401)
        settings = load_config(options.config)
        path = options.config.absolute().parent.joinpath(*PureWindowsPath(settings["storage"]["path"]).parts)
        session = EngineSession(settings, ExampleStore(path), value["credential"])
        server = EngineServer(session, options.port)
        print(json.dumps({"state": "READY", "host": "127.0.0.1", "port": server.server_port,
                          "protocol_version": PROTOCOL_VERSION}), flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as error:
        raise ProtocolError("ENGINE_OPERATION_FAILED", 500) from error
    finally:
        if server is not None:
            server.server_close()


if __name__ == "__main__":
    try:
        main()
    except ProtocolError:
        print(json.dumps({"error": {"code": "ENGINE_OPERATION_FAILED"}}), file=sys.stderr)
        raise SystemExit(1) from None
