from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nextagent_bench.paths import adapt_text, make_mappings
from nextagent_bench.settings import effective_configs, load_task
from nextagent_bench.results import event_metrics, summarize_verifier, resume_identity


class PathAdaptationTests(unittest.TestCase):
    def test_nested_workdir_uses_full_prefix_and_preserves_urls(self):
        mappings = make_mappings("/app/workspace", [])
        before = "Read `/app/workspace/data/a.csv`, run `cd /app/workspace`. https://host/app/workspace/data remains a URL."
        after = adapt_text(before, mappings)
        self.assertIn("`workspace/data/a.csv`", after)
        self.assertIn("`cd workspace`", after)
        self.assertIn("https://host/app/workspace/data", after)
        self.assertNotIn("workspace/workspace", after)

    def test_multi_root_has_distinct_targets(self):
        mappings = make_mappings("/root", ["/data", "/output", "/opt/syzkaller"])
        after = adapt_text("`/data/input` `/output/a.json` `/opt/syzkaller/sys` `/root/a`", mappings)
        self.assertEqual(after, "`workspace/_roots/data/input` `workspace/_roots/output/a.json` `workspace/_roots/opt/syzkaller/sys` `workspace/a`")

    def test_skill_locations_and_temporary_paths_are_consistent(self):
        mappings = make_mappings("/root", [])
        after = adapt_text("'/root/.claude/skills/x/scripts/a.py' /tmp/x /usr/bin/python /rooted/x", mappings)
        self.assertEqual(after, "'workspace/skills/x/scripts/a.py' temp/x /usr/bin/python /rooted/x")
        self.assertEqual(adapt_text(after, mappings), after)

    def test_system_root_cannot_be_relocated(self):
        for path in ["/", "/usr", "/etc", "/opt/nextagent", "/opt/na-eval", "/app/../usr"]:
            with self.assertRaises(ValueError):
                make_mappings(path, [])


class ConfigurationTests(unittest.TestCase):
    def test_yaml_task_budgets_are_nested(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "task.md").write_text("---\nagent:\n  timeout_sec: 2400.0\nverifier:\n  timeout_sec: 900.0\nsandbox:\n  cpus: 1\n  memory_mb: 4096\n---\nRead workspace/input.txt", encoding="utf-8")
            task = load_task(path)
        self.assertEqual(task["agent_timeout"], 2400)
        self.assertEqual(task["verifier_timeout"], 900)
        self.assertEqual(task["memory_mb"], 4096)

    def test_two_config_files_preserve_user_settings_and_record_overrides(self):
        system = {"models": {"profiles": [{"models": [{"temperature": 0.2, "maxOutputTokens": 10240}]}]}, "memory": {"enabled": True}, "paths": {"agentRoot": "agents"}}
        agent = {"agentId": "default-agent", "runtimeSettings": {"guardrailEnabled": False, "maxTurns": 50}, "hooks": [{"hookId": "developer-hook-trace.loop-raw-boundary"}, {"hookId": "user-query-memory-recall"}]}
        config, definition, changes = effective_configs(system, agent, ["developer-hook-trace.loop-raw-boundary"])
        self.assertEqual(config["models"], system["models"])
        self.assertFalse(definition["runtimeSettings"]["guardrailEnabled"])
        self.assertEqual(definition["runtimeSettings"]["maxTurns"], 50)
        self.assertEqual(definition["hooks"], [{"hookId": "user-query-memory-recall"}])
        self.assertTrue(changes)
        self.assertEqual(len(agent["hooks"]), 2)


class ResultContractTests(unittest.TestCase):
    def test_ctrf_reads_status_and_does_not_call_passed_tests_failed(self):
        detail = summarize_verifier("1", {"results": {"tests": [{"name": "ok", "status": "passed"}, {"name": "skipped", "status": "skipped"}]}}, 0)
        self.assertEqual(detail["failed_tests"], [])
        self.assertEqual(detail["reward"], 1.0)
        bad = summarize_verifier("0", {"results": {"tests": [{"name": "broken", "status": "failed"}]}}, 0)
        self.assertEqual(bad["failed_tests"], ["broken"])

    def test_missing_reward_is_verifier_error_not_task_failure(self):
        self.assertEqual(summarize_verifier("", {}, 2)["outcome"], "VERIFIER_ERROR")

    def test_events_count_steps_once_and_skill_subjects(self):
        events = [{"eventType": "LLM_CONTENT_DELTA", "payload": {"stepId": "a"}}, {"eventType": "LLM_THINKING_DELTA", "payload": {"stepId": "a"}}, {"eventType": "CAPABILITY_STARTED", "payload": {"capabilityId": "Skill", "capabilitySubjectName": "mesh-analysis"}}]
        metrics = event_metrics(events)
        self.assertEqual(metrics["model_rounds"], 1)
        self.assertEqual(metrics["skills_invoked"], ["mesh-analysis"])
        self.assertEqual(metrics["tool_calls"], 1)

    def test_public_skill_target_fields_distinguish_invocation_and_success(self):
        events = [{"eventType": "CAPABILITY_STARTED", "payload": {"capabilityId": "Skill", "targetCapabilityId": "mesh-analysis"}},
                  {"eventType": "CAPABILITY_COMPLETED", "payload": {"capabilityId": "Skill", "targetCapabilityId": "mesh-analysis", "status": "SUCCEEDED"}}]
        self.assertEqual(event_metrics(events)["skills_invoked"], ["mesh-analysis"])
        self.assertEqual(event_metrics(events)["skills_loaded"], ["mesh-analysis"])

    def test_resume_never_blends_framework_model_or_profile(self):
        base = {"framework_sha": "a", "dataset_sha": "b", "profile_sha": "c", "adapter_sha": "d", "model": "qwen3.8-27b", "base_url": "https://example.test/v1", "tasks": ["one"], "skill_mode": "with-skill"}
        self.assertEqual(resume_identity(base), resume_identity(dict(base)))
        for key in base:
            changed = dict(base)
            changed[key] = "different"
            self.assertNotEqual(resume_identity(base), resume_identity(changed), key)


if __name__ == "__main__":
    unittest.main()
