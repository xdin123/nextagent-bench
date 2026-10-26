from __future__ import annotations

import json
import os
import shutil
import tempfile
import tarfile
import unittest
import uuid
from pathlib import Path

from nextagent_bench.docker import Container
from nextagent_bench.paths import make_mappings
from nextagent_bench.runner import poll_run
from nextagent_bench.settings import HOME
from nextagent_bench.util import CommandError, command


@unittest.skipUnless(os.environ.get("NAB_DOCKER_TESTS") == "1", "Set NAB_DOCKER_TESTS=1 for isolated Docker contract tests")
class DockerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = tempfile.TemporaryDirectory()
        root = Path(cls.context.name)
        shutil.copytree(Path(__file__).resolve().parents[1] / "nextagent_bench/runtime", root / "runtime")
        (root / "Dockerfile").write_text("FROM node:22.22.0-bookworm-slim\nCOPY runtime /opt/na-eval/runtime\nRUN mkdir -p /opt/na-eval/node/bin /fixture && ln -s /usr/local/bin/node /opt/na-eval/node/bin/node\nWORKDIR /fixture\n")
        cls.image = "nextagent-bench/contracts:" + uuid.uuid4().hex[:12]
        command(["docker", "build", "-t", cls.image, str(root)], timeout=300)

    @classmethod
    def tearDownClass(cls):
        command(["docker", "image", "rm", cls.image], check=False)
        cls.context.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        name = "nab-contract-" + uuid.uuid4().hex[:12]
        self.container = Container(name, name, self.directory, {"cpus": 1, "memory_mb": 256}, self.directory)
        self.container.start(self.image, "contract-tests")
        self.container.helper("prepare", {"agentId": "fixture-agent"})

    def tearDown(self):
        self.container.close()
        self.temporary.cleanup()

    def test_multi_root_outputs_are_visible_at_original_verifier_paths(self):
        self.container.exec(["sh", "-c", f"mkdir -p {HOME}/workspaces/execution/test/workspace /data /output; echo input > /fixture/input.txt; echo data > /data/source.txt"])
        bridge = self.container.helper("bridge", {"mappings": make_mappings("/fixture", ["/data", "/output"])})
        workspace = bridge["workspace"]
        self.container.exec(["sh", "-c", f"printf '{{\"ok\":true}}' > {workspace}/_roots/output/result.json"])
        texts = self.container.helper("read", {"paths": ["/fixture/input.txt", "/data/source.txt", "/output/result.json", workspace + "/input.txt"]})
        self.assertEqual(texts["/fixture/input.txt"], texts[workspace + "/input.txt"])
        self.assertEqual(json.loads(texts["/output/result.json"]), {"ok": True})
        self.assertEqual(texts["/data/source.txt"], "data\n")

    def test_skill_copy_has_no_extra_skills_directory(self):
        source = self.directory / "skills" / "fixture"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("fixture")
        self.container.put(str(source.parent) + "/.", HOME + "/skills/")
        result = self.container.helper("read", {"paths": [HOME + "/skills/fixture/SKILL.md", HOME + "/skills/skills/fixture/SKILL.md"]})
        self.assertEqual(result[HOME + "/skills/fixture/SKILL.md"], "fixture")
        self.assertIsNone(result[HOME + "/skills/skills/fixture/SKILL.md"])

    def test_archive_preserves_workspace_and_extracts_only_logs(self):
        self.container.exec(["sh", "-c", f"mkdir -p {HOME}/logs {HOME}/workspaces; echo log > {HOME}/logs/run.jsonl; echo output > {HOME}/workspaces/result.txt; ln -s result.txt {HOME}/workspaces/link.txt"])
        target = self.directory / "nextagent-home.tar"
        result = self.container.archive_home(target)
        with tarfile.open(target) as archive:
            self.assertEqual(archive.extractfile("home/workspaces/result.txt").read(), b"output\n")
            self.assertTrue(archive.getmember("home/workspaces/link.txt").issym())
        self.assertEqual(result["extracted_log_files"], 1)
        self.assertFalse((self.directory / "nextagent-home/workspaces").exists())

    def test_discovery_facts_distinguish_system_skills_from_user_catalog(self):
        self.container.exec(["mkdir", "-p", HOME + "/logs"])
        evidence = self.directory / "discovery.jsonl"
        evidence.write_text('\n'.join(json.dumps(item) for item in [
            {"event": "skill.discovery.registered", "providerId": "local-skills-system", "skillId": "model-only-skill"},
            {"event": "skill.discovery.registered", "providerId": "builtin-skills", "skillId": "builtin"},
        ]))
        self.container.put(evidence, HOME + "/logs/discovery.jsonl")
        result = self.container.helper("skill-discovery")
        self.assertEqual(result["registered"], ["model-only-skill"])

    def test_launcher_uses_import_only_esm_public_export(self):
        from unittest.mock import patch
        import time
        product = self.directory / "product"
        module = product / "node_modules/@nextagent/agent-app"
        module.mkdir(parents=True)
        (product / "package.json").write_text(json.dumps({"type": "module"}))
        (module / "package.json").write_text(json.dumps({"type": "module", "exports": {"import": "./index.js"}}))
        (module / "index.js").write_text("import http from 'node:http'; export async function createNextAgentAppAsync(){let server;return{start:async()=>{server=http.createServer((q,r)=>r.end('{}')).listen(31872,'127.0.0.1')},close:async()=>{server.close()}}}")
        self.container.put(str(product) + "/.", "/opt/nextagent/")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-no-provider"}):
            self.container.launch("fixture", "https://unused.invalid")
        for attempt in range(20):
            try:
                result = self.container.rpc("GET", "/api/v1/runtime/bootstrap")
                break
            except Exception:
                time.sleep(0.1)
        else:
            self.fail("Import-only public ESM export could not start")
        self.assertEqual(result, {})
        self.assertTrue(self.container.helper("status")["running"])
        self.assertTrue(self.container.stop_application()["stopped"])

    def test_host_and_container_http_polling_cross_event_pages(self):
        script = self.directory / "http-fixture.mjs"
        script.write_text("""import http from 'node:http';
http.createServer((req,res)=>{
const u=new URL(req.url,'http://fixture');
const after=Number(u.searchParams.get('afterSequence')||0);
const events=after===0?Array.from({length:1000},(_,i)=>({eventId:String(i+1),sequence:i+1,eventType:'LLM_CONTENT_DELTA',payload:{}})):[{eventId:'1001',sequence:1001,eventType:'REQUEST_COMPLETED',payload:{content:'done'}}];
res.setHeader('content-type','application/json');res.end(JSON.stringify({events}));
}).listen(31872,'127.0.0.1');
""")
        self.container.put(script, "/opt/na-eval/run/http-fixture.mjs")
        command(["docker", "exec", "-d", self.container.name, "/opt/na-eval/node/bin/node", "/opt/na-eval/run/http-fixture.mjs"])
        result = poll_run(self.container, "s", "r", "q", 15, self.directory / "trajectory.jsonl")
        self.assertEqual(result["status"], "REQUEST_COMPLETED")
        self.assertEqual(len((self.directory / "trajectory.jsonl").read_text().splitlines()), 1001)

    def test_bridge_rejects_system_root_without_deleting_it(self):
        self.container.exec(["sh", "-c", f"mkdir -p {HOME}/workspaces/execution/test/workspace"])
        with self.assertRaises(CommandError):
            self.container.helper("bridge", {"mappings": [{"physical": "/usr", "logical": "workspace", "relocate": True}]})
        self.container.exec(["test", "-f", "/usr/bin/env"])


if __name__ == "__main__":
    unittest.main()
