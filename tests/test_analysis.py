from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nextagent_bench.analysis import DIMENSIONS, align_tool_boundaries, analyze_failures, audit_diagnosis, exchange_end_signals, reconstruct_calls, select_prompt_packet, validate_diagnosis
from nextagent_bench.util import write_json
from nextagent_bench.gateway import ModelGateway


REQUEST = {"tools": [{"type": "function", "function": {"name": "Bash", "parameters": {
    "type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"], "additionalProperties": False}}}]}


def fragments(value):
    return [{"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "call-a", "function": {"name": "Bash", "arguments": value[:5]}}]}}]},
            {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "", "function": {"arguments": value[5:]}}]}}]}]


def diagnosis():
    return {"case_summary": "fixture", "root_cause": {"owner": "INTERACTION", "conclusion": "candidate", "confidence": "VERIFIED",
            "evidence_ids": ["E001"], "missing_evidence": ["causal replay"]}, "failure_chain": [],
            "dimensions": [{"dimension": dimension, "status": "INSUFFICIENT_EVIDENCE", "observation": "no fixture evidence", "evidence_ids": []} for dimension in DIMENSIONS],
            "recommendations": [], "alternatives": [], "reproduction": [], "uncertainties": []}


class AnalysisTests(unittest.TestCase):
    def test_fragment_continuation_empty_id_preserves_valid_arguments(self):
        result = reconstruct_calls(REQUEST, fragments('{"command":"echo ok"}'))[0]
        self.assertEqual(result["id"], "call-a")
        self.assertTrue(result["visible_schema_valid"])
        self.assertEqual(result["empty_id_continuations"], 1)

    def test_model_argument_schema_violation_is_distinct_from_malformed_json(self):
        result = reconstruct_calls(REQUEST, fragments('{"command":42}'))[0]
        self.assertTrue(result["json_valid"])
        self.assertFalse(result["visible_schema_valid"])
        self.assertEqual(result["schema_violations"][0]["path"], ["command"])
        malformed = reconstruct_calls(REQUEST, fragments('{"command":'))[0]
        self.assertFalse(malformed["json_valid"])

    def test_join_detects_normalization_change_and_actual_next_round_feedback(self):
        checks = reconstruct_calls(REQUEST, fragments('{"command":"echo ok"}'))
        exchange = {"request": REQUEST, "contract_checks": checks, "location": "wire-one/"}
        later = {"request": {"messages": [{"role": "tool", "tool_call_id": "call-a", "content": "unknown parameter"}]},
                 "contract_checks": [], "location": "wire-two/"}
        diagnostic = [{"modelOutput": {"toolCalls": [{"toolCallId": "call-a", "arguments": {"command": "changed"}}]}},
                      {"toolCallId": "call-a", "toolInput": {"command": "changed"}, "status": "FAILED"}]
        joined = align_tool_boundaries([exchange, later], diagnostic)[0]
        self.assertEqual(joined["normalized_arguments_equal_wire"], [False])
        self.assertEqual(joined["executed_input_equal_wire"], [False])
        self.assertEqual(joined["subsequent_model_visible_feedback"][0]["message"]["content"], "unknown parameter")

    def test_fabricated_references_and_missing_dimensions_are_rejected(self):
        packet = {"evidence": [{"id": "E001", "kind": "observed_result"}]}
        value = diagnosis()
        value["root_cause"]["evidence_ids"] = ["E999"]
        with self.assertRaisesRegex(ValueError, "invented"):
            validate_diagnosis(value, packet)
        value = diagnosis()
        value["dimensions"].pop()
        with self.assertRaisesRegex(ValueError, "every analysis dimension"):
            validate_diagnosis(value, packet)

    def test_causal_claim_without_replay_remains_hypothesis(self):
        value = diagnosis()
        validate_diagnosis(value, {"evidence": [{"id": "E001", "kind": "observed_result"}]})
        self.assertEqual(value["root_cause"]["confidence"], "SUPPORTED_HYPOTHESIS")

    def test_evidence_insufficiency_synonym_never_becomes_high_confidence(self):
        value = diagnosis()
        value["root_cause"]["confidence"] = "INSUFFICIENT_EVIDENCE"
        validate_diagnosis(value, {"evidence": [{"id": "E001", "kind": "observed_result"}]})
        self.assertEqual(value["root_cause"]["confidence"], "UNKNOWN")
        self.assertEqual(value["root_cause"]["confidence_original"], "INSUFFICIENT_EVIDENCE")

    def test_repeated_streams_cannot_crowd_out_instruction_code_and_feedback(self):
        evidence = [{"id": f"E{i}", "kind": "provider_fragments_and_contract_checks", "location": "fixture", "content": "x"*15000, "truncated": False} for i in range(12)]
        for kind in ("model_visible_instruction_focus", "executed_framework_code", "framework_model_and_tool_boundaries"):
            evidence.append({"id": kind, "kind": kind, "location": "fixture", "content": "x"*15000, "truncated": False})
        packet = select_prompt_packet({"evidence": evidence, "evidence_gaps": []}, 30000)
        kinds = {item["kind"] for item in packet["evidence"]}
        self.assertTrue({"model_visible_instruction_focus", "executed_framework_code", "framework_model_and_tool_boundaries"} <= kinds)
        self.assertLessEqual(sum(len(json.dumps(item, ensure_ascii=False)) for item in packet["evidence"]), 30000)
        self.assertTrue(packet["evidence_gaps"])

    def test_transport_eof_is_distinct_from_provider_logical_completion(self):
        rows = [{"payload": {"choices": [{"delta": {"content": "partial"}, "finish_reason": None}]}}]
        signals = exchange_end_signals(rows)
        self.assertFalse(signals["done_marker_observed"])
        self.assertEqual(signals["finish_reasons"], [])
        rows.extend([{"payload": {"choices": [{"finish_reason": "stop"}]}}, {"payload": {"event": "done"}}])
        signals = exchange_end_signals(rows)
        self.assertTrue(signals["done_marker_observed"])
        self.assertEqual(signals["finish_reasons"], ["stop"])

    def test_failed_tool_fact_flags_an_unsupported_ok_environment_diagnosis(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            value = diagnosis()
            next(item for item in value["dimensions"] if item["dimension"] == "tool_environment")["status"] = "OK"
            write_json(root / "tool-boundary-checks.json", [{"tool_call_id": "call-a", "tool_name": "Python",
                "visible_contract_check": {"json_valid": True, "visible_schema_valid": True},
                "normalized_arguments_equal_wire": [False], "execution_boundaries": [{"toolOutput": {"status": "FAILED", "safeError": {"code": "SANDBOX_UNAVAILABLE"}}}]}])
            audit = audit_diagnosis(value, root)
            self.assertEqual(audit["status"], "REVIEW_REQUIRED")
            self.assertEqual(audit["facts"]["failed_tool_boundaries"][0]["code"], "SANDBOX_UNAVAILABLE")
            self.assertEqual(audit["facts"]["logged_normalized_argument_mismatch_ids"], ["call-a"])

    def test_diagnostic_failure_keeps_score_and_packet(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            attempt = root / "tasks/example/attempt-001"
            write_json(root / "manifest.json", {"model": "fixture"})
            result = {"status": "FINISHED", "outcome": "TASK_FAILED", "task": "example", "attempt": 1, "score": 0, "reward": 0}
            write_json(attempt / "result.json", result)
            original = (attempt / "result.json").read_bytes()
            class BrokenGateway:
                def completion(self, *_args):
                    raise RuntimeError("fixture timeout")
            packet = {"case": {"task": "example"}, "evidence": [], "evidence_gaps": []}
            with patch("nextagent_bench.analysis.build_packet", return_value=packet):
                analyze_failures(root, root, BrokenGateway(), {})
            self.assertEqual((attempt / "result.json").read_bytes(), original)
            latest = json.loads((attempt / "analysis/latest.json").read_text())
            self.assertEqual(latest["status"], "ANALYSIS_INCOMPLETE")
            self.assertTrue((Path(latest["directory"]) / "packet.json").exists())

    def test_format_repair_is_bounded_and_never_reruns_agent(self):
        for repaired in (True, False):
            with self.subTest(repaired=repaired), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                attempt = root / "tasks/example/attempt-001"
                write_json(root / "manifest.json", {"model": "fixture"})
                result = {"status": "FINISHED", "outcome": "TASK_FAILED", "task": "example", "attempt": 1, "score": 0, "reward": 0}
                write_json(attempt / "result.json", result)
                original = (attempt / "result.json").read_bytes()
                class Gateway:
                    calls = 0
                    def completion(self, *_args):
                        self.calls += 1
                        return {"content": json.dumps(diagnosis()) if self.calls == 2 and repaired else '{}'}
                gateway = Gateway()
                packet = {"case": {"task": "example"}, "evidence": [{"id": "E001", "kind": "observed_result", "location": "fixture", "content": "{}", "truncated": False}], "evidence_gaps": []}
                with patch("nextagent_bench.analysis.build_packet", return_value=packet):
                    analyze_failures(root, root, gateway, {})
                latest = json.loads((attempt / "analysis/latest.json").read_text())
                self.assertEqual(gateway.calls, 2)
                self.assertEqual(latest["status"], "SEMANTIC_ANALYSIS_COMPLETE" if repaired else "ANALYSIS_INCOMPLETE")
                self.assertTrue(Path(latest["report"]).exists())
                self.assertEqual((attempt / "result.json").read_bytes(), original)

    def test_independent_batches_cannot_each_claim_shared_quota(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = ModelGateway(root, root, {"run_id": "first"})
            second = ModelGateway(root, root, {"run_id": "second"})
            first.acquire_project_quota()
            try:
                with self.assertRaisesRegex(ValueError, "already owned"):
                    second.acquire_project_quota()
                second.close()
                self.assertTrue(first.lock.exists())
            finally:
                first.close()
            self.assertFalse(first.lock.exists())


if __name__ == "__main__":
    unittest.main()
