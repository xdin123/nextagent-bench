from __future__ import annotations

import hashlib
import contextlib
import json
import os
import re
import signal
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_document(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a mapping: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tree_manifest(root: Path, exclude: tuple[str, ...] = ()) -> dict[str, str]:
    output = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in {"__pycache__", ".git", ".venv"} for part in relative.parts):
            continue
        if relative.parts[0] in exclude or not path.is_file():
            continue
        output[relative.as_posix()] = file_sha(path)
    return output


def sanitize(text: str) -> str:
    text = re.sub(r"sk-[A-Za-z0-9_.-]{8,}", "<redacted>", text)
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        value = os.environ.get(name)
        if value:
            text = text.replace(value, "<redacted>")
    try:
        for credential in json.loads(os.environ.get("NAB_API_KEYS", "[]")):
            if credential.get("key"):
                text = text.replace(credential["key"], "<redacted>")
    except (ValueError, TypeError, AttributeError):
        pass
    return text


class CommandError(RuntimeError):
    pass


def _stop_process_tree(process: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       capture_output=True, timeout=10, check=False,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait(timeout=10)


def archive_from_container(container: str, source: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".partial.tar")
    with temporary.open("wb") as stream:
        process = subprocess.Popen(["docker", "cp", container + ":" + source, "-"], stdout=stream, stderr=subprocess.PIPE,
                                   start_new_session=os.name != "nt")
        try:
            _, errors = process.communicate(timeout=600)
        except BaseException:
            _stop_process_tree(process)
            raise
    if process.returncode:
        raise CommandError(sanitize("Archive export failed: " + errors.decode("utf-8", errors="replace")[-800:]))
    temporary.replace(destination)


def command(args: list[str], *, timeout: float = 120, input_text: str | None = None,
            log: Path | None = None, check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.ExitStack() as stack:
        stream = stack.enter_context(log.open("w", encoding="utf-8")) if log else subprocess.PIPE
        process = subprocess.Popen(args, stdin=subprocess.PIPE if input_text is not None else None,
                                   stdout=stream, stderr=subprocess.STDOUT if log else subprocess.PIPE,
                                   text=True, encoding="utf-8", errors="replace", env=env,
                                   start_new_session=os.name != "nt")
        try:
            output, errors = process.communicate(input_text, timeout=timeout)
        except BaseException:
            _stop_process_tree(process)
            process.communicate(timeout=10)
            raise
    if log:
        errors = log.read_text(encoding="utf-8", errors="replace")[-3000:] if process.returncode else ""
    result = subprocess.CompletedProcess(args, process.returncode, output or "", sanitize(errors or ""))
    if check and result.returncode:
        raise CommandError(sanitize(f"{args[0]} exited {result.returncode}: {(result.stderr or result.stdout)[-3000:]}"))
    return result


def adapter_sha(root: Path | None = None) -> str:
    root = root or Path(__file__).parent
    files = tree_manifest(root)
    return digest({key: value for key, value in files.items() if key.endswith((".py", ".mjs"))})
