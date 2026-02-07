"""Tests for health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TalentPulse API"
    assert "privacy" in data


@pytest.mark.asyncio
async def test_health_reports_ollama_status(client):
    resp = await client.get("/health")
    data = resp.json()
    # Ollama is unreachable in test env
    assert "ollama_available" in data
    assert data["ollama_available"] is False
