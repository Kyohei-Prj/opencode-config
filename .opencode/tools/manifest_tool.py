#!/usr/bin/env python3
"""
manifest_tool.py — backend for all feature.yaml operations.

Usage:
  uv run python manifest_tool.py read     <path>
  uv run python manifest_tool.py write    <path> <section> <json_data>
  uv run python manifest_tool.py set      <path> <dot_path> <json_value>
  uv run python manifest_tool.py append   <path> <dot_path> <json_item>
  uv run python manifest_tool.py validate <path>

All output is JSON. On success: {"ok": true, "data": ...}
On error:   {"ok": false, "error": "..."}
"""

import sys
import json
import os

try:
    import yaml
except ImportError:
    print(
        json.dumps(
            {"ok": False, "error": "PyYAML not installed. Run: uv add --dev pyyaml"}
        )
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Safe YAML loader/dumper helpers
# ---------------------------------------------------------------------------


def load_manifest(path):
    """Load and parse feature.yaml. Returns (data, error)."""
    if not os.path.exists(path):
        return None, f"File not found: {path}"
    try:
        with open(path, "r") as f:
            content = f.read()
        # Detect and reject if empty
        if not content.strip():
            return None, "feature.yaml is empty"
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return None, "feature.yaml does not contain a YAML mapping at the top level"
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"


def dump_manifest(path, data):
    """Write data to path as YAML. Returns error or None."""
    try:
        # Write to a temp file first, then rename — atomic on POSIX
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
            )
        os.replace(tmp, path)
        return None
    except Exception as e:
        return f"Write error: {e}"


# ---------------------------------------------------------------------------
# Dot-path resolver  e.g. "execution.waves.0.status"
# ---------------------------------------------------------------------------


def get_by_path(data, dot_path):
    """Traverse data using a dot-separated path. Returns (value, error)."""
    parts = dot_path.split(".")
    node = data
    for part in parts:
        if isinstance(node, dict):
            if part not in node:
                return None, f"Key '{part}' not found at path '{dot_path}'"
            node = node[part]
        elif isinstance(node, list):
            try:
                idx = int(part)
            except ValueError:
                return (
                    None,
                    f"Expected numeric index, got '{part}' at path '{dot_path}'",
                )
            if idx < 0 or idx >= len(node):
                return (
                    None,
                    f"Index {idx} out of range (len={len(node)}) at path '{dot_path}'",
                )
            node = node[idx]
        else:
            return None, f"Cannot traverse into {type(node).__name__} at '{part}'"
    return node, None


def set_by_path(data, dot_path, value):
    """Set a value at a dot-separated path. Creates intermediate dicts. Returns error or None."""
    parts = dot_path.split(".")
    node = data
    for part in parts[:-1]:
        if isinstance(node, dict):
            if part not in node:
                node[part] = {}
            node = node[part]
        elif isinstance(node, list):
            try:
                idx = int(part)
                node = node[idx]
            except (ValueError, IndexError) as e:
                return f"Path traversal error at '{part}': {e}"
        else:
            return f"Cannot traverse into {type(node).__name__} at '{part}'"

    last = parts[-1]
    if isinstance(node, dict):
        node[last] = value
    elif isinstance(node, list):
        try:
            idx = int(last)
            if idx == len(node):
                node.append(value)
            else:
                node[idx] = value
        except ValueError:
            return f"Expected numeric index for list, got '{last}'"
    else:
        return f"Cannot set on {type(node).__name__} at '{last}'"
    return None


def append_by_path(data, dot_path, item):
    """Append an item to a list at dot_path. Returns error or None."""
    node, err = get_by_path(data, dot_path)
    if err:
        # If the path doesn't exist, try to create an empty list and set it
        err2 = set_by_path(data, dot_path, [item])
        return err2
    if not isinstance(node, list):
        return f"Target at '{dot_path}' is {type(node).__name__}, not a list"
    node.append(item)
    return None


# ---------------------------------------------------------------------------
# Validation — checks structural integrity of feature.yaml
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS_BY_STATUS = {
    "intake_complete": ["meta", "feature", "problem"],
    "shaping": ["meta", "feature", "problem"],
    "shape_complete": ["meta", "feature", "problem", "design"],
    "slicing": ["meta", "feature", "problem", "design"],
    "slice_complete": ["meta", "feature", "problem", "design", "plan"],
    "building": ["meta", "feature", "problem", "design", "plan", "execution"],
    "build_complete": ["meta", "feature", "problem", "design", "plan", "execution"],
    "verifying": [
        "meta",
        "feature",
        "problem",
        "design",
        "plan",
        "execution",
        "review",
    ],
    "verified": ["meta", "feature", "problem", "design", "plan", "execution", "review"],
    "blocked": ["meta", "feature", "problem", "design", "plan", "execution", "review"],
}


