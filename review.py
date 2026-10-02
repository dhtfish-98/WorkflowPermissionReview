"""Offline review of GitHub Actions workflow privileges."""

from __future__ import annotations

import yaml


def review_text(text: str) -> list[dict[str, str]]:
    try:
        workflow = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError("invalid workflow YAML") from exc
    if not isinstance(workflow, dict) or not isinstance(workflow.get("jobs"), dict):
        raise ValueError("expected a workflow with jobs mapping")
    findings = []

    def add(rule: str, location: str, note: str) -> None:
        findings.append({"rule": rule, "location": location, "note": note})

    triggers = workflow.get("on", workflow.get(True))  # YAML 1.1 parses 'on' as True.
    if isinstance(triggers, str):
        triggers = [triggers]
    trigger_names = set(triggers) if isinstance(triggers, (dict, list)) else set()
    if "pull_request_target" in trigger_names:
        add("privileged-pr-trigger", "on", "pull_request_target requires careful trust-boundary review")

    def check_permissions(value: object, location: str) -> None:
        if value is None:
            add("implicit-token-permissions", location, "No explicit token permissions declaration")
        elif value == "write-all":
            add("write-all", location, "Token receives all write permissions")
        elif isinstance(value, dict):
            for scope, access in value.items():
                if access == "write":
                    add("write-permission", f"{location}.{scope}", "Review whether this write permission is needed")
        elif value != "read-all":
            raise ValueError("unsupported permissions declaration")

    check_permissions(workflow.get("permissions"), "permissions")
    for name, job in workflow["jobs"].items():
        if not isinstance(name, str) or not isinstance(job, dict):
            raise ValueError("jobs must contain named job objects")
        if "permissions" in job:
            check_permissions(job["permissions"], f"jobs.{name}.permissions")
    return findings
