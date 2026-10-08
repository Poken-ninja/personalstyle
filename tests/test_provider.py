"""Deterministic provider failures plus real loopback transport deadline checks."""

import hashlib
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from personalstyle import provider
from personalstyle.provider import GenerationError, OllamaProvider

DIGEST = "a" * 64


@pytest.fixture(params=["qwen3:30b", "qwen3:8b"])
def adapter(request, monkeypatch):
    calls = []
    model = request.param
    value = OllamaProvider(model)

    def response(path, deadline, body=None):
        assert 0 < deadline - time.monotonic() <= 120
        calls.append((path, body))
        if path in ("/api/tags", "/api/ps"):
            return {"models": [{"name": value.model, "digest": DIGEST, "context_length": 8000}]}
        if path == "/api/version":
            return {"version": "0.40.0"}
        if path == "/api/show":
            return {"template": TEMPLATES[model], "model_info": {"tokenizer.ggml.model": "gpt2"},
                    "capabilities": ["completion", "thinking"]}
        if path == "/api/generate":
            assert body["prompt"] == "" and "messages" not in body
            return {"model": value.model, "done": True, "response": ""}
        if path == "/api/chat":
            return {"model": value.model, "done": True, "done_reason": "stop",
                    "message": {"content": "PRIVATE_CANDIDATE"},
                    "prompt_eval_count": 20, "eval_count": 10}
        pytest.fail("unexpected provider operation")

    monkeypatch.setattr(value, "_json", response)
    return value, calls, response


