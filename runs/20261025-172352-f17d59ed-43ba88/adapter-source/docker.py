from __future__ import annotations

import json
import os
import shutil
import tarfile
from pathlib import Path

import yaml

from .settings import HOME
from .util import CommandError, command, digest, read_json, tree_manifest, write_json, archive_from_container

NODE = "/opt/na-eval/node/bin/node"
HELPER = "/opt/na-eval/runtime/helper.mjs"


def ensure_task_image(project: Path, task: Path, framework_image: str, node_version: str, budget: dict,
                      log_dir: Path, legacy_image: str | None = None) -> tuple[str, dict]:
    environment_sha = digest(tree_manifest(task / "environment"))
    base = "nextagent-bench/environment:" + environment_sha[:20]
    if legacy_image:
        base = legacy_image
    elif command(["docker", "image", "inspect", base], check=False).returncode:
        command(["docker", "build", "-t", base, str(task / "environment")], timeout=budget["build_timeout"], log=log_dir / "environment-build.log")
    fingerprint = digest({"base_id": json.loads(command(["docker", "image", "inspect", base]).stdout)[0]["Id"],
                          "framework": framework_image, "node": node_version})
    image = "nextagent-bench/task:" + fingerprint[:20]
    if command(["docker", "image", "inspect", image], check=False).returncode:
        context = project / "cache" / "images" / fingerprint
        context.mkdir(parents=True, exist_ok=True)
        version = node_version.removeprefix("v")
        (context / "Dockerfile").write_text(
            f"FROM node:{version}-bookworm-slim AS node_runtime\n"
            f"FROM {base}\n"
            "COPY --from=node_runtime /usr/local/bin/node /opt/na-eval/node/bin/node\n"
            f"COPY --from={framework_image} /opt/nextagent/ /opt/nextagent/\n"
            f"COPY --from={framework_image} /opt/na-eval/runtime/ /opt/na-eval/runtime/\n", encoding="utf-8")
        command(["docker", "build", "-t", image, str(context)], timeout=budget["build_timeout"], log=log_dir / "agent-layer-build.log")
    inspected = json.loads(command(["docker", "image", "inspect", image]).stdout)[0]
    return image, {"image_id": inspected["Id"], "environment_sha": environment_sha,
                   "workdir": inspected["Config"].get("WorkingDir") or "/root",
                   "legacy_environment_override": legacy_image}


