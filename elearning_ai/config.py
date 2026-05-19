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

LOCATOR_ACTIONS = {
    "assert_text",
    "check",
    "click",
    "extract_text",
    "fill",
    "press",
    "select_option",
    "uncheck",
    "wait_for",
}

REQUIRED_FIELDS_BY_ACTION = {
    "assert_text": {"value"},
    "extract_text": {"name"},
    "fill": {"value"},
    "goto": {"url"},
    "press": {"key"},
    "screenshot": {"path"},
    "select_option": {"value"},
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

        selector = action.get("selector")
        text = action.get("text")
        if selector is not None and not isinstance(selector, str):
            raise ValueError(f"Action #{index} field 'selector' must be a string.")
        if text is not None and not isinstance(text, str):
            raise ValueError(f"Action #{index} field 'text' must be a string.")

        if action_type in LOCATOR_ACTIONS:
            has_locator = bool(selector or text)
            if action_type == "wait_for" and not has_locator:
                if "duration_ms" not in action:
                    raise ValueError(
                        f"Action #{index} requires 'selector' or 'text', or a 'duration_ms' for wait_for."
                    )
            elif not has_locator:
                raise ValueError(f"Action #{index} requires 'selector' or 'text'.")

        if "nth" in action:
            nth = action["nth"]
            if not isinstance(nth, int) or nth < 0:
                raise ValueError(f"Action #{index} field 'nth' must be a non-negative integer.")

        if "exact" in action and not isinstance(action["exact"], bool):
            raise ValueError(f"Action #{index} field 'exact' must be true or false.")

        if "duration_ms" in action:
            duration = action["duration_ms"]
            if not isinstance(duration, int) or duration < 0:
                raise ValueError(f"Action #{index} field 'duration_ms' must be a non-negative integer.")

        if "timeout_ms" in action:
            timeout = action["timeout_ms"]
            if not isinstance(timeout, int) or timeout < 0:
                raise ValueError(f"Action #{index} field 'timeout_ms' must be a non-negative integer.")

    headless = data.get("headless", True)
    if not isinstance(headless, bool):
        raise ValueError("'headless' must be true or false when provided.")

    slow_mo = data.get("slow_mo_ms", 0)
    if not isinstance(slow_mo, int) or slow_mo < 0:
        raise ValueError("'slow_mo_ms' must be a non-negative integer.")

    return data
