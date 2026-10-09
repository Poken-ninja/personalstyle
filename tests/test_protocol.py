import copy
import http.client
import json
import secrets
import socket
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from threading import Thread
from time import monotonic
from types import SimpleNamespace
from typing import ClassVar
from uuid import uuid4

import pytest

from personalstyle.config import load_config
from personalstyle.feedback import FeedbackInput
from personalstyle.protocol import (
    CAPABILITIES,
    CLOSE_GRACE_SECONDS,
    MAX_BODY_BYTES,
    EngineServer,
    EngineSession,
)
from personalstyle.provider import Candidate, PreparedModel
from personalstyle.security import prepare_private_directory
from personalstyle.storage import ExampleInput, ExampleStore, StoreError
from personalstyle.verification import CHECKS, VERIFY_SYSTEM

TEXT = "Alex will deliver 12 reports on Monday. Thank you."
EDIT = "Alex will deliver 12 reports on Monday.\n\nThank you."


def envelope(capability="handshake", payload=None, **metadata):
    return {"protocol_version": "1.0", "client_version": "0.1.0", "client_kind": "desktop",
            "requested_capability": capability, "payload": {} if payload is None else payload,
            **metadata}


@contextmanager
def serving(session):
    server = EngineServer(session)
    worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    worker.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        worker.join(3)
        assert not worker.is_alive()


def request(server, token, value=None, *, raw=None, headers=None, path="/v1"):
    wire = json.dumps(envelope() if value is None else value).encode() if raw is None else raw
    fields = {"Content-Type": "application/json"}
    if token is not None:
        fields["Authorization"] = "Bearer " + token
    fields.update(headers or {})
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=60)
    try:
        connection.request("POST", path, wire, fields)
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


class SpySession(EngineSession):
    def execute(self, capability, data):
        self.calls.append(capability)
        if self.failure is not None:
            raise self.failure
        return super().execute(capability, data) if capability == "handshake" else {"executed": True}


@pytest.fixture
def boundary(tmp_path):
    settings = load_config(Path(__file__).resolve().parents[1] / "personalstyle.toml")
    token = secrets.token_urlsafe(32)
    session = SpySession(settings, ExampleStore(tmp_path / "never-opened.db"), token)
    session.calls, session.failure = [], None
    with serving(session) as server:
        yield server, session, token
    assert not list(tmp_path.iterdir())


