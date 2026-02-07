# Architecture

> System design for TalentPulse — AI-Powered Performance Monitoring & Talent Intelligence Engine.

---

## High-Level Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Docker Compose                                 │
│                                                                          │
│  ┌─────────────┐     ┌───────────────────┐     ┌──────────────────┐     │
│  │  Next.js 14  │────▶│   FastAPI (async)  │────▶│  PostgreSQL 16   │     │
│  │  Port 3000   │◀────│   Port 8000        │◀────│  Port 5432       │     │
│  │              │     │                    │     │                  │     │
│  │  • App Router│     │  • SQLAlchemy 2.0  │     │  • 6 tables      │     │
│  │  • Tailwind  │     │  • Alembic         │     │  • UUID PKs      │     │
│  │  • Recharts  │     │  • APScheduler     │     │  • JSON columns  │     │
│  └─────────────┘     └────────┬───────────┘     └──────────────────┘     │
│                                │                                         │
│                       ┌────────▼───────────┐                             │
│                       │   Ollama (optional) │                             │
│                       │   Port 11434        │                             │
│                       │   llama3.1:8b       │                             │
│                       └────────────────────┘                             │
└──────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Signal Ingestion Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐
│ MS Graph API │────▶│ graph_client │────▶│ WeeklySignal DB │
│ (metadata)   │     │ (metadata    │     │ (21 columns per │
│              │     │  only!)      │     │  employee/week) │
└──────────────┘     └──────────────┘     └────────┬────────┘
       │                                            │
       │ OR (demo mode)                             │
       │                                            ▼
┌──────────────┐                          ┌─────────────────┐
│ generate_demo│─────────────────────────▶│ Scoring Engine  │
│ (5 archetype │                          │ - 4 dimensions  │
│  synthetic)  │                          │ - YAML weights  │
└──────────────┘                          │ - bias normali. │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ EmployeeScore DB│
                                          │ - explainability│
                                          │ - JSON metadata │
                                          └─────────────────┘
```

### 2. Request Flow

```
Browser → Next.js Page → API Client (lib/api.ts)
                              │
                              ▼
                         FastAPI Router
                              │
                    ┌─────────┼──────────┐
                    ▼         ▼          ▼
              Services    Scoring    Ollama Client
              (insights,  (scorer,   (generate +
               questions,  bias)     fallback)
               reviews)
                    │
                    ▼
              SQLAlchemy Async Session → PostgreSQL
```

## Backend Layers

### Layer 1: Models (`app/models.py`)

| Model | Purpose | Key Columns |
|---|---|---|
| `Team` | Organization unit | name, department |
| `Employee` | Individual person | name, email, role, seniority, tenure_months, archetype |
| `WeeklySignal` | Raw metadata signals per week | 21 signal columns (tasks, meetings, focus, collab, etc.) |
| `EmployeeScore` | Computed score per dimension | dimension, score, label, explainability (JSON) |
| `EmployeeSkill` | Skill proficiency tracking | skill_name, proficiency, is_growing |
| `AppSettings` | Application configuration | key-value JSON storage |

All models use UUID primary keys and have `created_at` / `updated_at` timestamps.

### Layer 2: Signals (`app/signals/`)

**`generate_demo.py`** — Synthetic data generator
- 5 archetypes: `healthy`, `overloaded`, `declining`, `rising_star`, `quiet_impact`
- 15 demo employees across 8+ teams
- Deterministic with seed (reproducible demos)
- 8 weeks of realistic weekly signal data per employee

**`compute.py`** — Signal analysis
- `compute_trend()` — linear regression slope classification
- `compute_delta()` — week-over-week percentage change
- `compute_rolling_average()` — moving average with configurable window
- `compute_workload_distribution()` — Gini coefficient for workload fairness
- `compute_fragmentation()` — calendar fragmentation score

### Layer 3: Scoring (`app/scoring/`)

**`weights.yaml`** — Configurable scoring weights
```yaml
burnout_risk:
  meeting_hours: 0.20
  after_hours_events: 0.25
  focus_blocks: -0.15        # protective factor (negative = reduces risk)
  fragmentation_score: 0.15
  ...
