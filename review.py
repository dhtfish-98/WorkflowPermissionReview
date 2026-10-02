"""Offline review of GitHub Actions workflow privileges."""
from __future__ import annotations
import re
import yaml


class WorkflowLoader(yaml.SafeLoader):
    """Keep event names as strings and reject duplicate mapping keys."""
    yaml_implicit_resolvers = {
        key: [(tag, pattern) for tag, pattern in rules if tag != "tag:yaml.org,2002:bool"]
        for key, rules in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key, value in self.construct_pairs(node, deep=deep):
            try:
                if key in mapping:
                    raise ValueError("duplicate workflow key")
                mapping[key] = value
            except TypeError as exc:
                raise ValueError("workflow mapping keys must be scalar") from exc
        return mapping


WorkflowLoader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), list("tTfF"))


def review_text(text: str) -> list[dict[str, str]]:
    try:
        workflow = yaml.load(text, Loader=WorkflowLoader)
    except (yaml.YAMLError, ValueError, RecursionError) as exc:
        raise ValueError("invalid or ambiguous workflow YAML") from exc
    if not isinstance(workflow, dict) or not isinstance(workflow.get("jobs"), dict) or not workflow["jobs"]:
        raise ValueError("expected a workflow with named jobs")
    triggers = workflow.get("on")
    if isinstance(triggers, str) and triggers:
        trigger_names = [triggers]
    elif isinstance(triggers, (dict, list)) and triggers and all(isinstance(name, str) and name for name in triggers):
        trigger_names = list(triggers)
    else:
        raise ValueError("on must contain event names")
    findings = []
    def add(rule, location, note):
        findings.append({"rule": rule, "location": location, "note": note})
    if "pull_request_target" in trigger_names:
        add("privileged-pr-trigger", "on", "pull_request_target requires careful trust-boundary review")

    def check_permissions(value, location):
        if value == "write-all":
            add("write-all", location, "Token receives all write permissions")
        elif value == "read-all":
            return
        elif isinstance(value, dict):
            for scope, access in value.items():
                if not isinstance(scope, str) or not scope or not isinstance(access, str) or access not in ("read", "write", "none"):
                    raise ValueError("invalid permission scope or access value")
                if access == "write":
                    add("write-permission", f"{location}.{scope}", "Review whether this write permission is needed")
        else:
            raise ValueError("unsupported permissions declaration")

    if "permissions" in workflow:
        check_permissions(workflow["permissions"], "permissions")
    for name, job in workflow["jobs"].items():
        if not isinstance(name, str) or not name or not isinstance(job, dict):
            raise ValueError("jobs must contain named job objects")
        if "permissions" in job:
            check_permissions(job["permissions"], f"jobs.{name}.permissions")
        elif "permissions" not in workflow:
            add("implicit-token-permissions", f"jobs.{name}.permissions", "Job inherits unspecified repository token defaults")
    return findings
