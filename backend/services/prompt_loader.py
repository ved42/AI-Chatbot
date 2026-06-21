from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from backend.config.config import AppConfig
from backend.utils.logger import get_logger


class PromptLoader:
    """Utility to load and render prompt templates from YAML files."""

    def __init__(self, config: Optional[AppConfig] = None, logger: Optional[Any] = None) -> None:
        self.config = config or AppConfig()
        self.logger = logger or get_logger(__name__, config=self.config)
        self.prompt_root = Path(__file__).parent

    def load_yaml(self, prompt_file: str) -> Dict[str, Any]:
        """Load a YAML prompt file and return its contents."""
        prompt_path = self.prompt_root / prompt_file
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with prompt_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        if not isinstance(data, dict):
            raise ValueError(f"Prompt file must contain a mapping at top level: {prompt_path}")
        return data

    def get_prompt(self, prompt_file: str, prompt_key: str) -> str:
        """Fetch a specific prompt string from a YAML prompt file."""
        data = self.load_yaml(prompt_file)
        prompt_value = data.get(prompt_key)
        if prompt_value is None:
            raise KeyError(f"Prompt key '{prompt_key}' not found in {prompt_file}")
        if not isinstance(prompt_value, str):
            raise ValueError(f"Prompt '{prompt_key}' must be a string in {prompt_file}")
        return prompt_value

    def render(self, prompt: str, **context: Any) -> str:
        """Render prompt variables using Python formatting syntax."""
        try:
            return prompt.format(**context)
        except KeyError as exc:
            missing = exc.args[0]
            raise ValueError(f"Missing prompt context for key: {missing}") from exc

    def load_and_render(self, prompt_file: str, prompt_key: str, **context: Any) -> str:
        """Load a prompt by key from YAML and render it with provided context."""
        prompt = self.get_prompt(prompt_file, prompt_key)
        return self.render(prompt, **context)
