from __future__ import annotations

import json
from pathlib import Path


SUPPORTED_ACTIONS = {
    "assert_text",
    "check",
    "click",
    "extract_text",
    "fill",
    "goto",
    "press",
    "screenshot",
    "select_option",
    "uncheck",
    "wait_for",
}

REQUIRED_FIELDS_BY_ACTION = {
    "assert_text": {"selector", "value"},
    "click": {"selector"},
    "extract_text": {"selector", "name"},
    "fill": {"selector", "value"},
    "goto": {"url"},
    "press": {"selector", "key"},
    "screenshot": {"path"},
    "select_option": {"selector", "value"},
}


def load_config(path: str | Path) -> dict:
    config_path = Path(path)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Config root must be a JSON object.")

    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("Config must contain a non-empty 'actions' list.")

    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            raise ValueError(f"Action #{index} must be an object.")
        action_type = action.get("type")
        if action_type not in SUPPORTED_ACTIONS:
            raise ValueError(
                f"Action #{index} has unsupported type '{action_type}'. "
                f"Supported types: {', '.join(sorted(SUPPORTED_ACTIONS))}."
            )
        missing_fields = sorted(REQUIRED_FIELDS_BY_ACTION.get(action_type, set()) - action.keys())
        if missing_fields:
            raise ValueError(f"Action #{index} is missing required fields: {', '.join(missing_fields)}.")

    headless = data.get("headless", True)
    if not isinstance(headless, bool):
        raise ValueError("'headless' must be true or false when provided.")

    slow_mo = data.get("slow_mo_ms", 0)
    if not isinstance(slow_mo, int) or slow_mo < 0:
        raise ValueError("'slow_mo_ms' must be a non-negative integer.")

    return data
