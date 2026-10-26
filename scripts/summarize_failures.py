"""Summarize recorded failures without model calls, reruns or score changes."""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

from nextagent_bench.util import sanitize, write_json


def review(run: Path) -> list[dict]:
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    rows = []
    for task in manifest["tasks"]:
        files = sorted((run / "tasks" / task).glob("attempt-*/result.json"))
        if not files:
            rows.append({"run": run.name, "task": task, "outcome": "NOT_STARTED", "category": "NOT_EXECUTED", "evidence": []})
            continue
        path = files[-1]
        result = json.loads(path.read_text(encoding="utf-8"))
        outcome = result.get("outcome", result.get("status"))
        code = (result.get("terminal") or {}).get("payload", {}).get("code")
        error = str(result.get("error", ""))
        evidence = [{"file": path.relative_to(run).as_posix(), "fact": f"outcome={outcome}; code={code}; phase={result.get('failed_phase')}"}]
        logs = {}
        for name in ("environment-build.log", "verifier-stdout.txt"):
            log = path.parent / name
            if log.exists():
                logs[name] = log.read_text(encoding="utf-8", errors="replace")
        build = logs.get("environment-build.log", "")
        verifier = logs.get("verifier-stdout.txt", "")
        confidence = "OBSERVED_OUTCOME_ROOT_CAUSE_UNPROVEN"
        docker = False
        if outcome == "PASSED":
            category = "PASSED"
        elif outcome == "INTERRUPTED":
            category = "INTERRUPTED_NOT_MODEL_FAILURE"
        elif outcome == "ENVIRONMENT_ERROR":
            docker = True
            if "evaluation memory budget" in error:
                category = "DOCKER_MEMORY_CAPACITY"
            elif re.search(r"registry-1\.docker\.io.*(?:EOF|timeout)|failed to do request:.*EOF", build, re.I):
                category = "DOCKER_REGISTRY_TRANSPORT"
            elif re.search(r"SSLEOFError|SSLError\(|CERTIFICATE_VERIFY_FAILED|SSL:.*EOF|ReadTimeoutError", build, re.I):
                category = "DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK"
            elif re.search(r"502\s+Bad Gateway|Unable to connect|Could not connect|Connection failed|Temporary failure resolving", build, re.I):
                category = "APT_OR_DEPENDENCY_NETWORK"
            elif re.search(r"curl: \((?:28|35|56|60)\)", build):
                category = "DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK"
            elif "timed out" in error:
                category = "BUILD_TIMEOUT_CAUSE_UNPROVEN"
            else:
                category = "ENVIRONMENT_BUILD_OR_SETUP_UNRESOLVED"
            if category not in {"BUILD_TIMEOUT_CAUSE_UNPROVEN", "ENVIRONMENT_BUILD_OR_SETUP_UNRESOLVED"}:
                confidence = "DIRECT_RECORDED_EVIDENCE"
        elif outcome == "VERIFIER_ERROR" and re.search(r"/tmp/.*(?:Permission denied|GetTempFile)|mkstemp /tmp", verifier):
            category, docker, confidence = "TMP_PERMISSION_ERROR", True, "DIRECT_RECORDED_EVIDENCE"
            proof_path = run / "maintenance/20261026-docker-repair/tmp-apt-validation/proof.json"
            if proof_path.exists():
                proof = json.loads(proof_path.read_text(encoding="utf-8"))
                if proof.get("task") == task and proof.get("status") == "SUCCEEDED":
                    category, confidence = "HARNESS_TMP_PERMISSION_REGRESSION", "REPRODUCED_AND_FIXED"
                    evidence.append({"file": proof_path.relative_to(run).as_posix(), "fact": "Repaired bridge: mode=1777; apt-get update succeeds."})
        elif code == "MODEL_AUTHENTICATION_FAILED" or "MODEL_AUTHENTICATION_FAILED" in error:
            category = "MODEL_ACCOUNT_AUTH_OR_BILLING"
        elif outcome == "PREFLIGHT_ERROR" and re.search(r'"status"\s*:\s*"INTERRUPTED"', error):
            category = "PREFLIGHT_INTERRUPTED_NOT_DIRECT_MODEL_ERROR"
        elif code == "MODEL_DUPLICATION_DETECTED":
            category = "FRAMEWORK_MODEL_DUPLICATION_INTERACTION"
        elif code in {"MODEL_PROVIDER_ERROR", "MODEL_PROVIDER_UNAVAILABLE"} or "MODEL_PROVIDER_UNAVAILABLE" in error:
            category = "MODEL_PROVIDER_OR_TRANSPORT"
        elif code == "MODEL_RESPONSE_INVALID":
            category = "MODEL_RESPONSE_PROTOCOL_OR_NORMALIZATION"
        elif outcome == "TIMEOUT":
            category = "AGENT_TIME_BUDGET_EXCEEDED"
        elif outcome == "TASK_FAILED":
            category = "VERIFIER_ASSERTIONS_NOT_MET"
        else:
            category = "FRAMEWORK_OR_HARNESS_UNRESOLVED"
        signature = re.compile(r"502\s+Bad Gateway|Unable to connect|Could not connect|Connection failed|"
                               r"SSLEOFError|SSLError\(|SSL:.*EOF|failed to do request:.*EOF|"
                               r"curl: \((?:28|35|56|60)\)|mkstemp /tmp.*|/tmp/.*Permission denied", re.I)
        for name, content in logs.items():
            matches = [(number, line) for number, line in enumerate(content.splitlines(), 1) if signature.search(line)]
            for number, line in matches[:2]:
                evidence.append({"file": (path.parent / name).relative_to(run).as_posix(),
                                 "line": number, "fact": sanitize(line[-220:])})
        rows.append({"run": run.name, "task": task, "attempt": result["attempt"], "outcome": outcome,
                     "score": result.get("score"), "reward": result.get("reward"), "terminal_code": code,
                     "failed_phase": result.get("failed_phase"), "category": category,
                     "docker_or_harness_environment": docker, "confidence": confidence,
                     "agent_budget_seconds": result.get("budgets", {}).get("agent_timeout"),
                     "agent_seconds": result.get("phase_seconds", {}).get("agent"),
                     "failed_tests": result.get("verifier", {}).get("failed_tests", []), "evidence": evidence})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args()
    runs = [p.resolve() for p in args.runs]
    rows = [row for run in runs for row in review(run)]
    output = runs[0] / "failure-review"
    summaries = {run.name: {"latest_outcomes": dict(collections.Counter(r["outcome"] for r in rows if r["run"] == run.name)),
                            "categories": dict(collections.Counter(r["category"] for r in rows if r["run"] == run.name))} for run in runs}
    write_json(output / "summary.json", {"runs": summaries, "tasks": rows,
               "scope": "Latest attempts per run. Reruns are shown separately; original scores are not replaced.",
               "limits": "Classification follows recorded evidence. A terminal code does not prove a model or framework root cause. Timeout-only builds are not automatically labelled network failures."})
    lines = ["# 历史评测失败原因汇总", "", "仅分析现有证据，不调用模型、不重跑 Agent、不改评分。各批次分别统计，补测不替换原首测。", ""]
    labels = {
        "APT_OR_DEPENDENCY_NETWORK": "软件源或依赖下载连接失败/502",
        "DEPENDENCY_DOWNLOAD_TLS_OR_NETWORK": "依赖下载 TLS/EOF/连接中断",
        "DOCKER_REGISTRY_TRANSPORT": "Docker 镜像仓库传输失败",
        "BUILD_TIMEOUT_CAUSE_UNPROVEN": "构建超时；具体根因未证实",
        "DOCKER_MEMORY_CAPACITY": "题目内存声明超过 Docker 调度容量",
        "HARNESS_TMP_PERMISSION_REGRESSION": "评测器迁移 /tmp 丢失权限；已复现并修复",
        "TMP_PERMISSION_ERROR": "/tmp 权限错误；责任方未定",
        "MODEL_ACCOUNT_AUTH_OR_BILLING": "模型账号鉴权/欠费影响",
        "MODEL_PROVIDER_OR_TRANSPORT": "模型服务或传输异常",
        "FRAMEWORK_MODEL_DUPLICATION_INTERACTION": "框架与模型重复输出处理交互",
        "MODEL_RESPONSE_PROTOCOL_OR_NORMALIZATION": "模型返回协议/框架归一化问题待查",
        "AGENT_TIME_BUDGET_EXCEEDED": "Agent 执行超时",
        "VERIFIER_ASSERTIONS_NOT_MET": "输出未满足原验证器断言",
        "PREFLIGHT_INTERRUPTED_NOT_DIRECT_MODEL_ERROR": "预检被中断；不能当作模型直接失败",
        "FRAMEWORK_OR_HARNESS_UNRESOLVED": "框架或评测器异常，根因待查",
        "INTERRUPTED_NOT_MODEL_FAILURE": "执行中断；不记为模型答错",
        "NOT_EXECUTED": "未启动",
        "PASSED": "验证通过",
    }
    for run, summary in summaries.items():
        lines += [f"## {run}", "", "| 原因类别 | 数量 |", "|---|---:|"]
        lines += [f"| {labels.get(kind, kind)} (`{kind}`) | {count} |" for kind, count in sorted(summary["categories"].items())]
        lines.append("")
    lines += ["## 逐题证据", "", "重复输出属于框架检测与模型输出的交互现象，不能仅凭错误码判定单方责任；验证器断言失败和 Agent 超时也不自动归为 Docker 问题。", "",
              "| 批次 | 任务 | 状态 | 分数 | 原因类别 | 可核验记录 |", "|---|---|---|---:|---|---|"]
    for row in rows:
        if row["category"] == "PASSED":
            continue
        refs = "; ".join(f"{v['file']}" + (f":{v['line']}" if "line" in v else "") for v in row["evidence"])
        lines.append(f"| {row['run']} | {row['task']} | {row['outcome']} | {row.get('score') if row.get('score') is not None else ''} | {row['category']} | {refs} |")
    lines += ["", "带行号的简短错误证据、失败测试名、时限和归因置信范围见 summary.json。完整 prompt、reasoning 和轨迹正文不写入此汇总。", ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"output": str(output), "runs": summaries}, ensure_ascii=False))


if __name__ == "__main__":
    main()
