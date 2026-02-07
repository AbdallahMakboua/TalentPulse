# Privacy & Ethics Architecture

> How TalentPulse protects employee privacy while enabling data-informed management.

---

## Core Principles

| Principle | Implementation |
|---|---|
| **Metadata only** | Zero access to message content, email bodies, file contents, or code |
| **On-premises AI** | Ollama runs locally — no data leaves your infrastructure |
| **Transparency** | Every score shows exactly which signals drove it and their weights |
| **Bias awareness** | Self-comparison baselines + cohort z-score normalization |
| **Right to deletion** | One-click GDPR-compliant data erasure per employee |
| **No rank-stacking** | Scores are wellness indicators, not performance rankings |

---

## What We Collect vs. What We Never Touch

### ✅ Collected (Metadata Only)

| Signal | Source | Example |
|---|---|---|
| Task counts | Project tracker | "12 tasks completed this week" |
| Meeting hours | Calendar | "22.5 hours in meetings" |
| Response time buckets | Email/chat metadata | "fast" / "normal" / "slow" |
| After-hours events | Calendar | "8 events outside 9am-6pm" |
| Collaboration breadth | Interaction metadata | "12 unique collaborators" |

### 🚫 Never Collected

| Category | Details |
|---|---|
| **Message content** | No email bodies, chat messages, or DMs |
| **Code content** | No source code, commit diffs, or PR descriptions |
| **File content** | No document text, spreadsheet data, or attachments |
| **Browsing history** | No website visits or search queries |
| **Location data** | No GPS, office badge swipes, or IP geolocation |
| **Keystrokes** | No keystroke logging or screen captures |
| **Sentiment analysis** | No NLP on any written communication |

---

## Bias-Aware Scoring

### The Problem

Raw metrics are inherently unfair:
- A senior architect has fewer PRs than a junior developer
- A part-time employee has fewer meeting hours than full-time
- Different roles have different collaboration patterns

### Our Solution

**Three-layer normalization:**

```
1. Self-Comparison     → Compare employee to their own 8-week baseline
2. Cohort Baseline     → Adjust for role, seniority, and tenure
3. Z-Score Fairness    → Flag scores > 2σ from cohort mean for review
```

**How it works:**

1. **Self-comparison baseline**: Each employee's scores are primarily compared to their own historical pattern. A sudden spike in after-hours work is significant regardless of absolute numbers.

2. **Cohort normalization**: Scores are adjusted for role (`engineer` vs `designer`), seniority (`junior` vs `senior`), and tenure. A junior developer's 15 weekly tasks is different from a senior architect's 15.

3. **Fairness warnings**: When an employee's score diverges > 2 standard deviations from their cohort mean, the system flags a `fairness_warning` in the explainability card. Managers see this warning before taking action.

### Explainability Card

Every score includes a full breakdown:

```json
{
  "score_name": "burnout_risk",
  "score": 72.4,
  "top_contributors": [
    { "signal": "after_hours_events", "contribution": 0.20, "direction": "up" },
    { "signal": "meeting_hours", "contribution": 0.15, "direction": "up" }
  ],
  "confidence": 0.85,
  "limitations": "Based on 6 weeks of data (8 recommended)",
  "fairness_warning": ""
}
```

Managers can drill into exactly why a score looks the way it does, preventing "black box" decisions.

---

## Data Lifecycle

```
Collect → Normalize → Score → Display → Retain → Purge
  │           │          │        │         │        │
  │           │          │        │         │        └─ Auto-delete after
  │           │          │        │         │           retention_days (default 90)
  │           │          │        │         │
  │           │          │        │         └─ Configurable retention period
  │           │          │        │
  │           │          │        └─ Scores shown with full explainability
  │           │          │
  │           │          └─ Bias-aware weighted scoring
  │           │
  │           └─ Self-baseline + cohort normalization
  │
  └─ Metadata extraction only (no content)
```

### Retention Policy

| Setting | Default | Description |
|---|---|---|
| `data_retention_days` | 90 | Signals older than this are auto-purged |
| Manual deletion | On demand | `DELETE /employees/{id}/data` removes everything |

---

## GDPR Compliance

### Right to Access
- `GET /employees/{id}/insights` returns all stored data for an employee

### Right to Deletion
- `DELETE /employees/{id}/data` removes:
  - Employee record
  - All weekly signals
  - All computed scores
  - All skill records
  - Cascading delete ensures no orphaned data

### Right to Explanation
- Every score includes `top_contributors`, `confidence`, `limitations`, and `fairness_warning`
- No opaque predictions — every output traces back to specific signals

### Data Minimization
- Only 21 metadata signals collected (no PII beyond name/email/role)
- Signals are aggregated weekly — no per-minute granularity
- No behavioral surveillance or continuous monitoring

---

## On-Premises LLM

### Why Ollama?

| Concern | Solution |
|---|---|
| Data leaves company | Ollama runs 100% locally |
| Cloud API costs | Open-source model, no per-token fees |
| Vendor lock-in | Swap models freely (llama3.1, mistral, etc.) |
| Compliance | No third-party data processing agreement needed |

### What the LLM Sees

When generating coaching questions or review drafts, the LLM receives:

```
✅ Sent to LLM:
- Employee name
- Score values (e.g., "burnout_risk: 72")
- Signal trends (e.g., "after_hours_events trending up")
- Role and seniority

🚫 Never sent to LLM:
- Email content
- Chat messages
- Code or documents
- Personal information beyond name/role
```

### Template Fallback

If Ollama is unavailable, the system falls back to rule-based templates that require zero AI — ensuring the system remains functional without any LLM.

---

## Ethical Use Guidelines

### Intended Use
- Help managers support employee wellbeing
- Surface hidden talent that traditional metrics miss
- Provide early burnout warning for proactive intervention
- Generate data-informed (not data-driven) 1:1 conversations

### Prohibited Use
- Using scores as sole basis for promotion/termination decisions
- Comparing employees against each other for ranking
- Surveillance or monitoring of specific individuals
- Automated decision-making without human review

### Safeguards
1. **No leaderboards** — Scores are individual, never ranked
2. **Confidence scores** — Low-confidence predictions are flagged
3. **Limitations disclosed** — Each score states what data gaps exist
4. **Manager guidance** — Coaching questions guide supportive conversations, not interrogations
5. **Template fallback** — System works without AI, preventing over-reliance on LLM outputs

---

## Security Measures

| Layer | Protection |
|---|---|
| **Network** | All services run on internal Docker network |
| **Database** | PostgreSQL with role-based access, no public exposure |
| **API** | FastAPI with input validation via Pydantic |
| **LLM** | Local Ollama — no external API calls |
| **Secrets** | Environment variables, never committed to code |
| **Audit** | All score computations are logged with timestamps |