def validate_manifest(data):
    """Return list of validation error strings."""
    errors = []

    # Top-level must be a dict
    if not isinstance(data, dict):
        return ["Root is not a mapping"]

    # feature section basics
    feature = data.get("feature", {})
    if not isinstance(feature, dict):
        errors.append("feature section is not a mapping")
        return errors

    status = feature.get("status")
    if not status:
        errors.append("feature.status is missing")
    else:
        expected = REQUIRED_SECTIONS_BY_STATUS.get(status, [])
        for section in expected:
            if section not in data:
                errors.append(
                    f"Section '{section}' expected for status '{status}' but not present"
                )

    # plan.dag sanity: no cycles (simple reachability check)
    plan = data.get("plan", {})
    if isinstance(plan, dict):
        dag = plan.get("dag", {})
        if isinstance(dag, dict):
            for slug, slice_data in dag.items():
                if not isinstance(slice_data, dict):
                    errors.append(f"plan.dag.{slug} is not a mapping")
                    continue
                deps = slice_data.get("depends_on", [])
                if not isinstance(deps, list):
                    errors.append(f"plan.dag.{slug}.depends_on is not a list")
                    continue
                for dep in deps:
                    if dep not in dag:
                        errors.append(
                            f"plan.dag.{slug}.depends_on references unknown slice '{dep}'"
                        )
                if slug in deps:
                    errors.append(f"plan.dag.{slug} depends on itself")

    # execution.waves sanity
    execution = data.get("execution", {})
    if isinstance(execution, dict):
        waves = execution.get("waves", [])
        if not isinstance(waves, list):
            errors.append("execution.waves is not a list")
        else:
            for i, wave in enumerate(waves):
                if not isinstance(wave, dict):
                    errors.append(f"execution.waves[{i}] is not a mapping")
                    continue
                if "wave" not in wave:
                    errors.append(f"execution.waves[{i}] is missing 'wave' number")
                if "status" not in wave:
                    errors.append(f"execution.waves[{i}] is missing 'status'")

    return errors


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def cmd_read(args):
    if len(args) < 1:
        return {"ok": False, "error": "Usage: read <path>"}
    path = args[0]
    data, err = load_manifest(path)
    if err:
        return {"ok": False, "error": err}
    return {"ok": True, "data": data}


def cmd_write(args):
    """Write an entire top-level section. Merges into existing manifest."""
    if len(args) < 3:
        return {"ok": False, "error": "Usage: write <path> <section> <json_data>"}
    path, section, json_data = args[0], args[1], args[2]

    try:
        value = json.loads(json_data)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON data: {e}"}

    data, err = load_manifest(path)
    if err and "not found" in err:
        # New file — start from empty dict
        data = {}
    elif err:
        return {"ok": False, "error": err}

    data[section] = value
    err = dump_manifest(path, data)
    if err:
        return {"ok": False, "error": err}

    return {"ok": True, "data": f"Section '{section}' written to {path}"}


def cmd_set(args):
    """Set a specific field by dot-path."""
    if len(args) < 3:
        return {"ok": False, "error": "Usage: set <path> <dot_path> <json_value>"}
    path, dot_path, json_value = args[0], args[1], args[2]

    try:
        value = json.loads(json_value)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON value: {e}"}

    data, err = load_manifest(path)
    if err:
        return {"ok": False, "error": err}

    err = set_by_path(data, dot_path, value)
    if err:
        return {"ok": False, "error": err}

    # Always update feature.updated_at when setting any field
    import datetime

    if dot_path != "feature.updated_at":
        set_by_path(data, "feature.updated_at", datetime.date.today().isoformat())

    err = dump_manifest(path, data)
    if err:
        return {"ok": False, "error": err}

    return {"ok": True, "data": f"Set {dot_path} in {path}"}


def cmd_append(args):
    """Append an item to a list at dot-path."""
    if len(args) < 3:
        return {"ok": False, "error": "Usage: append <path> <dot_path> <json_item>"}
    path, dot_path, json_item = args[0], args[1], args[2]

    try:
        item = json.loads(json_item)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON item: {e}"}

    data, err = load_manifest(path)
    if err:
        return {"ok": False, "error": err}

    err = append_by_path(data, dot_path, item)
    if err:
        return {"ok": False, "error": err}

    import datetime

    set_by_path(data, "feature.updated_at", datetime.date.today().isoformat())

    err = dump_manifest(path, data)
    if err:
        return {"ok": False, "error": err}

    return {"ok": True, "data": f"Appended to {dot_path} in {path}"}


def cmd_validate(args):
    if len(args) < 1:
        return {"ok": False, "error": "Usage: validate <path>"}
    path = args[0]
    data, err = load_manifest(path)
    if err:
        return {"ok": False, "error": err}
    errors = validate_manifest(data)
    if errors:
        return {"ok": False, "error": "Validation failed", "errors": errors}
    return {"ok": True, "data": "Manifest is valid"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

COMMANDS = {
    "read": cmd_read,
    "write": cmd_write,
    "set": cmd_set,
    "append": cmd_append,
    "validate": cmd_validate,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "No command given. Commands: read, write, set, append, validate",
                }
            )
        )
        sys.exit(1)

    cmd = sys.argv[1]
    rest = sys.argv[2:]

    handler = COMMANDS.get(cmd)
    if not handler:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"Unknown command '{cmd}'. Commands: {list(COMMANDS)}",
                }
            )
        )
        sys.exit(1)

    result = handler(rest)
    print(json.dumps(result, default=str))
    sys.exit(0 if result.get("ok") else 1)
