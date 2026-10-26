from __future__ import annotations

import difflib
import re
from pathlib import Path, PurePosixPath

from .util import file_sha, write_json


def predict_workdir(dockerfile: Path) -> str:
    """Planning hint only; execution always uses Docker image inspect."""
    import posixpath
    import shlex
    variables, workdir = {}, "/root"
    text = re.sub(r"\\\r?\n", " ", dockerfile.read_text(encoding="utf-8"))
    for line in text.splitlines():
        words = line.strip().split(None, 1)
        if len(words) != 2:
            continue
        instruction, value = words[0].upper(), words[1]
        if instruction == "FROM":
            variables, workdir = {}, "/root"
        elif instruction in {"ENV", "ARG"}:
            pairs = shlex.split(value)
            if instruction == "ENV" and len(pairs) == 2 and "=" not in pairs[0]:
                variables[pairs[0]] = pairs[1]
            else:
                for pair in pairs:
                    if "=" in pair:
                        key, val = pair.split("=", 1)
                        variables[key] = val
        elif instruction == "WORKDIR":
            value = value.strip('"\'')
            value = re.sub(r"\$\{([A-Za-z_][A-Za-z_0-9]*)\}|\$([A-Za-z_][A-Za-z_0-9]*)", lambda m: variables.get(m[1] or m[2], m[0]), value)
            if "$" in value:
                raise ValueError(f"Unresolved WORKDIR in {dockerfile}; build and inspect before planning")
            workdir = posixpath.normpath(posixpath.join(workdir, value))
    return validate_root(workdir)


def validate_root(path: str) -> str:
    if not path.startswith("/") or ".." in PurePosixPath(path).parts:
        raise ValueError(f"Unsafe task root: {path}")
    path = path.rstrip("/")
    if path in {"", "/bin", "/sbin", "/usr", "/etc", "/dev", "/proc", "/sys", "/opt", "/home", "/var"}:
        raise ValueError(f"System root cannot be relocated: {path}")
    if path.startswith(("/bin/", "/sbin/", "/usr/", "/etc/", "/dev/", "/proc/", "/sys/")):
        raise ValueError(f"System root cannot be relocated: {path}")
    if path.startswith(("/opt/nextagent", "/opt/na-eval")):
        raise ValueError(f"Task root overlaps evaluator: {path}")
    return path


def make_mappings(workdir: str, extra_roots: list[str]) -> list[dict]:
    workdir = validate_root(workdir)
    result = [{"physical": workdir, "logical": "workspace", "relocate": True}]
    for root in extra_roots:
        root = validate_root(root)
        if root == workdir or root.startswith(workdir + "/"):
            continue
        if workdir.startswith(root + "/"):
            raise ValueError(f"Extra root is an ancestor of WORKDIR: {root}")
        result.append({"physical": root, "logical": "workspace/_roots" + root, "relocate": True})
    result.extend([
        {"physical": "/tmp", "logical": "temp", "relocate": True},
        {"physical": "/root/.claude/skills", "logical": "workspace/skills", "relocate": False},
        {"physical": "~/.claude/skills", "logical": "workspace/skills", "relocate": False},
        {"physical": "/skills", "logical": "workspace/skills", "relocate": False},
    ])
    return sorted(result, key=lambda item: len(item["physical"]), reverse=True)


def adapt_text(text: str, mappings: list[dict]) -> str:
    # Skip complete URLs; only replace complete POSIX path prefixes. Longest
    # prefix wins, so /app/workspace never becomes workspace/workspace.
    alternatives = "|".join(re.escape(item["physical"]) for item in mappings)
    targets = {item["physical"]: item["logical"] for item in mappings}
    pattern = re.compile(r"https?://[^\s<>`\"']+|(?<![\w/.:])(?:" + alternatives + r")(?=/|[\s`'\"),;:\]}]|$)")
    return pattern.sub(lambda match: targets.get(match.group(), match.group()), text)


def adapt_task(task_dir: Path, destination: Path, mappings: list[dict]) -> dict:
    """Only agent-facing task/Skill text changes. Verifier/oracle stay untouched."""
    import shutil

    destination.mkdir(parents=True, exist_ok=True)
    source = task_dir / "task.md"
    original = source.read_text(encoding="utf-8")
    prompt = original.split("---", 2)[2].strip() if original.startswith("---") else original
    (destination / "prompt.txt").write_text(adapt_text(prompt, mappings), encoding="utf-8")
    shutil.copyfile(source, destination / "task.original.md")
    skills = task_dir / "environment" / "skills"
    patches = []
    if skills.is_dir():
        shutil.copytree(skills, destination / "skills", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for path in sorted((destination / "skills").rglob("*")):
            if not path.is_file():
                continue
            try:
                before = path.read_text(encoding="utf-8")
            except (UnicodeError, OSError):
                continue
            after = adapt_text(before, mappings)
            if before != after:
                path.write_text(after, encoding="utf-8")
                name = path.relative_to(destination).as_posix()
                patches.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=name + ".original", tofile=name))
    after = (destination / "prompt.txt").read_text(encoding="utf-8")
    patches.extend(difflib.unified_diff(prompt.splitlines(True), after.splitlines(True), fromfile="prompt.original", tofile="prompt.effective"))
    (destination / "adaptation.patch").write_text("".join(patches), encoding="utf-8")
    manifests = []
    for skill in sorted((destination / "skills").glob("*/SKILL.md")):
        import yaml
        parts = skill.read_text(encoding="utf-8").split("---", 2)
        front = yaml.safe_load(parts[1]) if len(parts) == 3 else {}
        manifests.append({"name": (front or {}).get("name", skill.parent.name), "directory": skill.parent.name,
                          "description": (front or {}).get("description", ""), "sha256": file_sha(skill)})
    audit = {"mappings": mappings, "provided_skills": manifests, "verifier_sha": file_sha(task_dir / "verifier" / "test.sh"),
             "prompt_sha": file_sha(destination / "prompt.txt")}
    write_json(destination / "adaptation.json", audit)
    return audit
