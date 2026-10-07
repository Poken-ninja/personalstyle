"""One local Ollama adapter; fixed deadlines, identities and no transport retries."""

import hashlib
import http.client
import json
import re
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

PREPARATION_SECONDS = 120
PORT = 11434
MAX_RESPONSE_BYTES = 1024 * 1024
MODEL_TEMPLATE_SHA256 = {
    "qwen3:30b": "2d54db2b9bb29ce7db54fea63a891f5859603813c555b1f88b5e0994652897f9",
    "qwen3:8b": "ae370d884f108d16e7cc8fd5259ebc5773a0afa6e078b11f4ed7e39a27e0dfc4",
}


class GenerationError(ValueError):
    """Fixed codes only, without provider error bodies or writing."""


@dataclass(frozen=True)
class PreparedModel:
    provider: str
    model: str
    digest: str
    runtime_version: str
    context_tokens: int
    framing_bytes: int
    preparation_seconds: float


@dataclass(frozen=True)
class Candidate:
    text: str = field(repr=False)
    seconds: float
    prompt_tokens: int
    output_tokens: int


class ModelProvider(Protocol):
    def prepare(self, context_tokens: int) -> PreparedModel: ...

    def generate(
        self, prepared: PreparedModel, messages: list[dict[str, str]], *,
        timeout_seconds: int, max_tokens: int, temperature: float,
    ) -> Candidate: ...


