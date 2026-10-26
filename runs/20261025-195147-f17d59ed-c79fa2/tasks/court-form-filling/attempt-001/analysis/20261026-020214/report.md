# 分析未完成，需要核验

Diagnostic request failed: HTTP_401

Evidence packet retained where available; no unsupported root cause asserted. Retry diagnostics without rerunning the task.

原始回复见本目录 model-response.json / format-repair-response.json；不可把格式未验证的内容当作已证实根因。

## 已保存证据

- E001 / observed_result: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\result.json
- E002 / effective_task: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\agent-facing\prompt.txt
- E003 / path_and_skill_plan: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\agent-facing\adaptation.json
- E004 / physical_path_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\path-bridge.json
- E005 / effective_runtime_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\bootstrap.json
- E006 / skill_discovery: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\skill-discovery.json
- E007 / verifier_assertions: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\ctrf.json
- E008 / verifier_output: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\verifier-stdout.txt
- E009 / startup_evidence: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\runtime\na-start.log
- E010 / provided_skill_document: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\agent-facing\skills\pdf\SKILL.md
- E011 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\default-system.yaml
- E012 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\agent.yaml
- E013 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\changes.json
- E014 / frozen_configuration: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\config\quota.json
- E015 / canonical_execution_timeline: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\trajectory.jsonl
- E016 / framework_model_and_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\nextagent-home\logs
- E017 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/faa16c42fce741b1a256d36d9a5d285b/request.json
- E018 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/faa16c42fce741b1a256d36d9a5d285b/request.json
- E019 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/faa16c42fce741b1a256d36d9a5d285b/
- E020 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/8baf413b7d734c99b2683367f80eb36c/request.json
- E021 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/8baf413b7d734c99b2683367f80eb36c/request.json
- E022 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/8baf413b7d734c99b2683367f80eb36c/
- E023 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/bd7a03c5df4a411b968d3b1aa31de836/request.json
- E024 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/bd7a03c5df4a411b968d3b1aa31de836/request.json
- E025 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/bd7a03c5df4a411b968d3b1aa31de836/
- E026 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/2f77361cf45a4de69de068a9bc889378/request.json
- E027 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/2f77361cf45a4de69de068a9bc889378/request.json
- E028 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/2f77361cf45a4de69de068a9bc889378/
- E029 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/9619245e46b14924aefdc9dfe02f90cc/request.json
- E030 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/9619245e46b14924aefdc9dfe02f90cc/request.json
- E031 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/9619245e46b14924aefdc9dfe02f90cc/
- E032 / actual_model_request: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/57ae8740d1334dd19472d52051f2468e/request.json
- E033 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/57ae8740d1334dd19472d52051f2468e/request.json
- E034 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\model-gateway\20261025-200449-ca2847\exchanges.tar!evidence/court-form-filling/attempt-1/57ae8740d1334dd19472d52051f2468e/
- E035 / joined_tool_boundaries: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\tool-boundary-checks.json
- E036 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\helper.mjs
- E037 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\adapter-upgrades\4f5d50753f4f23abc988562533a0deb321ea508210f2a493c734457a39d64064\source\runtime\start.mjs
- E038 / operator_concurrency_history: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\concurrency-history.jsonl
- E039 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-platform-gateway-local/dist/sandbox/restricted-local-sandbox.js
- E040 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/workspace-files/path-security.js
- E041 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/providers/openai-compatible/response-handling.js
- E042 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/invocation/failure-recovery.js
- E043 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/skill-tool.js
- E044 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/python/python-tool.js
- E045 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\court-form-filling\verifier\test_outputs.py
- E046 / workspace_artifact_inventory: C:\Project\nextagent-bench\runs\20261025-195147-f17d59ed-c79fa2\tasks\court-form-filling\attempt-001\nextagent-home.tar
