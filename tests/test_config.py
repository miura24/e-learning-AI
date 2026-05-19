from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from elearning_ai.config import load_config


class LoadConfigTests(unittest.TestCase):
    def write_config(self, payload: dict) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_loads_valid_config(self) -> None:
        path = self.write_config({"headless": True, "actions": [{"type": "goto", "url": "https://example.com"}]})

        config = load_config(path)

        self.assertTrue(config["headless"])
        self.assertEqual(config["actions"][0]["type"], "goto")

    def test_rejects_unknown_action_type(self) -> None:
        path = self.write_config({"actions": [{"type": "unknown"}]})

        with self.assertRaisesRegex(ValueError, "unsupported type"):
            load_config(path)

    def test_rejects_action_missing_required_fields(self) -> None:
        path = self.write_config({"actions": [{"type": "fill", "selector": "#answer"}]})

        with self.assertRaisesRegex(ValueError, "missing required fields: value"):
            load_config(path)
