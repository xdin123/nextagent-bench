"""Standalone entry point. Bootstrap and packaging use only Python's standard library."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def environment() -> dict[str, str]:
    value = dict(os.environ)
    value.setdefault("PYTHONUTF8", "1")
    return value


def setup(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python bench.py setup", description="Install dependencies and import local evaluation inputs.")
    parser.add_argument("--framework", help="Linux x64 release tar.gz, deployment directory, or imported framework directory")
    parser.add_argument("--dataset", help="Optional replacement for the bundled/default SkillsBench dataset")
    parser.add_argument("--skip-import", action="store_true", help="Install the code without importing inputs")
    parser.add_argument("--skip-tests", action="store_true", help="Skip the offline contract tests during installation")
    args = parser.parse_args(arguments)
    if not PYTHON.is_file():
        venv.EnvBuilder(with_pip=True).create(ROOT / ".venv")
    env = environment()
    for name in ("OPENAI_API_KEY", "NAB_API_KEYS"):
        env.pop(name, None)
    subprocess.run([str(PYTHON), "-m", "pip", "install", "--disable-pip-version-check", "-e", str(ROOT)],
                   cwd=ROOT, env=env, check=True)
    if not args.skip_tests:
        subprocess.run([str(PYTHON), "-m", "unittest", "discover", "-s", "tests"], cwd=ROOT, env=env, check=True)
    if not args.skip_import:
        command = [str(PYTHON), "-m", "nextagent_bench", "prepare", "--pin-defaults"]
        if args.framework:
            command += ["--framework", str(Path(args.framework).expanduser().resolve())]
        if args.dataset:
            command += ["--dataset", str(Path(args.dataset).expanduser().resolve())]
        subprocess.run(command, cwd=ROOT, env=env, check=True)
    print("Setup complete. Configure your model credential, then run: python bench.py doctor")
    return 0


def frozen_dataset() -> tuple[str, list[tuple[Path, str]]]:
    content = (ROOT / "evaluation.yaml").read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)^dataset:[ \t]*['\"]?(datasets/[a-f0-9]{64})['\"]?[ \t]*$", content)
    if not match:
        raise ValueError("First prepare and pin a local frozen dataset before bundling it")
    relative = match[1]
    dataset = ROOT / relative
    if os.name == "nt":
        absolute = str(dataset.resolve())
        dataset = Path(absolute if absolute.startswith("\\\\?\\") else
                       ("\\\\?\\UNC\\" + absolute[2:] if absolute.startswith("\\\\") else "\\\\?\\" + absolute))
    manifest = json.loads((dataset / "manifest.json").read_text(encoding="utf-8-sig"))
    files = json.loads((dataset / "files.json").read_text(encoding="utf-8-sig"))
    identity = hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if identity != manifest["sha256"] or relative != "datasets/" + identity:
        raise ValueError("Frozen dataset manifest changed; import and pin it again")
    entries = []
    for name, expected in sorted(files.items()):
        path = dataset / "tasks" / name
        if not path.resolve().is_relative_to((dataset / "tasks").resolve()) or path.is_symlink():
            raise ValueError("Refusing a dataset file outside the frozen tasks")
        with path.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
                raise ValueError("Frozen dataset file changed: " + name)
        entries.append((path, relative + "/tasks/" + name))
    for name in ("manifest.json", "files.json", "README.md", "LICENSE", "registry.json", "AGENTS.md"):
        if (dataset / name).is_file():
            entries.append((dataset / name, relative + "/" + name))
    return relative, entries


def bundle(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python bench.py bundle", description="Create a handoff ZIP without credentials or execution data.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--with-dataset", action="store_true", help="Include the pinned SkillsBench dataset so the receiver only supplies a framework archive")
    args = parser.parse_args(arguments)
    output = (args.output or ROOT / "dist" / ("nextagent-bench-ready.zip" if args.with_dataset else "nextagent-bench-portable.zip")).expanduser().resolve()
    candidates = [ROOT / name for name in ("bench.py", "pyproject.toml", "README.md", ".gitignore", "evaluation.yaml", "credentials.example.json")]
    candidates += list(ROOT.glob("*.ps1"))
    for directory in ("nextagent_bench", "scripts", "profiles", "tests"):
        candidates += [p for p in (ROOT / directory).rglob("*") if p.is_file() and
                       p.suffix in {".py", ".mjs", ".ps1", ".yaml"} and "__pycache__" not in p.parts]
    candidates += [ROOT / "docs" / "ENVIRONMENT.md"]
    selected = sorted(set(p for p in candidates if p.is_file()))
    for path in selected:
        if not path.resolve().is_relative_to(ROOT) or path.is_symlink():
            raise ValueError("Refusing a source file outside the project")
    entries = [(path, path.relative_to(ROOT).as_posix()) for path in selected]
    dataset = "inputs/skillsbench"
    if args.with_dataset:
        dataset, dataset_entries = frozen_dataset()
        entries.extend(dataset_entries)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in entries:
            if name == "evaluation.yaml":
                content = path.read_text(encoding="utf-8-sig")
                for key, placeholder in (("framework", "inputs/nextagent-linux-x64.tar.gz"), ("dataset", dataset)):
                    content, count = re.subn(r"(?m)^" + key + r":.*$", key + ": " + placeholder, content)
                    if count != 1:
                        raise ValueError("evaluation.yaml must declare one top-level " + key)
                archive.writestr(name, content)
            else:
                archive.write(path, name)
    print(json.dumps({"bundle": str(output), "files": len(entries), "bytes": output.stat().st_size,
                      "includes_credentials": False, "includes_dataset": args.with_dataset,
                      "includes_framework": False, "includes_results": False}, ensure_ascii=True))
    return 0


def credentials(env: dict[str, str], filename: Path | None, command: str) -> None:
    if filename is not None:
        value = json.loads(filename.expanduser().read_text(encoding="utf-8-sig"))
        if not isinstance(value, list) or not value:
            raise ValueError("Credentials file must be a nonempty JSON list of name/key objects")
        env["NAB_API_KEYS"] = json.dumps(value)
    elif command in {"run", "resume", "analyze", "doctor"} and not env.get("NAB_API_KEYS") and not env.get("OPENAI_API_KEY"):
        if os.name == "nt" and (ROOT / ".secrets").is_dir():
            powershell = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
            if not powershell:
                raise ValueError("Set OPENAI_API_KEY or --credentials-file; native PowerShell is needed only for the optional Windows encrypted credential store")
            common = str(ROOT / "scripts/Common.ps1").replace("'", "''")
            result = subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-Command", ". '" + common + "'; Get-BenchKeyRing"],
                                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
                                    env=env, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode:
                raise ValueError("Cannot read this Windows user's encrypted credentials. Use your own OPENAI_API_KEY or --credentials-file")
            env["NAB_API_KEYS"] = json.dumps(json.loads(result.stdout.lstrip("\ufeff").strip()))


def forward(arguments: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--credentials-file", type=Path)
    args, remaining = parser.parse_known_args(arguments)
    if not remaining:
        raise ValueError("Choose a command; run python bench.py --help")
    if not PYTHON.is_file():
        raise ValueError("First run: python bench.py setup --framework <release.tar.gz> [--dataset <skillsbench-root>]")
    env = environment()
    if not any(value in {"-h", "--help"} for value in remaining):
        credentials(env, args.credentials_file, remaining[0])
    for index, value in enumerate(remaining[:-1]):
        if value in {"--framework", "--dataset"} and not remaining[index + 1].startswith("--"):
            remaining[index + 1] = str(Path(remaining[index + 1]).expanduser().resolve())
    command = [str(PYTHON), "-m", "nextagent_bench", *remaining]
    if not args.background:
        return subprocess.call(command, cwd=ROOT, env=env)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    directory = ROOT / "launches"
    directory.mkdir(exist_ok=True)
    stdout, stderr = directory / (stamp + ".stdout.log"), directory / (stamp + ".stderr.log")
    with stdout.open("w", encoding="utf-8") as out, stderr.open("w", encoding="utf-8") as err:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                   start_new_session=os.name != "nt",
                                   creationflags=(subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0)
    record = {"pid": process.pid, "arguments": remaining, "stdout": str(stdout), "stderr": str(stderr)}
    (directory / (stamp + ".json")).write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=True))
    return 0


def main(arguments: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    if not arguments or arguments[0] in {"-h", "--help"}:
        print("NextAgent benchmark: no Codex or host Node.js required.\n"
              "  python bench.py setup --framework <release.tar.gz> [--dataset <skillsbench-root>]\n"
              "  python bench.py doctor\n"
              "  python bench.py run --suite full --jobs 2 [--background] [--credentials-file <keys.json>]\n"
              "  python bench.py status|metrics|stop|resume|report <run-id>\n"
              "  python bench.py bundle [--with-dataset] [--output <handoff.zip>]\n"
              "Core command help: python bench.py <command> --help\n"
              "Requirements and credentials: docs/ENVIRONMENT.md")
        return 0
    if sys.version_info < (3, 12):
        print("Python 3.12 or newer is required.", file=sys.stderr)
        return 2
    try:
        if arguments[0] == "setup":
            return setup(arguments[1:])
        if arguments[0] == "bundle":
            return bundle(arguments[1:])
        return forward(arguments)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("Error: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
