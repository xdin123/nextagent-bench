from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import time
from pathlib import Path

from .util import command, file_sha, now, write_json, archive_from_container


def credential_ring() -> list[dict]:
    raw = os.environ.get("NAB_API_KEYS")
    keys = json.loads(raw) if raw else [{"name": "environment", "key": os.environ.get("OPENAI_API_KEY", "")}]
    if not isinstance(keys, list) or not keys:
        raise ValueError("No model credentials. Set OPENAI_API_KEY or NAB_API_KEYS, or use bench.py --credentials-file. Windows users may also use Set-ModelCredential.ps1")
    names, values, output = set(), set(), []
    for item in keys:
        name, key = item.get("name", ""), item.get("key", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name) or not isinstance(key, str) or not key:
            raise ValueError("Invalid credential alias or empty key")
        if name in names:
            raise ValueError("Duplicate credential alias: " + name)
        names.add(name)
        if key not in values:
            values.add(key)
            output.append({"name": name, "key": key})
    return output


class ModelGateway:
    def __init__(self, project: Path, directory: Path, manifest: dict):
        self.project, self.directory, self.manifest = project, directory, manifest
        self.name = "nab-model-" + manifest["run_id"]
        self.network = "nab-model-net-" + manifest["run_id"]
        self.url = "http://" + self.name + ":8787/v1"
        self.token = secrets.token_urlsafe(32)
        self.control_token = secrets.token_urlsafe(32)
        self.created = False
        self.lock_owned = False
        self.lock = project / ".state" / "shared-model-quota.lock"
        self.started_at = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(3)
        self.output = directory / "model-gateway" / self.started_at

    def acquire_project_quota(self):
        # One active batch/diagnostic gateway per project. Independent sidecars
        # must never each claim the same account's full budget.
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            previous = json.loads(self.lock.read_text(encoding="utf-8"))
            pid = str(previous["pid"])
            if os.name == "nt":
                active = pid in command(["tasklist", "/FI", "PID eq " + pid, "/FO", "CSV", "/NH"], check=False).stdout.split('"')
            else:
                try:
                    os.kill(int(pid), 0)
                    active = True
                except ProcessLookupError:
                    active = False
            container = False if active else command(["docker", "ps", "-aq", "--filter", "name=^/" + previous["container"] + "$"]).stdout.strip()
            if active or container:
                raise ValueError("Shared quota is already owned by run " + previous["run_id"] +
                                 ". Wait for it, or stop/recover that run before starting another model-consuming batch.")
            self.lock.unlink()
            descriptor = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "run_id": self.manifest["run_id"], "container": self.name}, stream)
        self.lock_owned = True

    def start(self):
        self.acquire_project_quota()
        self.output.mkdir(parents=True, exist_ok=True)
        source = Path(__file__).parent / "model_proxy.py"
        image = "nextagent-bench/model-gateway:" + file_sha(source)[:20]
        if command(["docker", "image", "inspect", image], check=False).returncode:
            context = self.project / "cache" / "model-gateway" / file_sha(source)
            context.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, context / "model_proxy.py")
            (context / "Dockerfile").write_text('FROM python:3.12-slim\nCOPY model_proxy.py /opt/model_proxy.py\nENTRYPOINT ["python", "-u", "/opt/model_proxy.py"]\n', encoding="utf-8")
            from .docker import build_image
            build_image(image, context, 600, self.output / "build.log")
        keys = credential_ring()
        config = {"upstream": self.manifest["base_url"], "quota": self.manifest["quota"],
                  "capture_model_exchanges": self.manifest.get("analysis", {}).get("capture_model_exchanges", True)}
        environment = dict(os.environ, NAB_API_KEYS=json.dumps(keys), NAB_PROXY_CONFIG=json.dumps(config), NAB_PROXY_TOKEN=self.token, NAB_CONTROL_TOKEN=self.control_token)
        command(["docker", "network", "create", "--label", "nextagent-bench.run=" + self.manifest["run_id"], self.network])
        self.created = True
        command(["docker", "run", "-d", "--name", self.name, "--network", self.network,
                 "--label", "nextagent-bench.run=" + self.manifest["run_id"], "--label", "nextagent-bench.role=model-gateway",
                 "--memory", "256m", "--cpus", "0.5", "-e", "NAB_API_KEYS", "-e", "NAB_PROXY_CONFIG", "-e", "NAB_PROXY_TOKEN", "-e", "NAB_CONTROL_TOKEN", image],
                env=environment, log=self.output / "start.log")
        for _attempt in range(30):
            check = command(["docker", "exec", self.name, "python", "-c",
                             "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8787/health',timeout=2).read()"], check=False)
            if check.returncode == 0:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("Private model gateway did not become healthy")
        write_json(self.output / "identity.json", {"created_at": now(), "upstream": self.manifest["base_url"], "internal_url": self.url,
                   "credential_aliases": [item["name"] for item in keys], "quota": config["quota"], "image": image,
                   "credentials_shared_account": True, "host_ports_published": False})

    def connect(self, container: str):
        command(["docker", "network", "connect", self.network, container])

    def set_concurrency(self, jobs: int):
        code = ("import os,json,sys,urllib.request; r=urllib.request.Request('http://127.0.0.1:8787/control/concurrency',"
                "data=json.dumps({'jobs':int(sys.argv[1])}).encode(),headers={'Authorization':'Bearer '+os.environ['NAB_CONTROL_TOKEN'],"
                "'Content-Type':'application/json'}); print(urllib.request.urlopen(r,timeout=10).status)")
        command(["docker", "exec", self.name, "python", "-c", code, str(jobs)])

    def metrics(self) -> dict:
        code = ("import os,urllib.request; r=urllib.request.Request('http://127.0.0.1:8787/metrics',"
                "headers={'Authorization':'Bearer '+os.environ['NAB_PROXY_TOKEN']}); print(urllib.request.urlopen(r,timeout=5).read().decode())")
        return json.loads(command(["docker", "exec", self.name, "python", "-c", code]).stdout)

    def task_url(self, task: str, attempt: int) -> str:
        from urllib.parse import quote
        return self.url[:-3] + "/tasks/" + quote(task, safe="") + f"/attempts/{attempt}/v1"

    def export_evidence(self) -> Path | None:
        target = self.output / "exchanges.tar"
        if not self.manifest.get("analysis", {}).get("capture_model_exchanges", True):
            return None
        if not target.exists():
            archive_from_container(self.name, "/evidence", target)
        return target

    def completion(self, task: str, attempt: int, body: dict, timeout: int) -> dict:
        from urllib.parse import quote
        value = {"path": "/analysis/" + quote(task, safe="") + f"/attempts/{attempt}/v1/chat/completions", "body": body, "timeout": timeout}
        result = command(["docker", "exec", "-i", self.name, "python", "/opt/model_proxy.py", "client"],
                         input_text=json.dumps(value), timeout=timeout + 150)
        response = json.loads(result.stdout)
        return response

    def close(self):
        try:
            if not self.created:
                return
            try:
                self.export_evidence()
                metrics = command(["docker", "exec", self.name, "python", "-c",
                    "import os,urllib.request; r=urllib.request.Request('http://127.0.0.1:8787/metrics',headers={'Authorization':'Bearer '+os.environ['NAB_PROXY_TOKEN']}); print(urllib.request.urlopen(r,timeout=5).read().decode())"], check=False)
                if metrics.returncode == 0:
                    write_json(self.output / "metrics.json", json.loads(metrics.stdout))
                logs = command(["docker", "logs", self.name], check=False)
                (self.output / "events.jsonl").write_text(logs.stdout, encoding="utf-8")
            except Exception as error:
                write_json(self.output / "evidence-export-error.json", {"error": str(error), "at": now()})
            finally:
                command(["docker", "rm", "-f", self.name], timeout=60, check=False)
                # Disconnect only our auxiliary network for kept task containers.
                inspection = command(["docker", "network", "inspect", self.network], check=False)
                if inspection.returncode == 0:
                    for identifier in json.loads(inspection.stdout)[0].get("Containers", {}):
                        command(["docker", "network", "disconnect", "-f", self.network, identifier], check=False)
                command(["docker", "network", "rm", self.network], check=False)
        finally:
            if self.lock_owned:
                self.lock.unlink(missing_ok=True)
                self.lock_owned = False
