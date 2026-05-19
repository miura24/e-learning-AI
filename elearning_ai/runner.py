from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


PLACEHOLDER_PATTERN = re.compile(r"\$\{([^}]+)\}")


def expand_placeholders(value: str | None, context: dict[str, str]) -> str | None:
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in context:
            return str(context[key])
        if key in os.environ:
            return os.environ[key]
        raise KeyError(f"Placeholder '{key}' was not found in extracted values or environment.")

    return PLACEHOLDER_PATTERN.sub(replace, value)


class ActionRunner:
    def __init__(self, page: Any, output_dir: str | Path | None = None):
        self.page = page
        self.output_dir = Path(output_dir) if output_dir else None

    def resolve_locator(self, action: dict[str, Any], context: dict[str, str]):
        selector = action.get("selector")
        if selector:
            selector = expand_placeholders(selector, context)
            locator = self.page.locator(selector)
        else:
            text = expand_placeholders(action.get("text"), context)
            locator = self.page.get_by_text(text, exact=action.get("exact", False))

        nth = action.get("nth")
        if nth is not None:
            locator = locator.nth(nth)
        return locator

    def run(self, actions: list[dict[str, Any]]) -> dict[str, str]:
        context: dict[str, str] = {}
        for action in actions:
            self.run_action(action, context)
        return context

    def run_action(self, action: dict[str, Any], context: dict[str, str]) -> None:
        action_type = action["type"]

        if action_type == "goto":
            self.page.goto(expand_placeholders(action["url"], context), wait_until=action.get("wait_until", "load"))
            return

        if action_type == "wait_for":
            if "selector" in action or "text" in action:
                locator = self.resolve_locator(action, context)
                locator.wait_for(
                    state=action.get("state", "visible"),
                    timeout=action.get("timeout_ms", 30_000),
                )
            else:
                self.page.wait_for_timeout(action.get("duration_ms", 1_000))
            return

        if action_type == "screenshot":
            path = Path(expand_placeholders(action["path"], context))
            if self.output_dir and not path.is_absolute():
                path = self.output_dir / path
            path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(path), full_page=action.get("full_page", True))
            return

        locator = self.resolve_locator(action, context)

        if action_type == "click":
            locator.click()
        elif action_type == "fill":
            locator.fill(expand_placeholders(action["value"], context))
        elif action_type == "press":
            locator.press(expand_placeholders(action["key"], context))
        elif action_type == "select_option":
            locator.select_option(expand_placeholders(action["value"], context))
        elif action_type == "check":
            locator.check()
        elif action_type == "uncheck":
            locator.uncheck()
        elif action_type == "extract_text":
            context[action["name"]] = locator.inner_text().strip()
        elif action_type == "assert_text":
            expected = expand_placeholders(action["value"], context)
            actual = locator.inner_text()
            if expected not in actual:
                raise AssertionError(f"Expected '{expected}' to be contained in '{actual}'.")
        else:
            raise ValueError(f"Unsupported action type '{action_type}'.")


def run_automation(
    config: dict[str, Any], output_dir: str | Path | None = None, *, headed_override: bool | None = None
) -> dict[str, str]:
    from playwright.sync_api import sync_playwright

    headless = config.get("headless", True)
    if headed_override is not None:
        headless = not headed_override

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless, slow_mo=config.get("slow_mo_ms", 0))
        context = browser.new_context()
        page = context.new_page()
        extracted = ActionRunner(page, output_dir=output_dir).run(config["actions"])
        browser.close()
        return extracted


def format_results(results: dict[str, str]) -> str:
    return json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True)
