from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nextagent_bench.docker import Container, build_image
from nextagent_bench.settings import load_task
from nextagent_bench.util import CommandError


class BuildRecoveryTests(unittest.TestCase):
    def test_compose_auxiliary_builds_keep_the_build_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "environment").mkdir()
            (root / "task.md").write_text("---\nsandbox:\n  memory_mb: 256\n---\nFixture")
            (root / "environment/compose.yaml").write_text("services:\n  main:\n    image: fixture\n")
            held = [False]

            class Gate:
                def __enter__(self):
                    held[0] = True

                def __exit__(self, *args):
                    held[0] = False

            def execute(args, **kwargs):
                if "up" in args:
                    self.assertTrue(held[0], "Compose can build auxiliary images and must keep its reservation")
                return subprocess.CompletedProcess(args, 0, "fixture-container\n", "")

            container = Container("fixture", "fixture", root, load_task(root), root)
            with patch("nextagent_bench.docker.command", side_effect=execute):
                container.start("fixture", "fixture-run", Gate())

    def test_transient_build_failure_keeps_logs_and_uses_remaining_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            context.mkdir()
            original = "FROM fixture\nRUN true\n"
            (context / "Dockerfile").write_text(original)
            clock = [0.0]
            attempts = []

            def execute(args, *, timeout, log):
                attempts.append(timeout)
                clock[0] += 1
                log.write_text("502 Bad Gateway" if len(attempts) == 1 else "success")
                if len(attempts) == 1:
                    raise CommandError("502 Bad Gateway")
                return subprocess.CompletedProcess(args, 0)

            with patch("nextagent_bench.docker.command", side_effect=execute), \
                    patch("nextagent_bench.docker.time.monotonic", side_effect=lambda: clock[0]), \
                    patch("nextagent_bench.docker.time.sleep", side_effect=lambda seconds: clock.__setitem__(0, clock[0] + seconds)):
                build_image("fixture", context, 10, root / "build.log")
            audit = json.loads((root / "build.log.attempts.json").read_text())
            self.assertEqual(audit["status"], "SUCCEEDED")
            self.assertEqual(attempts, [10, 7])
            self.assertEqual((root / "build.log").read_text(), "502 Bad Gateway")
            self.assertEqual((root / "build.retry-002.log").read_text(), "success")
            self.assertEqual((context / "Dockerfile").read_text(), original)

    def test_non_network_build_error_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("nextagent_bench.docker.command", side_effect=CommandError("Dockerfile parse error")):
                with self.assertRaises(CommandError):
                    build_image("fixture", root, 10, root / "build.log")
            audit = json.loads((root / "build.log.attempts.json").read_text())
            self.assertEqual(audit["status"], "FAILED")
            self.assertEqual(len(audit["attempts"]), 1)

    def test_timeout_is_not_retried_with_a_fresh_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("nextagent_bench.docker.command", side_effect=subprocess.TimeoutExpired(["docker"], 1)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    build_image("fixture", root, 1, root / "build.log")
            audit = json.loads((root / "build.log.attempts.json").read_text())
            self.assertEqual(audit["status"], "FAILED")
            self.assertEqual(len(audit["attempts"]), 1)
            self.assertEqual(audit["attempts"][0]["outcome"], "TIMEOUT")


if __name__ == "__main__":
    unittest.main()
