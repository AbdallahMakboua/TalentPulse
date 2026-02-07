# Deployment Guide

> Step-by-step guide to deploying TalentPulse in production.

---

## Quick Start (Docker Compose)

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker | 24+ | Container runtime |
| Docker Compose | v2+ | Service orchestration |
| Git | 2.x | Clone repository |

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/TalentPulse.git
cd TalentPulse

# Copy and configure environment
cp .env.example .env
```

Edit `.env`:

```bash
# Database
POSTGRES_USER=talentpulse
POSTGRES_PASSWORD=<strong-random-password>
POSTGRES_DB=talentpulse
DATABASE_URL=postgresql+asyncpg://talentpulse:<password>@db:5432/talentpulse

# Ollama (optional — system works without it)
OLLAMA_BASE_URL=http://ollama:11434

# App
APP_ENV=production
LOG_LEVEL=info
```

### 2. Launch All Services

```bash
# Start database + API + frontend
docker compose up -d

# Include Ollama (GPU recommended)
docker compose --profile ollama up -d
```

### 3. Run Database Migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Seed Demo Data

```bash
# Via API
curl -X POST http://localhost:8000/sync/run

# Or via make
make seed
```

### 5. Verify

```bash
# API health
curl http://localhost:8000/health

# Frontend
open http://localhost:3000
```

---

## Service Architecture

```
┌──────────────────────────────────────────────────┐
│                  Docker Network                   │
│                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │   db    │  │   api   │  │   web   │         │
│  │ :5432   │←─│ :8000   │←─│ :3000   │←── User │
│  │postgres │  │ FastAPI │  │ Next.js │         │
│  └─────────┘  └────┬────┘  └─────────┘         │
│                     │                            │
│               ┌─────┴─────┐                      │
│               │  ollama   │ (optional)            │
│               │  :11434   │                      │
│               └───────────┘                      │
└──────────────────────────────────────────────────┘
```

### Port Mapping

| Service | Internal Port | External Port | Purpose |
|---|---|---|---|
| `db` | 5432 | 5432 | PostgreSQL database |
| `api` | 8000 | 8000 | FastAPI backend |
| `web` | 3000 | 3000 | Next.js frontend |
| `ollama` | 11434 | 11434 | Local LLM (optional profile) |

---

## Environment Variables

### Required

| Variable | Example | Description |
|---|---|---|
| `POSTGRES_USER` | `talentpulse` | Database username |
| `POSTGRES_PASSWORD` | `<secret>` | Database password |
| `POSTGRES_DB` | `talentpulse` | Database name |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Full async connection string |

### Optional

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | Model for question/review generation |
| `APP_ENV` | `development` | `development` or `production` |
| `LOG_LEVEL` | `info` | Logging verbosity |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |

---

## Database Setup

### PostgreSQL

TalentPulse uses PostgreSQL 16 with UUID primary keys and JSON columns.

```bash
# Connect to database
docker compose exec db psql -U talentpulse -d talentpulse

# Check tables
\dt

# Verify data
SELECT count(*) FROM employees;
SELECT count(*) FROM weekly_signals;
```

### Migrations with Alembic

```bash
# Apply all migrations
docker compose exec api alembic upgrade head

# Check current revision
docker compose exec api alembic current

# Generate new migration (after model changes)
docker compose exec api alembic revision --autogenerate -m "description"

# Rollback one step
docker compose exec api alembic downgrade -1
```

---

## Ollama Setup

### With Docker Compose (Recommended)

```bash
# Start with Ollama profile
docker compose --profile ollama up -d

# Pull the model (first time only — ~4.7GB)
docker compose exec ollama ollama pull llama3.1:8b

# Verify
curl http://localhost:11434/api/tags
```

### Standalone Installation

```bash
# macOS
brew install ollama
ollama serve &
ollama pull llama3.1:8b

# Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

Update `.env`:
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434  # macOS/Windows
OLLAMA_BASE_URL=http://172.17.0.1:11434            # Linux
```

### GPU Acceleration

For GPU-accelerated inference:

```yaml
# docker-compose.override.yml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Without Ollama

TalentPulse works without Ollama. The system falls back to rule-based templates for coaching questions and review drafts. The `health` endpoint reports `ollama_available: false`.

---

## Production Hardening

### 1. Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name talentpulse.yourcompany.com;

    ssl_certificate /etc/ssl/certs/talentpulse.pem;
    ssl_certificate_key /etc/ssl/private/talentpulse.key;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

### 2. Database Backups

```bash
# Automated daily backup
docker compose exec db pg_dump -U talentpulse talentpulse | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore
gunzip < backup_20260101.sql.gz | docker compose exec -T db psql -U talentpulse talentpulse
```

### 3. Resource Limits

```yaml
# docker-compose.override.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
  web:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
  ollama:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### 4. Logging

```bash
# View API logs
docker compose logs -f api

# View all service logs
docker compose logs -f

# JSON structured logging (production)
LOG_LEVEL=info APP_ENV=production docker compose up -d
```

---

## Development Setup (Without Docker)

### Backend

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL locally
# Set DATABASE_URL in .env

alembic upgrade head
uvicorn app.routes.main:app --reload --port 8000
```

### Frontend

```bash
cd web
npm install
npm run dev
# → http://localhost:3000
```

### Run Tests

```bash
# Backend (81 tests)
cd api && pytest -v --tb=short

# Frontend (55 tests)
cd web && npx jest --verbose
```

---

## Makefile Commands

| Command | Description |
|---|---|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make seed` | Generate demo data |
| `make test` | Run all tests |
| `make logs` | Tail service logs |
| `make migrate` | Run Alembic migrations |
| `make clean` | Remove volumes and containers |

---

## Troubleshooting

### "Connection refused" on API

```bash
# Check if API container is running
docker compose ps

# Check API logs for startup errors
docker compose logs api

# Verify database is ready
docker compose exec db pg_isready
```

### "Ollama not available"

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If using Docker profile, ensure it's started
docker compose --profile ollama up -d

# Pull model if not downloaded
docker compose exec ollama ollama pull llama3.1:8b
```

### Database migration errors

```bash
# Check current state
docker compose exec api alembic current

# Force to a specific revision
docker compose exec api alembic stamp head

# Start fresh (WARNING: destroys data)
docker compose down -v
docker compose up -d
docker compose exec api alembic upgrade head
```

### Frontend can't reach API

```bash
# Check NEXT_PUBLIC_API_URL is set correctly
# Default: http://localhost:8000
# In Docker: http://api:8000 (internal) / http://localhost:8000 (browser)
```
