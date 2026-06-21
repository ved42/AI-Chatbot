from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Optional, Type

import google.genai as genai
from google.genai import Client
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel

from backend.config.config import AppConfig
from backend.utils.logger import get_logger


class LLMService:
    """Centralized wrapper for Gemini LLM calls with retry and configuration support."""

    def __init__(self, config: AppConfig, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.logger = logger or get_logger(__name__, config=config)
        self.client = Client(api_key=self.config.gemini_api_key)
        self.logger.debug("Gemini client configured with model %s.", self.config.gemini_model)

    def _build_generation_config(
        self,
        response_mime_type: str = "text",
        response_schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> GenerateContentConfig:
        config = GenerateContentConfig(
            systemInstruction=kwargs.get("system_prompt"),
            temperature=kwargs.get("temperature", self.config.gemini_temperature),
            top_p=kwargs.get("top_p", self.config.gemini_top_p),
            top_k=kwargs.get("top_k", self.config.gemini_top_k),
            max_output_tokens=kwargs.get("max_output_tokens", self.config.gemini_max_output_tokens),
        )

        if response_schema is not None:
            config.response_schema = response_schema

        return config

    def _execute_with_retry(self, callable_fn: Any, *args: Any, **kwargs: Any) -> Any:
        attempts = 0
        while True:
            try:
                attempts += 1
                return callable_fn(*args, **kwargs)
            except Exception as exc:
                self.logger.warning(
                    "LLM request failed on attempt %d/%d: %s",
                    attempts,
                    self.config.model_retry_attempts + 1,
                    exc,
                )
                if attempts > self.config.model_retry_attempts:
                    self.logger.error("Maximum Gemini retry attempts reached.")
                    raise
                backoff = self.config.model_retry_backoff_seconds * attempts
                time.sleep(backoff)

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **overrides: Any,
    ) -> str:
        """Generate text output from Gemini using a prompt."""
        generation_config = self._build_generation_config(response_mime_type="text", system_prompt=system_prompt, **overrides)

        response = self._execute_with_retry(
            self.client.models.generate_content,
            model=self.config.gemini_model,
            contents=prompt,
            config=generation_config,
        )

        if hasattr(response, "text"):
            return response.text

        return str(response)

    def generate_json(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_prompt: Optional[str] = None,
        **overrides: Any,
    ) -> BaseModel:
        """Generate JSON output from Gemini and validate it against a Pydantic schema."""
        generation_config = self._build_generation_config(
            response_mime_type="application/json",
            response_schema=response_schema,
            system_prompt=system_prompt,
            **overrides,
        )

        response = self._execute_with_retry(
            self.client.models.generate_content,
            model=self.config.gemini_model,
            contents=prompt,
            config=generation_config,
        )

        if hasattr(response, "text"):
            return response_schema.model_validate_json(response.text)

        return response_schema.model_validate(response)

    async def generate_text_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **overrides: Any,
    ) -> str:
        """Async wrapper for generate_text to avoid blocking an event loop."""
        return await asyncio.to_thread(self.generate_text, prompt, system_prompt, **overrides)

    async def generate_json_async(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_prompt: Optional[str] = None,
        **overrides: Any,
    ) -> BaseModel:
        """Async wrapper for generate_json to avoid blocking an event loop."""
        return await asyncio.to_thread(
            self.generate_json,
            prompt,
            response_schema,
            system_prompt,
            **overrides,
        )