```

**`scorer.py`** — Multi-dimensional scorer
- 4 dimensions: `burnout_risk`, `high_pressure`, `high_potential`, `performance_degradation`
- Weighted sum → 0-100 normalized score → label (Low/Medium/High)
- `detect_hidden_talent()` — quiet impact detection
- `predict_burnout()` — trend extrapolation with confidence intervals

**`bias.py`** — Bias-aware normalization
- `compute_self_baseline()` — 70% weight, employee's own historical patterns
- `compute_cohort_baseline()` — 30% weight, peer group comparison
- `z_score()` — standardized deviation from group
- `check_fairness()` — warns when cohort too small or role mismatch
- `build_fairness_note()` — human-readable bias disclosure

### Layer 4: Services (`app/services/`)

| Service | Responsibility |
|---|---|
| `insights.py` | Org overview, employee insights, recommendations engine |
| `questions.py` | 1:1 coaching agenda generation (Ollama + template fallback) |
| `reviews.py` | Performance review draft generation (Ollama + template fallback) |

### Layer 5: Routes (`app/routes/`)

| Router | Endpoints |
|---|---|
| `health.py` | `GET /health` |
| `sync.py` | `POST /sync/run` |
| `org.py` | `GET /org/overview` |
| `teams.py` | `GET /teams` |
| `employees.py` | `GET /employees`, `GET /{id}/insights`, `GET /{id}/questions`, `POST /{id}/review-draft`, `DELETE /{id}/data` |
| `settings.py` | `GET /settings`, `POST /settings` |

## Frontend Architecture

### Next.js 14 App Router

```
app/
├── layout.tsx          ← Root layout with Sidebar
├── page.tsx            ← Org Overview (dashboard home)
├── teams/page.tsx      ← Team cards with scores
├── employees/
│   ├── page.tsx        ← Searchable employee table
│   └── [id]/page.tsx   ← Employee detail + AI features
├── settings/page.tsx   ← Configuration form
└── transparency/page.tsx ← Privacy disclosure page
```

### Component Hierarchy

```
Layout
├── Sidebar (navigation, privacy badge)
└── Page Content
    ├── StatCard (metric display)
    ├── RiskDistribution (Recharts bar chart)
    ├── AlertsList (severity-coded alerts)
    ├── ScoreBadge (color-coded score + label)
    ├── SignalChart (multi-metric line chart)
    ├── ExplainCard (explainability display)
    ├── PredictiveBurnout (burnout prediction card)
    ├── HiddenTalent (quiet-impact discovery)
    ├── CoachingPanel (1:1 agenda generator)
    └── ReviewPanel (review draft generator)
```

## Database Schema

```
teams
├── id (UUID PK)
├── name
├── department
└── created_at

employees
├── id (UUID PK)
├── team_id (FK → teams)
├── name, email, role, seniority
├── tenure_months, archetype
└── created_at, updated_at

weekly_signals
├── id (UUID PK)
├── employee_id (FK → employees)
├── week_start (DATE)
├── 21 signal columns (tasks, meetings, focus, collab, etc.)
├── data_quality
└── UNIQUE(employee_id, week_start)

employee_scores
├── id (UUID PK)
├── employee_id (FK → employees)
├── dimension (burnout_risk | high_pressure | high_potential | performance_degradation)
├── score (0-100), label (Low/Medium/High)
├── explainability (JSON - top_contributors, trend, confidence, fairness)
└── scored_at

employee_skills
├── id (UUID PK)
├── employee_id (FK → employees)
├── skill_name, proficiency (1-5)
└── is_growing

app_settings
├── id (UUID PK)
├── key, value (JSON)
└── updated_at
```

## Key Design Decisions

### 1. Metadata-Only Collection
Signal columns are strictly aggregate counts and durations. No message content, email subjects, or conversation text is ever stored. This is enforced at the Graph client level via explicit `$select` fields.

### 2. Self+Cohort Baseline Normalization
- 70% self-baseline: compared to employee's own 8-week history
- 30% cohort-baseline: compared to same-role/seniority peers
- Prevents unfair comparison of IC vs. manager workload patterns

### 3. YAML-Driven Scoring
All scoring weights are in `weights.yaml`, not hardcoded. This allows:
- Easy tuning without code changes
- Transparent audit trail
- Customer-specific configuration

### 4. Graceful Degradation
- **No Ollama?** → Template-based questions and reviews still work
- **No Graph?** → Demo mode with 5 archetypes of synthetic data
- **No PostgreSQL?** → Tests use SQLite via aiosqlite

### 5. Explainability-First
Every score includes:
- Top contributing factors with weights and directions
- Trend explanation (is it getting better or worse?)
- Confidence level
- Fairness warning (if applicable)
- Limitations disclosure
