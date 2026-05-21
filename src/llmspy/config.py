from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(os.getenv("LLM_SPY_HOME", Path.home() / ".llm-spy")).expanduser()
DEFAULT_DB_PATH = APP_DIR / "llm-spy.db"
DEFAULT_PRICING_URL = "https://raw.githubusercontent.com/llm-spy/llm-spy/main/pricing.json"


def load_environment() -> None:
    load_dotenv()


def ensure_app_dir() -> Path:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    return APP_DIR


def db_path() -> Path:
    ensure_app_dir()
    return Path(os.getenv("LLM_SPY_DB_PATH", DEFAULT_DB_PATH)).expanduser()


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}
