"""e-learning browser automation package."""

from .config import load_config
from .runner import run_automation

__all__ = ["load_config", "run_automation"]
