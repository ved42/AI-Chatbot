from __future__ import annotations

import logging
from typing import Optional

from backend.config.config import AppConfig

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(config: Optional[AppConfig] = None) -> None:
    """Configure Python logging for the application using centralized settings."""
    if config is None:
        config = AppConfig()

    level_name = config.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str, config: Optional[AppConfig] = None) -> logging.Logger:
    """Return a module logger, configuring logging on first access."""
    configure_logging(config=config)
    return logging.getLogger(name)
