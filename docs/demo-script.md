# Demo Script — 3-Minute Hackathon Walkthrough

> Step-by-step script for presenting TalentPulse to judges in ~3 minutes.

---

## Setup (Before Demo)

```bash
# Start all services
docker compose up -d

# Seed demo data (15 employees, 8 teams, 8 weeks of signals)
curl -X POST http://localhost:8000/sync/run

# Open browser
open http://localhost:3000
```

Verify: API returns `{"status": "ok"}` at `http://localhost:8000/health`

---

## Slide 0 — The Problem (30 seconds)

**Say:**

> "Every year, top talent quietly burns out and leaves — and managers only find out at the exit interview. HR tools today surface lagging indicators: attrition rates, engagement surveys filled out once a quarter. By the time you see the data, it's too late."
>
> "TalentPulse is an AI-powered early warning system that detects burnout risk, hidden talent, and performance patterns **weeks before they become problems** — all from metadata, with zero surveillance."

---

## Slide 1 — Org Overview Dashboard (45 seconds)

**Navigate to:** `http://localhost:3000` (Dashboard page)

**Point out:**

1. **Risk distribution charts** — "This is the org at a glance. We see burnout risk, pressure, potential, and performance degradation across all 15 employees."

2. **Trending alerts** — "These are employees whose risk scores have been climbing over the past 4 weeks. Jordan Rivera's burnout risk hit 78 — that's a red flag."

3. **Overloaded teams** — "The Data Science team has an average workload score of 82. That's 30% above the org mean."

**Say:**

> "This view gives an HR leader or VP of Engineering a pulse check on the entire org in 10 seconds — no surveys, no self-reporting."

---

## Slide 2 — Employee Deep Dive (60 seconds)

**Click on:** A high-risk employee (e.g., Jordan Rivera or Alice Chen)

**Navigate to:** `http://localhost:3000/employees/{id}`

**Walk through each section:**

1. **Score cards at top** — "Four dimensions: burnout risk, high potential, performance degradation, and pressure. Each is color-coded — red, yellow, green."

2. **Explainability card** — "This is the key differentiator. Click on any score and you see **exactly** which signals drove it. After-hours events contributed 20%, meeting hours 15%. No black box."

3. **Signal trend chart** — "8 weeks of activity patterns. You can see after-hours events spiking in weeks 5-8. That's the burnout trajectory."

4. **Predictive burnout** — "The system projects this employee will reach critical burnout in ~3 weeks if trends continue. This is the early warning."

5. **Hidden talent flag** — "This employee also shows strong cross-team collaboration and mentoring — they're a hidden leader who might not show up in traditional metrics."

**Say:**

> "Every insight is traceable back to specific metadata signals. Managers can trust this because they can verify it."

---

## Slide 3 — Coaching Copilot (30 seconds)

**Click:** Coaching Questions tab

**Show:**

> "Before a 1:1, the manager gets AI-generated coaching questions tailored to this employee's data patterns. Not generic — these are informed by the burnout signals we just saw."

**Point out:**
- Questions adapt based on risk level (high burnout = empathetic tone)
- Listening cues tell managers what to watch for
- Follow-up actions are concrete and actionable

**Say:**

> "This turns data into action. The manager walks into the 1:1 prepared, with empathetic questions — not a confrontation."

---

## Slide 4 — Privacy Architecture (30 seconds)

**Say:**

> "The #1 question we get: 'Isn't this surveillance?' No."
>
> "We collect **metadata only** — task counts, meeting hours, collaboration breadth. Never message content, never code, never keystrokes."
>
> "The AI runs **locally** on Ollama — no data leaves your infrastructure. No OpenAI, no cloud APIs."
>
> "Every score has an explainability card. Employees can see exactly what data drives their scores. GDPR right-to-deletion is one API call."

---

## Slide 5 — Technical Highlights (15 seconds)

**Say:**

> "Built with FastAPI and Next.js. Bias-aware scoring with self-comparison baselines. 21 metadata signals, 4 scored dimensions. 136 tests passing — 81 backend, 55 frontend. Ships with Docker Compose in one command."

---

## Closing (10 seconds)

**Say:**

> "TalentPulse gives organizations a **privacy-first early warning system** for their most valuable asset — their people. It's not about watching employees. It's about **protecting** them."

---

## Backup: Data Points for Q&A

| Question | Answer |
|---|---|
| "How many signals do you track?" | 21 metadata signals per employee per week |
| "What model do you use?" | Llama 3.1 8B via Ollama (local, swappable) |
| "What if Ollama is down?" | Template fallback — system works without AI |
| "How do you handle bias?" | Self-comparison baseline + cohort normalization + fairness warnings |
| "Is this GDPR compliant?" | Yes — right to access, deletion, and explanation built in |
| "What's the tech stack?" | FastAPI, Next.js 14, PostgreSQL, Docker Compose, Ollama |
| "How long to deploy?" | `docker compose up -d` — under 2 minutes |
| "What about data retention?" | Configurable (default 90 days), auto-purge |
| "Can it integrate with real tools?" | Designed for Microsoft Graph API (Teams, Outlook, Planner) |
| "Test coverage?" | 136 tests (81 backend + 55 frontend), 70% backend coverage |

---

## Demo Environment Cheat Sheet

```bash
# Reset demo data
curl -X POST http://localhost:8000/sync/run

# Check health
curl http://localhost:8000/health

# View org overview
curl http://localhost:8000/org/overview | python -m json.tool

# Get employee insights
curl http://localhost:8000/employees | python -m json.tool
# Pick an ID, then:
curl http://localhost:8000/employees/{id}/insights | python -m json.tool

# Generate coaching questions
curl http://localhost:8000/employees/{id}/questions | python -m json.tool
```