def test_loopback_auth_handshake_revocation_and_no_logs(boundary, caplog, capsys):
    server, session, token = boundary
    assert server.server_address[0] == "127.0.0.1"
    assert request(server, None)[1]["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert request(server, "wrong")[1]["error"]["code"] == "AUTHENTICATION_INVALID"
    assert not session.calls
    for protocol in ("1.0", "1.7", "1.10000"):
        status, body = request(server, token, envelope(protocol_version=protocol, future_metadata=True))
        assert status == 200 and body["ok"]
        result = body["result"]
        assert result["compatibility"] == "compatible" and result["engine_version"] == "0.1.0"
        assert result["protocol_version"] == "1.0" and result["requested_protocol_version"] == protocol
        assert result["supported_capabilities"] == list(CAPABILITIES)
    replacement = EngineSession(session.settings, session.store, secrets.token_urlsafe(32))
    with serving(replacement) as restarted:
        assert request(restarted, token)[0] == 401
    assert token not in caplog.text + str(capsys.readouterr())


@pytest.mark.parametrize("value,headers,code", [
    (envelope(protocol_version="2.0"), {}, "PROTOCOL_MAJOR_INCOMPATIBLE"),
    (envelope("sqlite.write"), {}, "CAPABILITY_UNSUPPORTED"),
    (envelope(client_kind="browser"), {}, "ORIGIN_CALLER_REJECTED"),
    (envelope(), {"Origin": "https://example.com"}, "ORIGIN_CALLER_REJECTED"),
    (envelope(), {"Origin": ""}, "ORIGIN_CALLER_REJECTED"),
    (envelope(protocol_version="1"), {}, "REQUEST_MALFORMED"),
    (envelope(client_version="bad"), {}, "REQUEST_MALFORMED"),
    (envelope(payload={"database_path": "other.db"}), {}, "REQUEST_MALFORMED"),
    (envelope("rewrite", {"verified": True}), {}, "REQUEST_MALFORMED"),
    (envelope("preference.evaluate", {"context": "*"}), {}, "REQUEST_MALFORMED"),
    (envelope("feedback.write", {"run_id": str(uuid4()), "event": {}, "receipt": {}}), {}, "REQUEST_MALFORMED"),
    (envelope(), {"Content-Encoding": "gzip"}, "REQUEST_MALFORMED"),
    (envelope(), {"Transfer-Encoding": "chunked"}, "REQUEST_MALFORMED"),
    (envelope(), {"Content-Length": str(MAX_BODY_BYTES + 1)}, "REQUEST_RESOURCE_LIMIT"),
])
def test_pre_dispatch_rejections(boundary, value, headers, code):
    server, session, token = boundary
    for _ in range(20):
        status, body = request(server, token, value, headers=headers)
        assert status >= 400 and body["error"]["code"] == code and not session.calls


@pytest.mark.parametrize("raw", [b"{", b'{"payload":{},"payload":{}}', b"NaN", b"[" * 1200, b"\xff"])
def test_invalid_json_is_bounded_before_dispatch(boundary, raw):
    server, session, token = boundary
    for _ in range(20):
        assert request(server, token, raw=raw)[1]["error"]["code"] == "REQUEST_MALFORMED"
    assert not session.calls


@pytest.mark.parametrize("kind,code", [
    ("oversized", "REQUEST_RESOURCE_LIMIT"),
    ("origin", "ORIGIN_CALLER_REJECTED"),
    ("malformed", "REQUEST_MALFORMED"),
    ("bad_auth", "AUTHENTICATION_INVALID"),
    ("missing_auth", "AUTHENTICATION_REQUIRED"),
])
def test_early_rejection_with_unread_body_stress(boundary, kind, code, caplog, capsys):
    server, session, token = boundary
    sensitive = "PRIVATE_TRANSPORT_BODY"
    wire = (sensitive * 4000).encode()[:MAX_BODY_BYTES + 1]
    headers = {}
    if kind == "origin":
        headers["Origin"] = "https://example.com"
    elif kind == "malformed":
        headers["Content-Type"] = "text/plain"
    credential = "invalid" if kind == "bad_auth" else None if kind == "missing_auth" else token
    for _ in range(20):
        status, body = request(server, credential, raw=wire, headers=headers)
        assert status >= 400 and body["error"]["code"] == code
        assert sensitive not in json.dumps(body) and token not in json.dumps(body)
    assert not session.calls
    diagnostics = caplog.text + str(capsys.readouterr())
    assert sensitive not in diagnostics and token not in diagnostics


def test_stalled_rejected_body_receives_response_without_waiting_for_body(boundary):
    server, session, token = boundary
    for _ in range(20):
        with socket.create_connection(server.server_address, timeout=3) as connection:
            connection.sendall((
                f"POST /v1 HTTP/1.0\r\nAuthorization: Bearer {token}\r\n"
                f"Content-Length: {MAX_BODY_BYTES + 1}\r\n"
                "Content-Type: application/json\r\n\r\nx"
            ).encode())
            started = monotonic()
            response = http.client.HTTPResponse(connection)
            response.begin()
            assert json.loads(response.read())["error"]["code"] == "REQUEST_RESOURCE_LIMIT"
            assert monotonic() - started < 3
            response.close()
    assert not session.calls


@pytest.mark.parametrize("stalled", [False, True])
def test_close_discard_has_fixed_byte_time_bounds(stalled):
    class Peer:
        discarded = 0
        timeouts: ClassVar[list[float]] = []
        closed = False
        write_shutdown = False

        def shutdown(self, how):
            assert how == socket.SHUT_WR
            self.write_shutdown = True

        def settimeout(self, seconds):
            assert 0 < seconds <= CLOSE_GRACE_SECONDS
            self.timeouts.append(seconds)

        def recv(self, size):
            assert self.write_shutdown
            if stalled:
                raise TimeoutError
            self.discarded += size
            return b"x" * size

    peer = Peer()
    server = SimpleNamespace(close_request=lambda request: setattr(request, "closed", True))
    EngineServer.shutdown_request(server, peer)
    assert peer.closed and peer.write_shutdown
    assert peer.discarded <= MAX_BODY_BYTES
    assert peer.timeouts
    if not stalled:
        assert peer.discarded == MAX_BODY_BYTES


def test_invalid_constraint_rejected_before_dispatch(boundary):
    server, session, token = boundary
    status, body = request(server, token, envelope("rewrite", {
        "original": TEXT, "intent": "Make concise", "context": "work.email",
        "constraints": ["max_words:0"],
    }))
    assert status == 400 and body["error"]["code"] == "REQUEST_MALFORMED"
    assert not session.calls


def test_header_and_input_bounds_and_sanitized_errors(boundary, caplog, capsys):
    server, session, token = boundary
    assert request(server, token, headers={"X-Padding": "x" * 8200})[0] == 413
    sensitive = "PRIVATE_WRITING_SENTINEL"
    assert request(server, token, envelope("rewrite", {
        "original": sensitive * 4000, "intent": "Rewrite", "context": "work.email", "constraints": [],
    }))[0] == 413
    assert request(server, token, envelope("rewrite", {
        "original": TEXT, "intent": "x" * 1025, "context": "work.email", "constraints": [],
    }))[0] == 400
    assert not session.calls
    session.failure = RuntimeError(sensitive + token)
    assert request(server, token)[1]["error"] == {"code": "ENGINE_OPERATION_FAILED"}
    session.failure = StoreError("STORAGE_BOUNDARY_INVALID")
    assert request(server, token)[1]["error"]["engine_code"] == "STORAGE_BOUNDARY_INVALID"
    session.failure = StoreError(sensitive)
    body = request(server, token)[1]
    assert sensitive not in json.dumps(body) and token not in json.dumps(body)
    assert sensitive not in caplog.text + str(capsys.readouterr())


@pytest.mark.parametrize("duplicate", ["Authorization", "Content-Length"])
def test_duplicate_headers_rejected(boundary, duplicate):
    server, session, token = boundary
    value = "Bearer " + token if duplicate == "Authorization" else "2"
    wire = (f"POST /v1 HTTP/1.0\r\nAuthorization: Bearer {token}\r\nContent-Length: 2\r\n"
            f"Content-Type: application/json\r\n{duplicate}: {value}\r\n\r\n{{}}").encode()
    with socket.create_connection(server.server_address, timeout=3) as connection:
        connection.sendall(wire)
        response = connection.makefile("rb").read()
    assert b'"ok": false' in response and not session.calls


def test_absolute_ingress_timeout_does_not_invoke_engine(boundary):
    server, session, _token = boundary
    session.settings = copy.deepcopy(session.settings)
    session.settings["harness"]["timeout_seconds"] = 1
    for _ in range(20):
        with socket.create_connection(server.server_address, timeout=3) as connection:
            connection.sendall(b"POST /v1 HTTP/1.0\r\n")
            assert connection.recv(1) == b""
    assert not session.calls


class FixtureProvider:
    def __init__(self):
        self.calls = []
        self.invalid = False

    def prepare(self, context_tokens):
        self.calls.append(("prepare", context_tokens))
        return PreparedModel("ollama", "qwen3:8b", "a" * 64, "0.40.0", context_tokens, 1472, 0.01)

    def generate(self, prepared, messages, **options):
        self.calls.append((messages[0]["content"], options))
        text = json.dumps(dict.fromkeys(CHECKS, True)) if messages[0]["content"] == VERIFY_SYSTEM else TEXT
        if self.invalid:
            text = TEXT.replace("12", "13")
        return Candidate(text, 0.01, 100, 40)


def test_existing_verified_workflow_protected_mutations_preferences_and_provenance(tmp_path, caplog, capsys):
    settings = load_config(Path(__file__).resolve().parents[1] / "personalstyle.toml")
    original_settings = copy.deepcopy(settings)
    prepare_private_directory(tmp_path / "data")
    store = ExampleStore(tmp_path / "data" / "profile.db")
    provider, token = FixtureProvider(), secrets.token_urlsafe(32)
    session = EngineSession(settings, store, token, provider)
    with serving(session) as server:
        example = asdict(ExampleInput(str(uuid4()), "Synthetic example.", "work.email",
                                      "owner", "owner", "user_owned", True, True, False))
        write = envelope("example.write", example)
        status, saved = request(server, token, write)
        assert status == 200 and request(server, token, write)[1] == saved
        before = store.path.read_bytes()
        last_run = None
        for _ in range(3):
            status, rewritten = request(server, token, envelope("rewrite", {
                "original": TEXT, "intent": "Make concise", "context": "work.email", "constraints": [],
            }))
            assert status == 200, rewritten
            pair = rewritten["result"]
            assert pair["state"] == "SUCCEEDED" and pair["model_calls"] == 5
            assert all(c["verification_status"] == "verified" for c in pair["candidates"].values())
            assert store.path.read_bytes() == before
            event = asdict(FeedbackInput(str(uuid4()), "edit", "personalized", "owner", "owner",
                                         True, True, False, EDIT, classification_hint="style_expression"))
            feedback = envelope("feedback.write", {"run_id": pair["run_id"], "event": event})
            status, recorded = request(server, token, feedback)
            assert status == 200 and recorded["result"]["classification"] == "style_expression", recorded
            assert request(server, token, feedback)[1] == recorded
            before = store.path.read_bytes()
            last_run = pair["run_id"]
        evaluation = envelope("preference.evaluate", {"context": "work.email"})
        status, evaluated = request(server, token, evaluation)
        assert status == 200 and all(p["state"] == "active" for p in evaluated["result"])
        assert request(server, token, evaluation)[1] == evaluated
        assert request(server, token, envelope("preference.evaluate", {"context": "friends.chat"}))[1]["result"] == []
        before = store.path.read_bytes()
        status, final = request(server, token, envelope("rewrite", {
            "original": TEXT, "intent": "Make concise", "context": "work.email", "constraints": [],
        }))
        assert status == 200, final
        pair = final["result"]
        personalized = pair["candidates"]["personalized"]
        assert personalized["selected_examples"] == [{"id": example["id"], "record_version": 1}]
        assert personalized["selected_preferences"] == [{"id": p["id"], "version": p["version"]} for p in evaluated["result"]]
        assert personalized["writing_dna_source"]["source_fingerprint"]
        assert pair["versions"] == settings["versions"] and pair["prompt_contract"] == 1
        assert pair["model_identity"]["digest"] == "a" * 64
        assert pair["model_identity"]["model"] == "qwen3:8b"
        assert store.path.read_bytes() == before and settings == original_settings
        assert len(provider.calls) == 20  # Four runs: one prepare + two generation + two verification.
        assert all(c[1]["timeout_seconds"] == 60 for c in provider.calls if c[0] != "prepare")
        assert request(server, token, envelope("feedback.write", {"run_id": last_run, "event": event}))[1]["error"]["code"] == "SOURCE_RUN_UNAVAILABLE"
        provider.invalid = True
        status, rejected = request(server, token, envelope("rewrite", {
            "original": TEXT, "intent": "Make concise", "context": "work.email", "constraints": [],
        }))
        assert status == 422 and rejected["error"]["engine_code"] == "IDENTICAL_REPAIR"
        assert "candidates" not in rejected and store.path.read_bytes() == before
        assert len(provider.calls) == 24  # Failed run: prepare, two generations, one allowed repair.
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM examples").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM feedback").fetchone()[0] == 3
    assert token.encode() not in store.path.read_bytes()
    diagnostics = caplog.text + str(capsys.readouterr())
    assert all(value not in diagnostics for value in (TEXT, EDIT, token, "Synthetic example."))