class Container:
    def __init__(self, name: str, project_name: str, task: Path, budget: dict, directory: Path):
        self.name, self.project_name, self.task = name, project_name, task
        self.budget, self.directory = budget, directory
        self.compose: list[str] | None = None
        self.created = False

    def start(self, image: str, run_id: str) -> None:
        composition = next((self.task / "environment" / name for name in ("docker-compose.yaml", "docker-compose.yml", "compose.yaml", "compose.yml")
                            if (self.task / "environment" / name).exists()), None)
        if composition:
            data = yaml.safe_load(composition.read_text(encoding="utf-8"))
            services = data.get("services", {})
            main = self.budget["verifier_service"]
            if main not in services:
                main = "main" if "main" in services else "website" if "website" in services else next(iter(services))
            audit = {"source": str(composition), "main_service": main, "removed_host_ports": {}, "removed_main_volumes": []}
            data.pop("version", None)
            data.pop("name", None)
            for key, service in services.items():
                if service.get("ports"):
                    audit["removed_host_ports"][key] = service.pop("ports")
                service.pop("container_name", None)
                service.setdefault("labels", {})["nextagent-bench.run"] = run_id
            service = services[main]
            audit["removed_main_volumes"] = service.pop("volumes", [])
            # These two upstream compose files mount host credentials/logs.
            # Evaluator artifacts use docker cp, never user credential mounts.
            for volume in audit["removed_main_volumes"]:
                text = str(volume)
                if not any(key in text for key in ("HOST_VERIFIER_LOGS_PATH", "HOST_AGENT_LOGS_PATH", ".config/gcloud")):
                    raise ValueError(f"Unreviewed task volume mapping: {text}")
            service.pop("build", None)
            service.pop("deploy", None)
            service.update({"image": image, "entrypoint": [], "command": ["sh", "-c", "sleep infinity"],
                            "cpus": self.budget["cpus"], "mem_limit": str(self.budget["memory_mb"]) + "m"})
            target = self.directory / "compose.effective.yaml"
            target.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            write_json(self.directory / "compose-changes.json", audit)
            self.compose = ["docker", "compose", "--project-directory", str(composition.parent), "-p", self.project_name, "-f", str(target)]
            write_json(self.directory / "compose-owner.json", {"project": self.project_name, "directory": str(composition.parent)})
            self.created = True
            command(self.compose + ["up", "-d", "--build"], timeout=self.budget["build_timeout"], log=self.directory / "compose-start.log")
            self.name = command(self.compose + ["ps", "-q", main]).stdout.strip()
            if not self.name:
                raise CommandError("Compose main container not found")
        else:
            args = ["docker", "run", "-d", "--name", self.name, "--label", "nextagent-bench.run=" + run_id,
                    "--cpus", str(self.budget["cpus"]), "--memory", str(self.budget["memory_mb"]) + "m",
                    "--entrypoint", "sh"]
            if self.budget.get("gpus"):
                args.extend(["--gpus", str(self.budget["gpus"])])
            args.extend([image, "-c", "sleep infinity"])
            self.created = True
            command(args, timeout=120, log=self.directory / "container-start.log")
        self.exec([NODE, "--version"])

    def exec(self, args: list[str], *, input_text: str | None = None, timeout: float = 120,
             check: bool = True, log: Path | None = None):
        prefix = ["docker", "exec"] + (["-i"] if input_text is not None else [])
        return command(prefix + [self.name] + args, input_text=input_text, timeout=timeout, check=check, log=log)

    def helper(self, action: str, value: dict | None = None, *, timeout: float = 120) -> dict:
        result = self.exec([NODE, HELPER, action], input_text=json.dumps(value or {}), timeout=timeout)
        return json.loads(result.stdout.strip().splitlines()[-1])

    def rpc(self, method: str, path: str, body=None) -> dict:
        return self.helper("rpc", {"method": method, "path": path, "body": body}, timeout=40)

    def put(self, source: Path, destination: str) -> None:
        command(["docker", "cp", str(source), self.name + ":" + destination], timeout=600)

    def get(self, source: str, destination: Path, *, required: bool = True) -> bool:
        destination.parent.mkdir(parents=True, exist_ok=True)
        result = command(["docker", "cp", self.name + ":" + source, str(destination)], timeout=600, check=False)
        if result.returncode and required:
            raise CommandError(f"Artifact collection failed: {source}: {result.stderr[-600:]}")
        return result.returncode == 0

    def archive_home(self, destination: Path) -> dict:
        """Keep POSIX links and names in tar, extract only readable log files."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        archive_from_container(self.name, HOME, destination)
        extracted = 0
        with tarfile.open(destination) as archive:
            for member in archive:
                parts = Path(member.name.replace("\\", "/")).parts
                if not member.isfile() or len(parts) < 3 or parts[0] != "home" or parts[1] != "logs" or ".." in parts:
                    continue
                output = destination.parent / "nextagent-home" / Path(*parts[1:])
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, output.open("wb") as target:
                    shutil.copyfileobj(source, target)
                extracted += 1
        return {"file": destination.name, "size_bytes": destination.stat().st_size, "extracted_log_files": extracted,
                "workspace": "home/workspaces/execution/<scope>/workspace inside the archive"}

    def launch(self, model: str, base_url: str, api_key: str | None = None) -> None:
        # Pass the secret via inherited environment, never argv/value or a file.
        value = api_key or os.environ.get("OPENAI_API_KEY")
        if not value:
            raise ValueError("OPENAI_API_KEY is not set")
        environment = dict(os.environ, OPENAI_API_KEY=value)
        command(["docker", "exec", "-d", "-e", "OPENAI_API_KEY", "-e", "OPENAI_MODEL_NAME=" + model,
                 "-e", "OPENAI_BASE_URL=" + base_url, "-e", "NEXTAGENT_HOME=" + HOME,
                 self.name, "sh", "-c", f"echo $$ > /opt/na-eval/run/app.pid; exec {NODE} /opt/nextagent/.bench-start.mjs > /opt/na-eval/run/na-start.log 2>&1"], timeout=30, env=environment)

    def stop_application(self) -> dict:
        return self.helper("stop", timeout=60)

    def close(self) -> None:
        if not self.created:
            return
        if self.compose:
            command(self.compose + ["down", "--volumes", "--remove-orphans"], timeout=120, check=False,
                    log=self.directory / "compose-stop.log")
        else:
            command(["docker", "rm", "-f", self.name], timeout=60, check=False)
