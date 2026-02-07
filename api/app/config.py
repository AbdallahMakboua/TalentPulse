"""Application configuration loaded from environment / .env."""

from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


def _find_env_file() -> str:
    """Locate .env in current dir, parent, or project root."""
    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return ".env"


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://talentpulse:talentpulse_secret@db:5432/talentpulse"
    database_url_sync: str = "postgresql://talentpulse:talentpulse_secret@db:5432/talentpulse"

    # ── API ─────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "change-me-in-production"

    # ── Ollama (local LLM) ─────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 60

    # ── Mode ────────────────────────────────────────────────────────
    demo_mode: bool = True

    # ── Microsoft Graph (optional) ─────────────────────────────────
    graph_tenant_id: str = ""
    graph_client_id: str = ""
    graph_client_secret: str = ""
    enable_graph_ingestion: bool = False

    # ── Privacy ─────────────────────────────────────────────────────
    data_retention_days: int = 90
    working_hours_start: int = 9
    working_hours_end: int = 18
    timezone: str = "America/New_York"

    # ── Features ────────────────────────────────────────────────────
    enable_bias_warnings: bool = True

    model_config = {"env_file": _find_env_file(), "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
