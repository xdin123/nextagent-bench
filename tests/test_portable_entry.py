from __future__ import annotations

import os
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


class PortableEntryTests(unittest.TestCase):
    def test_dataset_bundle_keeps_frozen_tasks_and_needs_no_dataset_argument(self):
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(project / "bench.py", root / "bench.py")
            contents = {"sample/task.md": b"Task input", "sample/verifier/test.sh": b"original verifier"}
            files = {name: hashlib.sha256(value).hexdigest() for name, value in contents.items()}
            identity = hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            dataset = root / "datasets" / identity
            for name, content in contents.items():
                path = dataset / "tasks" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            (dataset / "files.json").write_text(json.dumps(files), encoding="utf-8")
            (dataset / "manifest.json").write_text(json.dumps({"sha256": identity, "tasks": ["sample"]}), encoding="utf-8")
            (dataset / "LICENSE").write_text("Dataset license", encoding="utf-8")
            (dataset / "debug.tmp").write_text("Excluded", encoding="utf-8")
            (root / "evaluation.yaml").write_text("framework: artifacts/old\ndataset: datasets/" + identity + "\n", encoding="utf-8")
            output = root / "ready.zip"
            result = subprocess.run([sys.executable, "-S", str(root / "bench.py"), "bundle", "--with-dataset", "--output", str(output)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as archive:
                self.assertIn("dataset: datasets/" + identity, archive.read("evaluation.yaml").decode())
                self.assertIn("framework: inputs/nextagent-linux-x64.tar.gz", archive.read("evaluation.yaml").decode())
                for name, content in contents.items():
                    self.assertEqual(archive.read("datasets/" + identity + "/tasks/" + name), content)
                self.assertEqual(archive.read("datasets/" + identity + "/LICENSE"), b"Dataset license")
                self.assertFalse(any(name.endswith("debug.tmp") for name in archive.namelist()))
            (dataset / "tasks/sample/task.md").write_text("Changed after freezing", encoding="utf-8")
            result = subprocess.run([sys.executable, "-S", str(root / "bench.py"), "bundle", "--with-dataset", "--output", str(root / "changed.zip")],
                                    capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("changed", result.stderr.lower())

    def test_source_bundle_has_no_credentials_or_runtime_data(self):
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "handoff.zip"
            result = subprocess.run([sys.executable, "-S", str(project / "bench.py"), "bundle", "--output", str(output)],
                                    cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertIn("bench.py", names)
                self.assertIn("docs/ENVIRONMENT.md", names)
                self.assertIn("profiles/agent.yaml", names)
                forbidden = (".secrets/", ".venv/", "runs/", "cache/", "artifacts/", "datasets/", ".git/", "launches/")
                self.assertFalse(any(name.startswith(forbidden) or "__pycache__" in name for name in names))
                config = archive.read("evaluation.yaml").decode("utf-8")
                self.assertIn("framework: inputs/nextagent-linux-x64.tar.gz", config)
                self.assertIn("dataset: inputs/skillsbench", config)

    def test_exported_entry_works_without_site_packages_and_explains_setup(self):
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "handoff.zip"
            subprocess.run([sys.executable, "-S", str(project / "bench.py"), "bundle", "--output", str(output)],
                           capture_output=True, check=True, timeout=30)
            exported = root / "project with spaces"
            with zipfile.ZipFile(output) as archive:
                archive.extractall(exported)
            env = {k: v for k, v in os.environ.items() if not k.startswith("CODEX_") and k not in {"NAB_API_KEYS", "OPENAI_API_KEY", "PYTHONPATH"}}
            help_result = subprocess.run([sys.executable, "-S", str(exported / "bench.py"), "--help"],
                                         cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            result = subprocess.run([sys.executable, "-S", str(exported / "bench.py"), "doctor", "--offline"],
                                    cwd=root, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("setup", result.stderr.lower())
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
