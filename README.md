<div align="center">

# 🎯 TalentPulse

**AI-Powered Performance Monitoring & Talent Intelligence Engine**

*Privacy-first · Explainable · Bias-aware*

[![CI](https://github.com/your-org/talentpulse/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/talentpulse/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## The Problem

Every organization faces the same talent blind spots:

| Blind Spot | Impact |
|---|---|
| **Burnout is invisible** until people quit | 34% of tech workers are actively burned out |
| **High performers hide** in large teams | Quiet contributors get overlooked at review time |
| **Reviews are subjective** and time-consuming | Managers spend 17+ hours writing reviews per cycle |
| **No coaching data** for 1:1 meetings | 1:1s become status updates instead of growth conversations |

**TalentPulse** turns Microsoft 365 metadata into actionable talent intelligence — without reading a single email or message.

---

## 10-Line Pitch

> TalentPulse is a privacy-first AI engine that monitors workforce health through Microsoft 365 metadata signals — never content. It predicts burnout 4-6 weeks before it becomes visible, surfaces hidden talent that traditional reviews miss, generates bias-aware review drafts in seconds, and powers every 1:1 with a data-informed coaching agenda.
>
> Every score is explainable (users see exactly what signals drove it), every metric is bias-normalized against self-baselines and cohort baselines, and there's a full transparency page showing what data is collected and — critically — what is never collected.
>
> It runs entirely on-premises with a local Ollama LLM, so no employee data ever leaves your infrastructure.

---

## ✨ Blow-Their-Minds Features

### 1. 🔥 Predictive Burnout Alerts
Detects rising burnout risk 4-6 weeks before it becomes visible, using trend analysis across after-hours work, meeting load, focus-time erosion, and weekend activity.

### 2. 💎 Hidden Talent Discovery
Identifies "quiet impact" employees — high collaboration, knowledge sharing, and mentoring signals that traditional performance reviews miss entirely.

### 3. 📝 AI Review Draft Generator
One-click review drafts grounded in 8 weeks of objective signal data. Choose from balanced, supportive, or direct tone. Always a starting point, never the final word.

### 4. 🧠 Coaching Copilot
Generates a data-informed 1:1 agenda with coaching questions tailored to each employee's current situation — powered by local Ollama LLM with template fallback.

---

## 🏗 Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Next.js 14  │────▶│   FastAPI (async) │────▶│ PostgreSQL   │
│  Dashboard   │◀────│   Scoring Engine  │◀────│  + Alembic   │
└─────────────┘     │   Signal Pipeline │     └──────────────┘
                     │   Bias Normalizer │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Ollama (local)   │
                     │  llama3.1:8b      │
                     │  Template fallback│
                     └──────────────────┘
```

**Key Design Decisions:**
- **Metadata only** — mail subjects, calendar durations, message counts. Never content or subjects.
- **Self-baseline** (70%) + **cohort-baseline** (30%) for bias-aware normalization
- **Explainability built-in** — every score shows its top contributing factors
- **Graceful degradation** — works without Ollama (template fallback), without Graph (demo data)

---

## 🚀 Quick Start — 2 Commands

```bash
# 1. Clone and configure
git clone https://github.com/your-org/talentpulse.git
cd talentpulse
cp .env.example .env

# 2. Launch everything
make up
```

That's it. Open **http://localhost:3000** and click **Sync Demo Data**.

### What happens:
1. Docker Compose starts PostgreSQL, FastAPI, and Next.js
2. Alembic runs migrations automatically
3. Click "Sync" → generates 15 demo employees across 8+ teams with 8 weeks of signals
4. Explore the dashboard, drill into employees, generate reviews and coaching agendas

---

## 🔧 Development Setup

### Prerequisites
- Docker & Docker Compose v2
- (Optional) [Ollama](https://ollama.ai) for AI features

### With Ollama (full AI features)
```bash
# Start with Ollama profile
make up-ollama

# Pull the model (first time only)
docker exec -it talentpulse-ollama ollama pull llama3.1:8b
```

### Without Ollama (template fallback)
```bash
make up
# Everything works — reviews and coaching use smart templates
```

### Run Tests
```bash
make test          # Run all tests with coverage
make test-fast     # Skip slow tests
make lint          # Run ruff linter
```

### Seed Demo Data
```bash
# Via API
curl -X POST http://localhost:8000/sync/run

# Via script
make seed
```

---

## 📡 API Reference

### Health
```bash
curl http://localhost:8000/health
# {"status": "ok", "ollama_available": true, "version": "0.1.0"}
```

### Sync Demo Data
```bash
curl -X POST http://localhost:8000/sync/run
# {"teams_synced": 8, "employees_synced": 15, "signals_generated": 120, "scores_computed": 15}
```

### Organization Overview
```bash
curl http://localhost:8000/org/overview
# Returns: total employees, risk distributions, alerts, overloaded teams
```

### Teams
```bash
curl http://localhost:8000/teams
# Returns: all teams with avg scores, burnout %, potential %, workload imbalance
```

### Employees
```bash
curl http://localhost:8000/employees
curl "http://localhost:8000/employees?risk_filter=high"
curl "http://localhost:8000/employees?team=Engineering"
```

### Employee Insights
```bash
curl http://localhost:8000/employees/1/insights
# Returns: scores, explainability cards, signals, recommendations, burnout prediction, hidden talent, skills
```

### Coaching Questions
```bash
curl http://localhost:8000/employees/1/questions
# Returns: 5 data-informed 1:1 questions + context summary
```

### Review Draft
```bash
curl -X POST http://localhost:8000/employees/1/review-draft \
  -H "Content-Type: application/json" \
  -d '{"tone": "balanced"}'
# Returns: multi-paragraph review grounded in signal data
```

### Delete Employee Data (GDPR)
```bash
curl -X DELETE http://localhost:8000/employees/1/data
```

### Settings
```bash
# Get current settings
curl http://localhost:8000/settings

# Update settings
curl -X POST http://localhost:8000/settings \
  -H "Content-Type: application/json" \
  -d '{"scoring_interval_hours": 12, "privacy_mode": "strict"}'
```

---

## 🔒 Privacy Architecture

| What we collect | What we NEVER collect |
|---|---|
| Email count, send time (hour) | Email body, subject, or recipients |
| Meeting duration, count | Meeting content, attendee names |
| Message count per channel | Message text or attachments |
| PR count, review count | Code content or diff |
| Focus/collab hour estimates | Screen recordings, keystrokes |

### Privacy Principles
1. **Metadata only** — aggregated counts and durations, never content
2. **No individual surveillance** — signals are for coaching, not monitoring
3. **Self-baseline normalization** — employees compared to their own patterns first
4. **Transparency page** — every user can see exactly what data drives their scores
5. **Data deletion** — one-click removal of all employee data (GDPR-ready)
6. **On-premises LLM** — Ollama runs locally, no data sent to external AI services

---

## 🧪 Testing

```bash
make test
```

**Test coverage target: ≥80%**

| Test File | Tests | Coverage Area |
|---|---|---|
| `test_health.py` | 2 | Health endpoint |
| `test_demo_generator.py` | 12 | Signal generation, archetypes, determinism |
| `test_signals_compute.py` | 15 | Trends, deltas, distributions, fragmentation |
| `test_scoring_bias.py` | 22 | Scoring, bias normalization, fairness |
| `test_insights_api.py` | 11 | Full API integration |
| `test_ollama_fallback.py` | 6 | LLM unavailability, fallback |

### Test Architecture
- **SQLite async** for test DB (no PostgreSQL needed in CI)
- **httpx AsyncClient** for API testing
- **Dependency injection** overrides for isolated tests
- **Deterministic seeds** for reproducible signal generation

---

## 🎬 Demo Script (3 minutes)

1. **Open dashboard** → Show org overview with risk distribution
2. **Point out alerts** → "This person has rising burnout risk — detected 4 weeks early"
3. **Click into an employee** → Show explainability cards: "Here's exactly why the score is 72"
4. **Show Hidden Talent** → "This quiet contributor has high impact signals that reviews miss"
5. **Generate coaching agenda** → Click button, show 5 data-informed questions
6. **Generate review draft** → Switch tone from balanced to supportive, show how it adapts
7. **Open transparency page** → "Here's everything we collect — and everything we don't"
8. **Delete data** → Show one-click data deletion for GDPR compliance

---

## 📁 Project Structure

```
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app + lifespan
│   │   ├── config.py             # Pydantic Settings
│   │   ├── db.py                 # Async SQLAlchemy
│   │   ├── models.py             # 6 ORM models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── graph_client.py       # MS Graph metadata client
│   │   ├── ollama_client.py      # Local LLM client + fallback
│   │   ├── signals/
│   │   │   ├── generate_demo.py  # 5 archetypes, 15 employees
│   │   │   └── compute.py        # Trend, delta, Gini, fragmentation
│   │   ├── scoring/
│   │   │   ├── weights.yaml      # Configurable scoring weights
│   │   │   ├── scorer.py         # 4-dimension scorer
│   │   │   └── bias.py           # Bias-aware normalization
│   │   ├── services/
│   │   │   ├── insights.py       # Org overview, employee insights
│   │   │   ├── questions.py      # Coaching question generator
│   │   │   └── reviews.py        # Review draft generator
│   │   └── routes/
│   │       ├── health.py         # GET /health
│   │       ├── sync.py           # POST /sync/run
│   │       ├── org.py            # GET /org/overview
│   │       ├── teams.py          # GET /teams
│   │       ├── employees.py      # CRUD + insights + AI
│   │       └── settings.py       # GET/POST /settings
│   ├── tests/
│   │   ├── conftest.py           # Async test fixtures
│   │   └── test_*.py             # 68 tests
│   └── alembic/                  # Database migrations
├── web/
│   ├── Dockerfile
│   ├── package.json
│   ├── app/                      # Next.js 14 App Router
│   │   ├── page.tsx              # Org Overview
│   │   ├── teams/page.tsx        # Team cards
│   │   ├── employees/page.tsx    # Employee table
│   │   ├── employees/[id]/page.tsx  # Employee detail
│   │   ├── settings/page.tsx     # Settings
│   │   └── transparency/page.tsx # Privacy disclosure
│   ├── components/               # Reusable UI components
│   └── lib/api.ts                # TypeScript API client
├── scripts/
│   ├── bootstrap.sh              # Full setup script
│   └── seed_demo_data.py         # Seed demo data
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| **Database** | PostgreSQL 16 |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| **AI/LLM** | Ollama (llama3.1:8b) with template fallback |
| **Testing** | pytest, pytest-asyncio, httpx, aiosqlite |
| **Infra** | Docker Compose, GitHub Actions CI |

---

## 🔑 Microsoft Graph Integration

For production use with real M365 data:

1. Register an Azure AD app with `Mail.Read`, `Calendars.Read`, `ChannelMessage.Read.All` (application permissions)
2. Set in `.env`:
   ```
   GRAPH_TENANT_ID=your-tenant-id
   GRAPH_CLIENT_ID=your-client-id
   GRAPH_CLIENT_SECRET=your-secret
   DATA_SOURCE=graph
   ```
3. Restart: `make up`

**Note:** Even with Graph, TalentPulse only reads metadata (counts, timestamps, durations) — never message content.

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Built for hackathons. Designed for production.**

*TalentPulse — Because your people deserve better than guesswork.*

</div>