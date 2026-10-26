# 分析未完成，需要核验

Diagnostic request failed: ANALYSIS_TRANSPORT_OR_PROTOCOL_ERROR

Evidence packet retained where available; no unsupported root cause asserted. Retry diagnostics without rerunning the task.

原始回复见本目录 model-response.json / format-repair-response.json；不可把格式未验证的内容当作已证实根因。

## 已保存证据

- E001 / observed_result: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\result.json
- E002 / effective_task: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\agent-facing\prompt.txt
- E003 / path_and_skill_plan: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\agent-facing\adaptation.json
- E004 / physical_path_evidence: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\path-bridge.json
- E005 / effective_runtime_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\bootstrap.json
- E006 / skill_discovery: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\skill-discovery.json
- E007 / verifier_assertions: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\ctrf.json
- E008 / verifier_output: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\verifier-stdout.txt
- E009 / startup_evidence: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\runtime\na-start.log
- E010 / provided_skill_document: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\agent-facing\skills\ada-plan-view-accessibility\SKILL.md
- E011 / provided_skill_document: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\agent-facing\skills\architectural-dxf-extraction\SKILL.md
- E012 / provided_skill_document: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\agent-facing\skills\geometric-layout-repair\SKILL.md
- E013 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\default-system.yaml
- E014 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\agent.yaml
- E015 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\changes.json
- E016 / frozen_configuration: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\config\quota.json
- E017 / canonical_execution_timeline: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\trajectory.jsonl
- E018 / framework_model_and_tool_boundaries: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home\logs
- E019 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/84027f59512c40a4a6aa5d04caa1df6a/request.json
- E020 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/84027f59512c40a4a6aa5d04caa1df6a/request.json
- E021 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/84027f59512c40a4a6aa5d04caa1df6a/
- E022 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/5f5cb9bfbcaa4199af6864abc3b22662/request.json
- E023 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/5f5cb9bfbcaa4199af6864abc3b22662/request.json
- E024 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/5f5cb9bfbcaa4199af6864abc3b22662/
- E025 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/6c5c42b51c404215a18ec61733955542/request.json
- E026 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/6c5c42b51c404215a18ec61733955542/request.json
- E027 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/6c5c42b51c404215a18ec61733955542/
- E028 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/6723b75d5da549ea98a9165a989dc976/request.json
- E029 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/6723b75d5da549ea98a9165a989dc976/request.json
- E030 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/6723b75d5da549ea98a9165a989dc976/
- E031 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/8c10721c9b564534815095576c9778b2/request.json
- E032 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/8c10721c9b564534815095576c9778b2/request.json
- E033 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/8c10721c9b564534815095576c9778b2/
- E034 / actual_model_request: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/693f8146d56f458999fa7fa91bc69f10/request.json
- E035 / model_visible_instruction_focus: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/693f8146d56f458999fa7fa91bc69f10/request.json
- E036 / provider_fragments_and_contract_checks: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\model-gateway\20261026-161540-c4ca5a\exchanges.tar!evidence/ada-bathroom-plan-repair/attempt-1/693f8146d56f458999fa7fa91bc69f10/
- E037 / joined_tool_boundaries: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\tool-boundary-checks.json
- E038 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\adapter-source\runtime\helper.mjs
- E039 / frozen_harness_code: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\adapter-source\runtime\start.mjs
- E040 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-platform-gateway-local/dist/sandbox/restricted-local-sandbox.js
- E041 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-capability/dist/builtins/workspace-files/path-security.js
- E042 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/duplication-detection/controller.js
- E043 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/duplication-detection/detection.js
- E044 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/providers/openai-compatible/response-handling.js
- E045 / executed_framework_code: C:\Project\nextagent-bench\artifacts\f17d59ed60bb55878db65750eee6cc591efe52c97351fb2c1ed850f9ff6b75a5\bundle.tar.gz!node_modules/@nextagent/agent-model/dist/invocation/failure-recovery.js
- E046 / original_verifier_code: C:\Project\nextagent-bench\datasets\c44fb04745607db4d1c0b07a945ec3fbdfaa2bd955ae172667aaa7edc95b4ae2\tasks\ada-bathroom-plan-repair\verifier\test_outputs.py
- E047 / workspace_artifact_inventory: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar
- E048 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/input/ada_rules.json
- E049 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/input/layer_schema.json
- E050 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/output_schema/changes_schema.json
- E051 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/output_schema/extracted_original_layout_schema.json
- E052 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/output_schema/layer_inventory_schema.json
- E053 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/output_schema/repaired_layout_schema.json
- E054 / actual_artifact_content: C:\Project\nextagent-bench\runs\20261026-161356-f17d59ed-b0c82d\tasks\ada-bathroom-plan-repair\attempt-001\nextagent-home.tar!home/workspaces/execution/4d1687d33cec49be/workspace/output_schema/violations_before_schema.json
