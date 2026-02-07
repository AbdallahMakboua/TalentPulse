"""Ollama local LLM client with automatic template fallback."""

from __future__ import annotations

import logging
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Calls local Ollama for generation. Falls back to templates if unreachable."""

    def __init__(self):
        s = get_settings()
        self.base_url = s.ollama_base_url
        self.model = s.ollama_model
        self.timeout = s.ollama_timeout
        self._available: bool | None = None

    async def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        if self._available is not None:
            return self._available
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                self._available = resp.status_code == 200
        except Exception:
            logger.warning("Ollama not reachable at %s – using template fallback", self.base_url)
            self._available = False
        return self._available

    async def generate(self, prompt: str, system: str = "") -> str | None:
        """Generate text from Ollama. Returns None if not available."""
        if not await self.is_available():
            return None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": system,
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 1024},
                    },
                )
                resp.raise_for_status()
                return resp.json().get("response", "")
        except Exception as e:
            logger.error("Ollama generation failed: %s", e)
            return None

    def reset(self):
        """Reset availability cache (useful for testing)."""
        self._available = None


# Singleton
ollama = OllamaClient()
