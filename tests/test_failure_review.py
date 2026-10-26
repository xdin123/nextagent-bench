from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nextagent_bench.util import write_json


class FailureEvidenceTests(unittest.TestCase):
    def test_cli_separates_timeout_tls_failure_and_account_error(self):
        script = Path(__file__).resolve().parents[1] / "scripts/summarize_failures.py"
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            write_json(run / "manifest.json", {"tasks": ["slow", "tls", "account"]})
            for task in ["slow", "tls", "account"]:
                record = {"task": task, "attempt": 1, "outcome": "ENVIRONMENT_ERROR", "score": None,
                          "failed_phase": "build", "error": "timed out after 10 seconds"}
                if task == "account":
                    record.update(outcome="EXECUTION_FAILED", terminal={"payload": {"code": "MODEL_AUTHENTICATION_FAILED"}})
                write_json(run / f"tasks/{task}/attempt-001/result.json", record)
            (run / "tasks/slow/attempt-001/environment-build.log").write_text("Get libssl-dev; still downloading")
            (run / "tasks/tls/attempt-001/environment-build.log").write_text("SSLEOFError: download failed\nNo matching distribution found")
            subprocess.run([sys.executable, str(script), str(run)], capture_output=True, check=True, timeout=20)
            rows = {r["task"]: r for r in json.loads((run / "failure-review/summary.json").read_text(encoding="utf-8"))["tasks"]}
            self.assertEqual(rows["slow"]["category"], "BUILD_TIMEOUT_CAUSE_UNPROVEN")
            self.assertEqual(rows["tls"]["category"], "DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK")
            self.assertEqual(rows["account"]["category"], "MODEL_ACCOUNT_AUTH_OR_BILLING")
            self.assertFalse(rows["account"]["docker_or_harness_environment"])


if __name__ == "__main__":
    unittest.main()
