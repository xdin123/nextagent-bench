from __future__ import annotations

import copy
import math
from pathlib import Path

import yaml

from .util import digest, fs_path, read_document

HOME = "/opt/na-eval/home"
PORT = 31872


def load_task(path: Path) -> dict:
    text = fs_path(path / "task.md").read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        raise ValueError(f"Missing task frontmatter: {path}")
    front = yaml.safe_load(text.split("---", 2)[1])
    if not isinstance(front, dict):
        raise ValueError(f"Invalid task frontmatter: {path}")
    agent, verifier, sandbox = (front.get(name) or {} for name in ("agent", "verifier", "sandbox"))
    values = {"task": path.name, "agent_timeout": agent.get("timeout_sec", 3600),
              "verifier_timeout": verifier.get("timeout_sec", 900), "build_timeout": sandbox.get("build_timeout_sec", 1800),
              "cpus": sandbox.get("cpus", 1), "memory_mb": sandbox.get("memory_mb", 4096),
              "storage_mb": sandbox.get("storage_mb"), "gpus": sandbox.get("gpus", 0),
              "network_mode": sandbox.get("network_mode", "public"), "verifier_service": verifier.get("service", "main")}
    for key in ("agent_timeout", "verifier_timeout", "build_timeout", "cpus", "memory_mb"):
        value = float(values[key])
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Invalid {key} in {path}")
        values[key] = value if key == "cpus" else math.ceil(value)
    return values


def effective_configs(system: dict, agent: dict) -> tuple[dict, dict, list[dict]]:
    system, agent = copy.deepcopy(system), copy.deepcopy(agent)
    changes = []

    def set_value(parent, key, value, location):
        if parent.get(key) != value:
            changes.append({"field": location, "before": parent.get(key), "after": value,
                            "reason": "Isolated evaluation paths / internal HTTP transport"})
            parent[key] = value

    for key, value in {"workspaceRoot": "workspaces", "logRoot": "logs", "skillRoot": "skills", "agentRoot": "agents"}.items():
        set_value(system.setdefault("paths", {}), key, value, "paths." + key)
    channel = system.setdefault("channel", {})
    for key, value in {"host": "127.0.0.1", "port": PORT, "routePrefix": "/"}.items():
        set_value(channel.setdefault("web", {}), key, value, "channel.web." + key)
    set_value(channel.setdefault("auth", {}), "mode", "none", "channel.auth.mode")
    agent_id = agent.get("agentId")
    if not isinstance(agent_id, str) or not agent_id or "/" in agent_id or ".." in agent_id:
        raise ValueError("Invalid agentId in the agent template")
    set_value(system.setdefault("agents", {}), "activeAgentId", agent_id, "agents.activeAgentId")
    if system.get("deployment", {}).get("mode", "LOCAL") != "LOCAL":
        raise ValueError("This evaluation profile requires LOCAL Gateway")
    return system, agent, changes


def load_settings(root: Path) -> dict:
    config = read_document(root / "evaluation.yaml")
    system = read_document(root / "profiles" / "default-system.yaml")
    agent = read_document(root / "profiles" / "agent.yaml")
    system, agent, changes = effective_configs(system, agent)
    if not config.get("model") or not config.get("base_url"):
        raise ValueError("Set model and base_url in evaluation.yaml")
    config["effective_system"], config["effective_agent"], config["config_changes"] = system, agent, changes
    profiles = system.get("models", {}).get("profiles", [])
    if len(profiles) != 1 or len(profiles[0].get("models", [])) != 1:
        raise ValueError("The evaluation profile must select one provider/model explicitly")
    provider = profiles[0]
    declared_model = provider["models"][0].get("modelId")
    declared_url = provider.get("baseUrl")
    if provider.get("credentialRef") != "env:OPENAI_API_KEY":
        raise ValueError("Use env:OPENAI_API_KEY in the evaluation model profile")
    if declared_model != "env:OPENAI_MODEL_NAME":
        config["model"] = declared_model
    if declared_url != "env:OPENAI_BASE_URL":
        config["base_url"] = declared_url
    if not config["model"] or not config["base_url"] or str(config["model"]).startswith("env:") or str(config["base_url"]).startswith("env:"):
        raise ValueError("Model/base URL must be a literal or the documented OPENAI environment reference")
    path_policy = read_document(root / "profiles" / "path-mappings.yaml")
    quota = read_document(root / "profiles" / "model-quota.yaml")
    if quota.get("shared_account") is not True:
        raise ValueError("This credential pool uses the confirmed shared account/project quota")
    for key in ("max_concurrency", "max_attempts", "max_wait_seconds", "upstream_idle_timeout_seconds"):
        if not isinstance(quota.get(key), (int, float)) or isinstance(quota[key], bool) or not math.isfinite(quota[key]) or quota[key] <= 0:
            raise ValueError("Invalid shared quota: " + key)
    for key in ("max_concurrency", "max_attempts"):
        if not isinstance(quota[key], int):
            raise ValueError("Integer required for shared quota: " + key)
    for key in ("requests_per_minute", "tokens_per_minute"):
        if quota.get(key) is not None and (not isinstance(quota[key], int) or quota[key] <= 0):
            raise ValueError("Set a positive known limit or null: " + key)
    if not isinstance(quota.get("min_interval_seconds"), (int, float)) or not math.isfinite(quota["min_interval_seconds"]) or quota["min_interval_seconds"] < 0:
        raise ValueError("Invalid shared quota min_interval_seconds")
    config["path_policy"] = path_policy
    config["quota"] = quota
    config["analysis"] = read_document(root / "profiles" / "analysis.yaml")
    config["profile_sha"] = digest({"system": system, "agent": agent, "changes": changes, "path_policy": path_policy, "quota": quota})
    return config
