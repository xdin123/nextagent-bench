"""Private Docker-side OpenAI-compatible gateway; standard library only.

Credentials share ONE admission budget. Only explicit pre-response 429/401/403
responses may be retried. No prompts, completions or credentials are logged.
"""
from __future__ import annotations

import hmac
import json
import hashlib
import os
import threading
import time
import urllib.error
import urllib.request
import uuid
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from collections import Counter, deque
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


@dataclass
class Credential:
    name: str
    secret: str = field(repr=False)
    active: int = 0
    disabled: bool = False
    requests: int = 0


class SharedBudget:
    def __init__(self, credentials: list[Credential], quota: dict):
        if not credentials:
            raise ValueError("No model credentials configured")
        self.credentials, self.quota = credentials, quota
        self.condition = threading.Condition()
        self.active, self.cursor = 0, 0
        self.cooldown_until = self.next_start = 0.0
        self.window = deque()
        self.statuses = Counter()

    def acquire(self, estimated_tokens: int, deadline: float) -> Credential:
        with self.condition:
            while True:
                now = time.monotonic()
                if now >= deadline:
                    raise TimeoutError("Shared model quota admission deadline exceeded")
                while self.window and self.window[0][0] <= now - 60:
                    self.window.popleft()
                available = [key for key in self.credentials if not key.disabled]
                if not available:
                    raise PermissionError("All registered credentials were rejected")
                rpm, tpm = self.quota.get("requests_per_minute"), self.quota.get("tokens_per_minute")
                reservation = min(estimated_tokens, tpm) if tpm else estimated_tokens
                wait_until = max(self.cooldown_until, self.next_start)
                if rpm and len(self.window) >= rpm:
                    wait_until = max(wait_until, self.window[0][0] + 60)
                if tpm and sum(item[1] for item in self.window) + reservation > tpm and self.window:
                    wait_until = max(wait_until, self.window[0][0] + 60)
                if self.active < self.quota["max_concurrency"] and now >= wait_until:
                    minimum = min(key.active for key in available)
                    choices = [key for key in available if key.active == minimum]
                    key = choices[self.cursor % len(choices)]
                    self.cursor += 1
                    self.active += 1
                    key.active += 1
                    key.requests += 1
                    self.window.append((now, reservation))
                    self.next_start = now + self.quota.get("min_interval_seconds", 2)
                    return key
                remaining = deadline - now
                if remaining <= 0:
                    raise TimeoutError("Shared model quota admission deadline exceeded")
                self.condition.wait(min(remaining, max(0.01, wait_until - now) if wait_until > now else 0.5))

    def release(self, credential: Credential, status: int, *, cooldown: float = 0, disable: bool = False):
        with self.condition:
            self.active -= 1
            credential.active -= 1
            credential.disabled = credential.disabled or disable
            self.statuses[status] += 1
            if cooldown:
                self.cooldown_until = max(self.cooldown_until, time.monotonic() + cooldown)
            self.condition.notify_all()

    def snapshot(self) -> dict:
        with self.condition:
            return {"quota": self.quota, "active": self.active, "cooldown_remaining_seconds": max(0, self.cooldown_until - time.monotonic()),
                    "statuses": dict(self.statuses), "credentials": [{"name": key.name, "requests": key.requests,
                    "disabled": key.disabled, "active": key.active} for key in self.credentials]}


def retry_after(value: str | None, fallback: float) -> float:
    if value:
        try:
            return max(0, float(value))
        except ValueError:
            try:
                return max(0, parsedate_to_datetime(value).timestamp() - time.time())
            except (ValueError, TypeError, OverflowError):
                pass
    return fallback


