"""TalentPulse – FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routes import health, sync, org, teams, employees, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await init_db()
    yield


app = FastAPI(
    title="TalentPulse",
    description=(
        "AI-Powered Performance Monitoring & Talent Intelligence Engine. "
        "Privacy-first: no content data is ever collected."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Next.js dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(sync.router)
app.include_router(org.router)
app.include_router(teams.router)
app.include_router(employees.router)
app.include_router(settings.router)
