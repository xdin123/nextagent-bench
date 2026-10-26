# adaptive-cruise-control / attempt 1

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

Observed terminal code: `MODEL_PROVIDER_ERROR`. Terminal sequence: 124.
Failed verifier cases: test_outputs.py::TestPIDController::test_pid_controller, test_outputs.py::TestACCSystem::test_acc_system, test_outputs.py::TestTuningResults::test_tuning_results, test_outputs.py::TestSimulationResults::test_simulation_results, test_outputs.py::TestReport::test_report_keywords, test_outputs.py::TestSpeedControl::test_speed_control, test_outputs.py::TestDistanceControl::test_distance_control, test_outputs.py::TestSafety::test_safety, test_outputs.py::TestScenario::test_scenario, test_outputs.py::TestSimulationExecution::test_simulation_execution, test_outputs.py::TestAntiCheat::test_anti_cheat
Root cause is not established by this automatic summary. Distinguish task assertions, framework execution, model/provider evidence and harness/environment errors before assigning responsibility.