def estimate_tokens(body: bytes) -> int:
    # Admission reservation only, never reported as measured model usage.
    output = 0
    try:
        value = json.loads(body)
        output = max(0, int(value.get("max_tokens") or value.get("max_completion_tokens") or 0))
    except (ValueError, TypeError, AttributeError):
        pass
    return max(1, (len(body) + 2) // 3 + output)


class ExchangeCapture:
    """Evaluation artifact, separate from operational logs. No auth headers/CoT."""
    def __init__(self, root: Path, request_id: str, context: dict, body: bytes, credentials):
        self.directory = root / context["task"] / ("attempt-" + str(context["attempt"])) / request_id
        self.directory.mkdir(parents=True, exist_ok=True)
        self.credentials, self.written = credentials, 0
        self.metadata = {"request_id": request_id, "context": context, "started_at": time.time(), "completed": False,
                         "completion_semantics": "transport forwarding only; provider finish/DONE signals must be inspected separately",
                         "request_sha256": hashlib.sha256(body).hexdigest(), "sanitizations": ["actual API keys redacted", "provider reasoning omitted"],
                         "capture_truncated": False, "responses": []}
        self.save("request.json", json.loads(self.redact(body.decode("utf-8"))))
        self.save("metadata.json", self.metadata)

    def redact(self, text):
        for credential in self.credentials:
            text = text.replace(credential.secret, "<redacted>")
        return text

    def save(self, name, data):
        (self.directory / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def record(self, attempt: int, line: bytes):
        if self.written >= 8 * 1024 * 1024:
            self.metadata["capture_truncated"] = True
            return
        text = self.redact(line.decode("utf-8", errors="replace").strip())
        if text.startswith("data:"):
            text = text[5:].strip()
            if text == "[DONE]":
                value = {"event": "done"}
            else:
                try:
                    value = json.loads(text)
                    for choice in value.get("choices", []):
                        for field in ("delta", "message"):
                            if isinstance(choice.get(field), dict):
                                choice[field].pop("reasoning_content", None)
                                choice[field].pop("reasoning", None)
                except (ValueError, AttributeError):
                    value = {"event": "unparseable_chunk", "bytes": len(line), "sha256": hashlib.sha256(line).hexdigest()}
        elif not text:
            return
        else:
            # Non-SSE JSON responses are recorded separately by the caller.
            return
        value = {"observed_at": time.time(), "payload": value}
        encoded = json.dumps(value, ensure_ascii=False) + "\n"
        with (self.directory / f"response-{attempt:02d}.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(encoded)
        self.written += len(encoded.encode("utf-8"))

    def finish_attempt(self, attempt, status, credential, response_started, error_kind, nonstream=None, completed=False):
        if nonstream:
            try:
                value = json.loads(self.redact(nonstream.decode("utf-8", errors="replace")))
                for choice in value.get("choices", []):
                    if isinstance(choice.get("message"), dict):
                        choice["message"].pop("reasoning_content", None)
                        choice["message"].pop("reasoning", None)
                self.save(f"response-{attempt:02d}.json", value)
            except (ValueError, AttributeError):
                pass
        self.metadata["responses"].append({"attempt": attempt, "status": status, "credential": credential,
                                          "response_started": response_started, "error_kind": error_kind})
        self.metadata["completed"] = completed
        self.metadata["finished_at"] = time.time()
        self.save("metadata.json", self.metadata)


def make_handler(pool: SharedBudget, upstream: str, token: str, *, emit=print, evidence_root: Path | None = None):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args):
            pass

        def respond(self, status: int, body: bytes, content_type="application/json", headers=None):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.close_connection = True
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def error_json(self, status, code):
            self.respond(status, json.dumps({"error": {"message": code, "type": "evaluation_gateway", "code": code}}).encode())

        def do_GET(self):
            if self.path == "/health":
                self.respond(200, b'{"ok":true}')
            elif self.path == "/metrics" and self.authorized():
                self.respond(200, json.dumps(pool.snapshot()).encode())
            else:
                self.forward()

        def do_POST(self):
            self.forward()

        def authorized(self):
            return hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + token)

        def forward(self):
            if not self.authorized():
                self.error_json(401, "EVAL_GATEWAY_UNAUTHORIZED")
                return
            relative = self.path[3:] if self.path.startswith("/v1/") else None
            context = {"task": "unscoped", "attempt": 0, "purpose": "evaluation"}
            match = re.match(r'^/(tasks|analysis)/([^/]+)/attempts/(\d+)/v1(/.*)$', self.path)
            if match:
                task = unquote(match[2])
                if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', task):
                    self.error_json(400, "EVAL_TASK_CONTEXT_INVALID")
                    return
                context = {"task": task, "attempt": int(match[3]), "purpose": "evaluation" if match[1] == "tasks" else "analysis"}
                relative = match[4]
            if relative is None:
                self.error_json(404, "EVAL_GATEWAY_PATH_NOT_FOUND")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 <= length <= 32 * 1024 * 1024:
                    raise ValueError()
            except ValueError:
                self.error_json(413, "EVAL_REQUEST_SIZE_INVALID")
                return
            body = self.rfile.read(length)
            request_id = uuid.uuid4().hex
            capture = None
            if evidence_root is not None and context["purpose"] == "evaluation" and self.command == "POST":
                try:
                    capture = ExchangeCapture(evidence_root, request_id, context, body, pool.credentials)
                except (OSError, ValueError):
                    emit(json.dumps({"event": "model.evidence.capture_failed", "request": request_id, "context": context}))
            deadline = time.monotonic() + pool.quota.get("max_wait_seconds", 90)
            attempts = pool.quota.get("max_attempts", 3)
            for attempt in range(1, attempts + 1):
                try:
                    key = pool.acquire(estimate_tokens(body), deadline)
                except (TimeoutError, PermissionError) as error:
                    code = "EVAL_QUOTA_WAIT_TIMEOUT" if isinstance(error, TimeoutError) else "EVAL_CREDENTIALS_REJECTED"
                    self.error_json(429 if isinstance(error, TimeoutError) else 401, code)
                    emit(json.dumps({"event": code, "request": request_id}))
                    if capture:
                        capture.metadata.update({"completed": True, "terminal_gateway_error": code})
                        capture.save("metadata.json", capture.metadata)
                    return
                start = time.monotonic()
                response_started = False
                status, cooldown, disabled = 502, 0, False
                error_kind = None
                operation = "UPSTREAM"
                nonstream = bytearray()
                logical_done = False
                try:
                    request = urllib.request.Request(upstream.rstrip("/") + relative, data=body if self.command == "POST" else None,
                        method=self.command, headers={"Authorization": "Bearer " + key.secret,
                        "Content-Type": self.headers.get("Content-Type", "application/json"), "Accept-Encoding": "identity"})
                    try:
                        response = urllib.request.urlopen(request, timeout=pool.quota.get("upstream_idle_timeout_seconds", 120))
                    except urllib.error.HTTPError as error:
                        status = error.code
                        raw = error.read()
                        nonstream.extend(raw[:8 * 1024 * 1024])
                        if status == 429:
                            cooldown = retry_after(error.headers.get("Retry-After"), min(60, 10 * 2 ** (attempt - 1)))
                        disabled = status in (401, 403)
                        if (status == 429 or disabled) and attempt < attempts and time.monotonic() + cooldown < deadline:
                            continue
                        for credential in pool.credentials:
                            raw = raw.replace(credential.secret.encode(), b"<redacted>")
                        extra = {"Retry-After": str(max(1, int(cooldown)))} if cooldown else {}
                        logical_done = True
                        operation = "CLIENT"
                        self.respond(status, raw, error.headers.get("Content-Type", "application/json"), extra)
                        return
                    with response:
                        status = response.status
                        # Headers/body are sent once. Never retry a stream or a
                        # transport failure after the provider accepted a call.
                        operation = "CLIENT"
                        self.send_response(status)
                        self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                        self.send_header("Connection", "close")
                        self.end_headers()
                        response_started = True
                        self.close_connection = True
                        while True:
                            operation = "UPSTREAM"
                            line = response.readline()
                            if not line:
                                break
                            if capture:
                                try:
                                    if "event-stream" in response.headers.get("Content-Type", ""):
                                        capture.record(attempt, line)
                                    elif len(nonstream) < 8 * 1024 * 1024:
                                        nonstream.extend(line)
                                except OSError:
                                    emit(json.dumps({"event": "model.evidence.capture_failed", "request": request_id, "context": context}))
                                    capture = None
                            operation = "CLIENT"
                            self.wfile.write(line)
                            self.wfile.flush()
                    logical_done = True
                    return
                except (BrokenPipeError, ConnectionResetError):
                    error_kind = "UPSTREAM_CONNECTION_RESET" if operation == "UPSTREAM" else "CLIENT_DISCONNECTED"
                    self.close_connection = True
                    if not response_started and operation == "UPSTREAM":
                        try:
                            self.error_json(502, "EVAL_UPSTREAM_CONNECTION_RESET")
                        except OSError:
                            pass
                    return
                except Exception:
                    error_kind = "UPSTREAM_TRANSPORT_ERROR" if operation == "UPSTREAM" else "CLIENT_TRANSPORT_ERROR"
                    self.close_connection = True
                    if not response_started and operation == "UPSTREAM":
                        try:
                            self.error_json(502, "EVAL_UPSTREAM_TRANSPORT_ERROR")
                        except OSError:
                            pass
                    return
                finally:
                    pool.release(key, status, cooldown=cooldown, disable=disabled)
                    if capture:
                        try:
                            capture.finish_attempt(attempt, status, key.name, response_started, error_kind, bytes(nonstream), logical_done)
                        except OSError:
                            emit(json.dumps({"event": "model.evidence.capture_failed", "request": request_id, "context": context}))
                    emit(json.dumps({"event": "model.proxy.attempt", "request": request_id, "attempt": attempt, "credential": key.name,
                                     "status": status, "duration_seconds": round(time.monotonic() - start, 3),
                                     "group_cooldown_seconds": cooldown, "credential_disabled": disabled,
                                     "response_started": response_started, "error_kind": error_kind, "context": context}))
    return Handler


def main():
    keys = [Credential(item["name"], item["key"]) for item in json.loads(os.environ["NAB_API_KEYS"])]
    config = json.loads(os.environ["NAB_PROXY_CONFIG"])
    pool = SharedBudget(keys, config["quota"])
    evidence = Path('/evidence') if config.get('capture_model_exchanges', True) else None
    if evidence:
        evidence.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", 8787), make_handler(pool, config["upstream"], os.environ["NAB_PROXY_TOKEN"], evidence_root=evidence))
    server.daemon_threads = True
    print(json.dumps({"event": "model.proxy.ready", "credentials": [key.name for key in keys], "quota_shared": True}), flush=True)
    server.serve_forever()


def client():
    value = json.load(sys.stdin)
    request = urllib.request.Request('http://127.0.0.1:8787' + value['path'], data=json.dumps(value['body']).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['NAB_PROXY_TOKEN'], 'Content-Type': 'application/json'})
    deadline = time.monotonic() + value.get('timeout', 240)
    content, usage, reason = [], None, None
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            for line in response:
                if time.monotonic() > deadline:
                    print(json.dumps({'error': 'ANALYSIS_TIMEOUT', 'content': ''.join(content), 'usage': usage, 'finish_reason': reason}))
                    return
                text = line.decode('utf-8', errors='replace').strip()
                if not text.startswith('data:') or text[5:].strip() == '[DONE]':
                    continue
                chunk = json.loads(text[5:])
                usage = chunk.get('usage') or usage
                for choice in chunk.get('choices', []):
                    delta = choice.get('delta') or choice.get('message') or {}
                    if isinstance(delta.get('content'), str):
                        content.append(delta['content'])
                    reason = choice.get('finish_reason') or reason
        print(json.dumps({'content': ''.join(content), 'usage': usage, 'finish_reason': reason}))
    except urllib.error.HTTPError as error:
        print(json.dumps({'error': 'HTTP_' + str(error.code)}))
    except (TimeoutError, OSError, ValueError):
        print(json.dumps({'error': 'ANALYSIS_TRANSPORT_OR_PROTOCOL_ERROR', 'content': ''.join(content), 'usage': usage, 'finish_reason': reason}))


if __name__ == "__main__":
    client() if len(sys.argv) > 1 and sys.argv[1] == 'client' else main()
