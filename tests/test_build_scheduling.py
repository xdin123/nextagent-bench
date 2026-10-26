from __future__ import annotations

import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from nextagent_bench.runner import MemoryGate, execute_task
from nextagent_bench.util import tree_manifest, write_json


class ReadyContainerSchedulingTests(unittest.TestCase):
    def test_ready_container_starts_while_unrelated_build_holds_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task = root / "datasets/d/tasks/ready"
            task.mkdir(parents=True)
            (task / "task.md").write_text("---\nsandbox:\n  memory_mb: 256\n---\nTask", encoding="utf-8")
            write_json(root / "datasets/d/files.json", {"ready/" + k: v for k, v in tree_manifest(task).items()})
            run = root / "runs/run"
            write_json(run / "config/path-policy.json", {})
            gate = threading.Semaphore(1)
            build_requested, build_active, release_build, started = (threading.Event() for _ in range(4))

            def other_build():
                build_requested.wait(5)
                with gate:
                    build_active.set()
                    release_build.wait(5)

            def prepare(*args):
                build_requested.set()
                if not build_active.wait(3):
                    raise RuntimeError("Fixture build did not start")
                return {"provided_skills": []}

            class ReadyContainer:
                created = False

                def __init__(self, *args):
                    pass

                def start(self, *args):
                    started.set()
                    raise InterruptedError("End the fixture after observable startup")

            manifest = {"dataset_sha": "d", "run_id": "run", "model": "fixture", "framework_sha": "f",
                        "framework": {"candidate": {}}, "jobs": 2}
            with ThreadPoolExecutor(max_workers=2) as pool, \
                    patch("nextagent_bench.runner.Container", ReadyContainer), \
                    patch("nextagent_bench.runner.ensure_task_image", return_value=("image", {"workdir": "/app"})), \
                    patch("nextagent_bench.runner.adapt_task", side_effect=prepare):
                builder = pool.submit(other_build)
                worker = pool.submit(execute_task, root, run, manifest, "ready", "framework", gate, MemoryGate(1024), None)
                try:
                    self.assertTrue(started.wait(3), "A ready container was blocked behind an unrelated image build")
                finally:
                    release_build.set()
                self.assertEqual(worker.result(timeout=3)["outcome"], "INTERRUPTED")
                builder.result(timeout=3)


if __name__ == "__main__":
    unittest.main()
