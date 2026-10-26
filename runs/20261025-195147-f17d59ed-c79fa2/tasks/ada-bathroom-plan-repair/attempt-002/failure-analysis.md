# ada-bathroom-plan-repair / attempt 2

Outcome: EXECUTION_FAILED
End-to-end score: 0; verifier reward: 0.0
Model: qwen3.8-27b; framework: f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5

## Evidence

- result.json: phase, terminal, budgets, timings and collection status.
- agent-facing/adaptation.json and adaptation.patch: exact path changes; verifier unchanged.
- skill-catalog.json + skill-discovery.json: discoverability; trajectory.jsonl: actual Skill invocation and loading.
- nextagent-home.tar: complete POSIX execution workspace, persistent state and framework logs; nextagent-home/logs/: readable log copy.
- ctrf.json, reward.txt and verifier-stdout.txt: original scoring evidence.

## Finding

Observed terminal code: `MODEL_DUPLICATION_DETECTED`. Terminal sequence: 182.
Failed verifier cases: test_outputs.py::TestAdaBathroomRepairOutputs::test_required_outputs_are_valid_json_and_match_schemas, test_outputs.py::TestAdaBathroomRepairOutputs::test_layer_inventory_and_original_extraction_match_cad, test_outputs.py::TestAdaBathroomRepairOutputs::test_violation_list_is_consistent_with_plan_view_rules, test_outputs.py::TestAdaBathroomRepairOutputs::test_repaired_layout_satisfies_accessibility_rules, test_outputs.py::TestAdaBathroomRepairOutputs::test_repaired_dxf_is_modified_and_matches_repaired_layout, test_outputs.py::TestAdaBathroomRepairOutputs::test_repair_preserves_the_existing_layout_reasonably
This code can originate from NextAgent's local duplication detector. It does not prove HTTP 429 or provider overload. Inspect model invocation and duplication details; no provider root cause is asserted here.
