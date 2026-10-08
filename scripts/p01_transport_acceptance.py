"""One bounded synthetic child-process/HTTP acceptance; no model calls or user profile."""

import http.client
import json
import queue
import secrets
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from threading import Thread
from time import perf_counter
from uuid import uuid4

from personalstyle.security import prepare_private_directory
from personalstyle.storage import ExampleInput, ExampleStore


def main():
    token = secrets.token_urlsafe(32)
    text = "Synthetic transport acceptance example."
    with tempfile.TemporaryDirectory(prefix="personalstyle-p01-") as temporary:
        root = Path(temporary)
        config = root / "personalstyle.toml"
        shutil.copyfile(Path(__file__).resolve().parents[1] / "personalstyle.toml", config)
        prepare_private_directory(root / "data")
        child = subprocess.Popen(
            [sys.executable, "-m", "personalstyle.protocol", "--config", str(config)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        ready_line = ""
        try:
            child.stdin.write(json.dumps({"credential": token}) + "\n")
            child.stdin.close()
            child.stdin = None
            ready_lines = queue.Queue(maxsize=1)
            reader = Thread(target=lambda: ready_lines.put(child.stdout.readline()), daemon=True)
            reader.start()
            ready_line = ready_lines.get(timeout=60)
            ready = json.loads(ready_line)
            assert ready["state"] == "READY" and ready["host"] == "127.0.0.1"
            connection = http.client.HTTPConnection(ready["host"], ready["port"], timeout=60)

            def call(capability, payload):
                wire = {"protocol_version": "1.0", "client_version": "0.1.0",
                        "client_kind": "cli", "requested_capability": capability, "payload": payload}
                connection.request("POST", "/v1", json.dumps(wire),
                                   {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
                response = connection.getresponse()
                result = json.loads(response.read())
                assert response.status == 200 and result["ok"]
                return result["result"]

            started = perf_counter()
            assert call("handshake", {})["compatibility"] == "compatible"
            handshake_seconds = perf_counter() - started
            example = ExampleInput(str(uuid4()), text, "work.email", "owner", "owner",
                                   "user_owned", True, True, False)
            started = perf_counter()
            saved = call("example.write", asdict(example))
            write_seconds = perf_counter() - started
            assert call("example.write", asdict(example)) == saved
            connection.close()
            store = ExampleStore(root / "data" / "personalstyle.db")
            assert store.get(example.id)["text"] == text
            assert token.encode() not in store.path.read_bytes()
        finally:
            child.terminate()  # Only the child launched by this acceptance run.
            stdout, stderr = child.communicate(timeout=10)
            assert all(value not in ready_line + stdout + stderr for value in (token, text))
        print(json.dumps({"state": "PASSED", "protocol": "1.0", "host": "127.0.0.1",
                          "workflow": "handshake + idempotent example.write + read-back",
                          "handshake_seconds": round(handshake_seconds, 4),
                          "write_seconds": round(write_seconds, 4),
                          "process_stopped": child.poll() is not None}))


if __name__ == "__main__":
    main()
