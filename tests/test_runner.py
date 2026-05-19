from __future__ import annotations

import os
import unittest

from elearning_ai.runner import ActionRunner, expand_placeholders


class FakeLocator:
    def __init__(self, page, selector: str):
        self.page = page
        self.selector = selector

    def fill(self, value: str) -> None:
        self.page.operations.append(("fill", self.selector, value))

    def click(self) -> None:
        self.page.operations.append(("click", self.selector))

    def press(self, key: str) -> None:
        self.page.operations.append(("press", self.selector, key))

    def select_option(self, value: str) -> None:
        self.page.operations.append(("select_option", self.selector, value))

    def check(self) -> None:
        self.page.operations.append(("check", self.selector))

    def uncheck(self) -> None:
        self.page.operations.append(("uncheck", self.selector))

    def wait_for(self, state: str, timeout: int) -> None:
        self.page.operations.append(("wait_for", self.selector, state, timeout))

    def inner_text(self) -> str:
        return self.page.text_by_selector[self.selector]


class FakePage:
    def __init__(self):
        self.operations: list[tuple] = []
        self.text_by_selector: dict[str, str] = {}

    def goto(self, url: str, wait_until: str) -> None:
        self.operations.append(("goto", url, wait_until))

    def wait_for_timeout(self, duration_ms: int) -> None:
        self.operations.append(("wait_for_timeout", duration_ms))

    def screenshot(self, path: str, full_page: bool) -> None:
        self.operations.append(("screenshot", path, full_page))

    def locator(self, selector: str) -> FakeLocator:
        return FakeLocator(self, selector)


class ActionRunnerTests(unittest.TestCase):
    def test_expand_placeholders_uses_context_before_environment(self) -> None:
        os.environ["E_LEARNING_USERNAME"] = "env-user"
        self.addCleanup(os.environ.pop, "E_LEARNING_USERNAME", None)

        result = expand_placeholders("${E_LEARNING_USERNAME}", {"E_LEARNING_USERNAME": "context-user"})

        self.assertEqual("context-user", result)

    def test_run_executes_and_extracts_values(self) -> None:
        page = FakePage()
        page.text_by_selector[".assignment"] = "Reading Task"
        runner = ActionRunner(page, output_dir="/tmp")

        results = runner.run(
            [
                {"type": "goto", "url": "https://example.com"},
                {"type": "extract_text", "selector": ".assignment", "name": "assignment_title"},
                {"type": "fill", "selector": "textarea.answer", "value": "Answer for ${assignment_title}"},
                {"type": "assert_text", "selector": ".assignment", "value": "Reading"},
            ]
        )

        self.assertEqual({"assignment_title": "Reading Task"}, results)
        self.assertIn(("goto", "https://example.com", "load"), page.operations)
        self.assertIn(("fill", "textarea.answer", "Answer for Reading Task"), page.operations)

    def test_wait_for_uses_timeout_when_selector_missing(self) -> None:
        page = FakePage()
        runner = ActionRunner(page)

        runner.run([{"type": "wait_for", "duration_ms": 250}])

        self.assertEqual([("wait_for_timeout", 250)], page.operations)