class OllamaProvider:
    def __init__(self, model: str):
        if (
            type(model) is not str or len(model) > 256 or model == "TODO"
            or re.fullmatch(r"[A-Za-z0-9_.:/-]+", model) is None
        ):
            raise GenerationError("MODEL_UNAVAILABLE")
        self.model = model

    @staticmethod
    def _json(path: str, deadline: float, body: dict[str, Any] | None = None) -> dict[str, Any]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise GenerationError("GENERATION_RESOURCE_LIMIT")
        connection = http.client.HTTPConnection("127.0.0.1", PORT, timeout=remaining)
        timer = None
        try:
            connection.connect()
            transport = connection.sock
            assert transport is not None

            def abort() -> None:
                try:
                    transport.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                transport.close()

            timer = threading.Timer(max(0, deadline - time.monotonic()), abort)
            timer.daemon = True
            timer.start()
            payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
            if payload is not None and len(payload) > MAX_RESPONSE_BYTES:
                raise GenerationError("INVALID_REQUEST")
            connection.request(
                "GET" if body is None else "POST", path, payload,
                {"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            if response.status != 200:
                raise GenerationError("MODEL_RUNTIME_UNAVAILABLE")
            content = response.read(MAX_RESPONSE_BYTES + 1)
            if time.monotonic() >= deadline:
                raise GenerationError("GENERATION_RESOURCE_LIMIT")
            if len(content) > MAX_RESPONSE_BYTES:
                raise GenerationError("MODEL_RESPONSE_INVALID")
            result = json.loads(content)
            if not isinstance(result, dict):
                raise GenerationError("MODEL_RESPONSE_INVALID")
            return result
        except (OSError, http.client.HTTPException):
            code = "GENERATION_RESOURCE_LIMIT" if time.monotonic() >= deadline else (
                "MODEL_RUNTIME_UNAVAILABLE"
            )
            raise GenerationError(code) from None
        except (UnicodeError, json.JSONDecodeError):
            raise GenerationError("MODEL_RESPONSE_INVALID") from None
        finally:
            if timer is not None:
                timer.cancel()
            connection.close()

    def _identity(
        self, deadline: float, digest: str | None = None, *, loaded: bool = False,
        context_tokens: int | None = None,
    ) -> str:
        inventory = self._json("/api/ps" if loaded else "/api/tags", deadline)
        models = inventory.get("models")
        if not isinstance(models, list):
            raise GenerationError("MODEL_RESPONSE_INVALID")
        matches = [m for m in models if isinstance(m, dict) and m.get("name") == self.model]
        if len(matches) != 1:
            raise GenerationError("MODEL_UNAVAILABLE")
        actual = matches[0].get("digest")
        if type(actual) is not str or re.fullmatch(r"[0-9a-f]{64}", actual) is None:
            raise GenerationError("MODEL_IDENTITY_MISMATCH")
        if digest is not None and actual != digest:
            raise GenerationError("MODEL_IDENTITY_MISMATCH")
        if loaded and matches[0].get("context_length") != context_tokens:
            raise GenerationError("MODEL_RESPONSE_INVALID")
        return actual

    def prepare(self, context_tokens: int) -> PreparedModel:
        if type(context_tokens) is not int or not 0 < context_tokens <= 8000:
            raise GenerationError("INVALID_REQUEST")
        start = time.monotonic()
        deadline = start + PREPARATION_SECONDS
        try:
            digest = self._identity(deadline)
            version = self._json("/api/version", deadline).get("version")
            show = self._json("/api/show", deadline, {"model": self.model})
            template = show.get("template")
            info, capabilities = show.get("model_info"), show.get("capabilities")
            if (
                type(version) is not str or re.fullmatch(r"\d+\.\d+\.\d+", version) is None
                or type(template) is not str
                or hashlib.sha256(template.encode()).hexdigest() != MODEL_TEMPLATE_SHA256.get(
                    self.model
                )
                or not isinstance(info, dict) or info.get("tokenizer.ggml.model") != "gpt2"
                or show.get("system", "") or show.get("remote_host") or show.get("remote_model")
                or not isinstance(capabilities, list) or "completion" not in capabilities
            ):
                raise GenerationError("MODEL_INCOMPATIBLE")
            result = self._json("/api/generate", deadline, {
                "model": self.model, "prompt": "", "stream": False, "keep_alive": "5m",
                "options": {"num_ctx": context_tokens},
            })
            if (
                result.get("model") != self.model or result.get("done") is not True
                or result.get("response", "") or result.get("thinking", "")
                or result.get("eval_count", 0) != 0
            ):
                raise GenerationError("MODEL_RESPONSE_INVALID")
            self._identity(deadline, digest)
            self._identity(deadline, digest, loaded=True, context_tokens=context_tokens)
            framing = len(re.sub(r"{{.*?}}", "", template, flags=re.DOTALL).encode("utf-8")) * 2
            if time.monotonic() >= deadline:
                raise GenerationError("GENERATION_RESOURCE_LIMIT")
            return PreparedModel(
                "ollama", self.model, digest, version, context_tokens, framing,
                time.monotonic() - start,
            )
        except GenerationError as error:
            if str(error) == "GENERATION_RESOURCE_LIMIT":
                raise GenerationError("MODEL_PREPARATION_TIMEOUT") from None
            raise

    def generate(
        self, prepared: PreparedModel, messages: list[dict[str, str]], *,
        timeout_seconds: int, max_tokens: int, temperature: float,
    ) -> Candidate:
        if (
            prepared.model != self.model or prepared.provider != "ollama"
            or type(timeout_seconds) is not int or not 0 < timeout_seconds <= 60
            or type(max_tokens) is not int or not 0 < max_tokens <= 2000
            or type(temperature) is not float or not 0 <= temperature <= 2
        ):
            raise GenerationError("INVALID_REQUEST")
        start = time.monotonic()
        deadline = start + timeout_seconds
        self._identity(deadline, prepared.digest)
        self._identity(deadline, prepared.digest, loaded=True, context_tokens=prepared.context_tokens)
        result = self._json("/api/chat", deadline, {
            "model": self.model, "messages": messages, "stream": False, "think": False,
            "keep_alive": "5m", "options": {
                "num_ctx": prepared.context_tokens, "num_predict": max_tokens,
                "temperature": temperature,
            },
        })
        message = result.get("message")
        text = message.get("content") if isinstance(message, dict) else None
        prompt_tokens, output_tokens = result.get("prompt_eval_count"), result.get("eval_count")
        if (
            result.get("model") != self.model or result.get("done") is not True
            or result.get("done_reason") != "stop" or type(text) is not str or not text.strip()
            or type(prompt_tokens) is not int or prompt_tokens <= 0
            or type(output_tokens) is not int or output_tokens <= 0
        ):
            raise GenerationError("MODEL_RESPONSE_INVALID")
        if output_tokens > max_tokens or prompt_tokens + max_tokens > prepared.context_tokens:
            raise GenerationError("GENERATION_RESOURCE_LIMIT")
        self._identity(deadline, prepared.digest)
        self._identity(deadline, prepared.digest, loaded=True, context_tokens=prepared.context_tokens)
        if time.monotonic() >= deadline:
            raise GenerationError("GENERATION_RESOURCE_LIMIT")
        return Candidate(text, time.monotonic() - start, prompt_tokens, output_tokens)
