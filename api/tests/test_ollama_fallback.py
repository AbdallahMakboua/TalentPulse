"""Tests for Ollama client fallback behavior."""

import pytest
from app.ollama_client import OllamaClient


class TestOllamaFallback:
    """Ensure system works gracefully without Ollama."""

    @pytest.mark.asyncio
    async def test_unavailable_ollama_returns_false(self):
        client = OllamaClient()
        client.base_url = "http://localhost:99999"  # unreachable
        client.reset()
        assert await client.is_available() is False

    @pytest.mark.asyncio
    async def test_generate_returns_none_when_unavailable(self):
        client = OllamaClient()
        client.base_url = "http://localhost:99999"
        client.reset()
        result = await client.generate("test prompt")
        assert result is None

    @pytest.mark.asyncio
    async def test_availability_is_cached(self):
        client = OllamaClient()
        client._available = True
        assert await client.is_available() is True

    @pytest.mark.asyncio
    async def test_reset_clears_cache(self):
        client = OllamaClient()
        client._available = True
        client.reset()
        assert client._available is None

    @pytest.mark.asyncio
    async def test_questions_endpoint_uses_template_fallback(self, client):
        """End-to-end: questions should work with template when Ollama down."""
        await client.post("/sync/run")
        emps = (await client.get("/employees")).json()
        resp = await client.get(f"/employees/{emps[0]['id']}/questions")
        assert resp.status_code == 200
        assert resp.json()["generated_by"] == "template"

    @pytest.mark.asyncio
    async def test_review_endpoint_uses_template_fallback(self, client):
        """End-to-end: review should work with template when Ollama down."""
        await client.post("/sync/run")
        emps = (await client.get("/employees")).json()
        resp = await client.post(f"/employees/{emps[0]['id']}/review-draft")
        assert resp.status_code == 200
        assert resp.json()["generated_by"] == "template"