def test_empty_preparation_identity_and_no_hidden_retry(adapter, caplog):
    value, calls, _ = adapter
    assert provider.PREPARATION_SECONDS == 120
    assert hashlib.sha256(TEMPLATES[value.model].encode()).hexdigest() == (
        provider.MODEL_TEMPLATE_SHA256[value.model]
    )
    prepared = value.prepare(8000)
    assert prepared.digest == DIGEST
    assert prepared.framing_bytes == {"qwen3:30b": 1360, "qwen3:8b": 1472}[value.model]
    frame = (
        "<|im_start|>system\n<|im_end|>\n<|im_start|>user\n /no_think<|im_end|>\n"
        "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    )
    assert len(frame.encode()) < prepared.framing_bytes
    candidate = value.generate(prepared, [{"role": "user", "content": "PRIVATE_PROMPT"}],
                               timeout_seconds=60, max_tokens=2000, temperature=0.2)
    assert candidate.text == "PRIVATE_CANDIDATE"
    assert [path for path, _ in calls].count("/api/generate") == 1
    assert [path for path, _ in calls].count("/api/chat") == 1
    assert "PRIVATE" not in caplog.text + repr(candidate)


@pytest.mark.parametrize("damage,code", [
    ("digest", "MODEL_IDENTITY_MISMATCH"), ("absent", "MODEL_UNAVAILABLE"),
    ("template", "MODEL_INCOMPATIBLE"), ("tokenizer", "MODEL_INCOMPATIBLE"),
    ("cloud", "MODEL_INCOMPATIBLE"), ("timeout", "MODEL_PREPARATION_TIMEOUT"),
    ("remote_model", "MODEL_INCOMPATIBLE"), ("capabilities", "MODEL_INCOMPATIBLE"),
    ("system", "MODEL_INCOMPATIBLE"), ("cross_template", "MODEL_INCOMPATIBLE"),
    ("load_response", "MODEL_RESPONSE_INVALID"),
    ("context", "MODEL_RESPONSE_INVALID"),
])
def test_preparation_failures_never_generate(adapter, monkeypatch, damage, code, caplog):
    value, calls, original = adapter

    def damaged(path, deadline, body=None):
        result = original(path, deadline, body)
        if path == "/api/ps" and damage == "digest":
            result["models"][0]["digest"] = "b" * 64
        if path == "/api/ps" and damage == "context":
            result["models"][0]["context_length"] = 4096
        if path == "/api/tags" and damage == "absent":
            result["models"] = []
        if path == "/api/show":
            if damage == "template":
                result["template"] += "PRIVATE_TEMPLATE"
            if damage == "tokenizer":
                result["model_info"] = {"tokenizer.ggml.model": "unknown"}
            if damage == "cloud":
                result["remote_host"] = "https://cloud.invalid"
            if damage == "remote_model":
                result["remote_model"] = "cloud-model"
            if damage == "capabilities":
                result["capabilities"] = ["thinking"]
            if damage == "system":
                result["system"] = "PRIVATE_SYSTEM_OVERRIDE"
            if damage == "cross_template":
                other = "qwen3:8b" if value.model == "qwen3:30b" else "qwen3:30b"
                result["template"] = TEMPLATES[other]
        if path == "/api/generate":
            if damage == "timeout":
                raise GenerationError("GENERATION_RESOURCE_LIMIT")
            if damage == "load_response":
                result["response"] = "PRIVATE_PROVIDER_ERROR"
        return result

    monkeypatch.setattr(value, "_json", damaged)
    with pytest.raises(GenerationError, match=f"^{code}$"):
        value.prepare(8000)
    assert not any(path == "/api/chat" for path, _ in calls)
    assert sum(path == "/api/generate" for path, _ in calls) <= 1
    assert "PRIVATE" not in caplog.text


def test_unknown_model_with_known_template_rejected_before_load(adapter):
    value, calls, _ = adapter
    value.model = "qwen3:14b"
    with pytest.raises(GenerationError, match="^MODEL_INCOMPATIBLE$"):
        value.prepare(8000)
    assert not any(path in ("/api/generate", "/api/chat") for path, _ in calls)


@pytest.mark.parametrize("damage,code", [
    ("identity", "MODEL_IDENTITY_MISMATCH"), ("unloaded", "MODEL_UNAVAILABLE"),
    ("wrong_model", "MODEL_RESPONSE_INVALID"), ("partial", "MODEL_RESPONSE_INVALID"),
    ("too_many_tokens", "GENERATION_RESOURCE_LIMIT"), ("malformed", "MODEL_RESPONSE_INVALID"),
])
def test_generation_rejects_invalid_or_changed_result(adapter, monkeypatch, damage, code):
    value, calls, original = adapter
    prepared = value.prepare(8000)
    calls.clear()

    def damaged(path, deadline, body=None):
        result = original(path, deadline, body)
        if path == "/api/tags" and damage == "identity":
            result["models"][0]["digest"] = "b" * 64
        if path == "/api/ps" and damage == "unloaded":
            result["models"] = []
        if path == "/api/chat":
            if damage == "wrong_model":
                result["model"] = "qwen3:8b" if value.model == "qwen3:30b" else "qwen3:30b"
            if damage == "partial":
                result["done_reason"] = "length"
            if damage == "too_many_tokens":
                result["eval_count"] = 2001
            if damage == "malformed":
                result["message"] = ["PRIVATE_ERROR"]
        return result

    monkeypatch.setattr(value, "_json", damaged)
    with pytest.raises(GenerationError, match=f"^{code}$"):
        value.generate(prepared, [], timeout_seconds=60, max_tokens=2000, temperature=0.2)
    assert sum(path == "/api/chat" for path, _ in calls) <= 1


@pytest.mark.parametrize("scenario,code", [
    ("drip", "GENERATION_RESOURCE_LIMIT"), ("error", "MODEL_RUNTIME_UNAVAILABLE"),
    ("oversized", "MODEL_RESPONSE_INVALID"),
])
def test_real_transport_deadline_error_and_response_bounds(monkeypatch, caplog, scenario, code):
    hits = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            hits.append(self.path)
            self.send_response(500 if scenario == "error" else 200)
            self.end_headers()
            try:
                if scenario == "drip":
                    for _ in range(50):
                        self.wfile.write(b" ")
                        self.wfile.flush()
                        time.sleep(0.02)
                else:
                    self.wfile.write(b"PRIVATE_PROVIDER_ERROR" * 100)
            except OSError:
                pass

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    monkeypatch.setattr(provider, "PORT", server.server_port)
    monkeypatch.setattr(provider, "MAX_RESPONSE_BYTES", 128)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    start = time.monotonic()
    try:
        with pytest.raises(GenerationError, match=f"^{code}$"):
            OllamaProvider._json("/test", start + (0.12 if scenario == "drip" else 2))
        assert time.monotonic() - start < 0.8
        assert hits == ["/test"]
        assert "PRIVATE" not in caplog.text
    finally:
        server.shutdown()
        server.server_close()

# Observed Qwen3 templates, frozen against their exact model compatibility hashes.
TEMPLATE_8B = "\n{{- $lastUserIdx := -1 -}}\n{{- range $idx, $msg := .Messages -}}\n{{- if eq $msg.Role \"user\" }}{{ $lastUserIdx = $idx }}{{ end -}}\n{{- end }}\n{{- if or .System .Tools }}<|im_start|>system\n{{ if .System }}\n{{ .System }}\n{{- end }}\n{{- if .Tools }}\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>\n{{- range .Tools }}\n{\"type\": \"function\", \"function\": {{ .Function }}}\n{{- end }}\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call>\n{{- end -}}\n<|im_end|>\n{{ end }}\n{{- range $i, $_ := .Messages }}\n{{- $last := eq (len (slice $.Messages $i)) 1 -}}\n{{- if eq .Role \"user\" }}<|im_start|>user\n{{ .Content }}\n{{- if and $.IsThinkSet (eq $i $lastUserIdx) }}\n   {{- if $.Think -}}\n      {{- \" \"}}/think\n   {{- else -}}\n      {{- \" \"}}/no_think\n   {{- end -}}\n{{- end }}<|im_end|>\n{{ else if eq .Role \"assistant\" }}<|im_start|>assistant\n{{ if (and $.IsThinkSet (and .Thinking (or $last (gt $i $lastUserIdx)))) -}}\n<think>{{ .Thinking }}</think>\n{{ end -}}\n{{ if .Content }}{{ .Content }}\n{{- else if .ToolCalls }}<tool_call>\n{{ range .ToolCalls }}{\"name\": \"{{ .Function.Name }}\", \"arguments\": {{ .Function.Arguments }}}\n{{ end }}</tool_call>\n{{- end }}{{ if not $last }}<|im_end|>\n{{ end }}\n{{- else if eq .Role \"tool\" }}<|im_start|>user\n<tool_response>\n{{ .Content }}\n</tool_response><|im_end|>\n{{ end }}\n{{- if and (ne .Role \"assistant\") $last }}<|im_start|>assistant\n{{ if and $.IsThinkSet (not $.Think) -}}\n<think>\n\n</think>\n\n{{ end -}}\n{{ end }}\n{{- end }}"
TEMPLATE = '{{- $lastUserIdx := -1 -}}\n{{- range $idx, $msg := .Messages -}}\n{{- if eq $msg.Role "user" }}{{ $lastUserIdx = $idx }}{{ end -}}\n{{- end }}\n{{- if or .System .Tools }}<|im_start|>system\n{{ if .System }}{{ .System }}\n\n{{ end }}\n{{- if .Tools }}# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>\n{{- range .Tools }}\n{"type": "function", "function": {{ .Function }}}\n{{- end }}\n</tools>\n\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{"name": <function-name>, "arguments": <args-json-object>}\n</tool_call>\n{{- end -}}\n<|im_end|>\n{{ end }}\n{{- range $i, $_ := .Messages }}\n{{- $last := eq (len (slice $.Messages $i)) 1 -}}\n{{- if eq .Role "user" }}<|im_start|>user\n{{ .Content }}<|im_end|>\n{{ else if eq .Role "assistant" }}<|im_start|>assistant\n{{ if (and $.IsThinkSet (and .Thinking (or $last (gt $i $lastUserIdx)))) -}}\n<think>{{ .Thinking }}</think>\n{{ end -}}\n{{ if .Content }}{{ .Content }}{{ end }}\n{{- if .ToolCalls }}\n{{- range .ToolCalls }}\n<tool_call>\n{"name": "{{ .Function.Name }}", "arguments": {{ .Function.Arguments }}}\n</tool_call>\n{{- end }}\n{{- end }}{{ if not $last }}<|im_end|>\n{{ end }}\n{{- else if eq .Role "tool" }}<|im_start|>user\n<tool_response>\n{{ .Content }}\n</tool_response><|im_end|>\n{{ end }}\n{{- if and (ne .Role "assistant") $last }}<|im_start|>assistant\n<think>\n{{ end }}\n{{- end }}'

TEMPLATES = {"qwen3:30b": TEMPLATE, "qwen3:8b": TEMPLATE_8B}


def test_long_document_deadline_is_explicit_without_changing_short_text(adapter):
    value, calls, _ = adapter
    prepared = value.prepare(8000)
    messages = [{"role": "user", "content": "PRIVATE_SYNTHETIC"}]
    with pytest.raises(GenerationError, match="^INVALID_REQUEST$"):
        value.generate(prepared, messages, timeout_seconds=61, max_tokens=2000, temperature=0.2)
    with pytest.raises(GenerationError, match="^INVALID_REQUEST$"):
        value.generate_document(prepared, messages, timeout_seconds=121, max_tokens=2000, temperature=0.2)
    calls.clear()
    assert value.generate_document(prepared, messages, timeout_seconds=120,
                                   max_tokens=2000, temperature=0.2).text == "PRIVATE_CANDIDATE"
    assert [path for path, _ in calls].count("/api/chat") == 1
    assert [path for path, _ in calls].count("/api/tags") == 2
    assert [path for path, _ in calls].count("/api/ps") == 2


def test_structured_format_is_document_only_and_one_call(adapter):
    value, calls, _ = adapter
    prepared = value.prepare(8000)
    messages = [{"role": "user", "content": "PRIVATE_SYNTHETIC"}]
    schema = {"type": "object", "properties": {"units": {"type": "array"}}}
    calls.clear()
    value.generate_document(prepared, messages, timeout_seconds=120, max_tokens=2000,
                            temperature=0.2, response_schema=schema)
    bodies = [body for path, body in calls if path == "/api/chat"]
    assert len(bodies) == 1 and bodies[0]["format"] == schema
    calls.clear()
    value.generate(prepared, messages, timeout_seconds=60, max_tokens=2000, temperature=0.2)
    bodies = [body for path, body in calls if path == "/api/chat"]
    assert len(bodies) == 1 and "format" not in bodies[0]
