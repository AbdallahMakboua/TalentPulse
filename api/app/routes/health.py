"""Health check endpoint."""

from fastapi import APIRouter
from app.ollama_client import ollama

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    ollama_ok = await ollama.is_available()
    return {
        "status": "healthy",
        "service": "TalentPulse API",
        "version": "1.0.0",
        "ollama_available": ollama_ok,
        "privacy": "No content data is ever collected. Metadata only.",
    }
