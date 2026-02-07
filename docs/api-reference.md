# API Reference

> Complete endpoint documentation for the TalentPulse FastAPI backend.

**Base URL:** `http://localhost:8000`

All responses are JSON. All endpoints return appropriate HTTP status codes.

---

## Health

### `GET /health`

System health check including Ollama availability.

**Response:**
```json
{
  "status": "ok",
  "service": "TalentPulse API",
  "version": "0.1.0",
  "ollama_available": true,
  "privacy": "metadata-only"
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | `"ok"` if the service is healthy |
| `ollama_available` | boolean | Whether the local LLM is reachable |
| `privacy` | string | Always `"metadata-only"` |

---

## Sync

### `POST /sync/run`

Triggers the full data pipeline: upsert teams/employees → generate signals → compute scores.

In demo mode, generates synthetic data for 15 employees across 8+ teams.

**Request:** No body required.

**Response:**
```json
{
  "status": "ok",
  "message": "Demo data synced successfully",
  "teams_synced": 8,
  "employees_synced": 15,
  "signals_generated": 120,
  "scores_computed": 60
}
```

---

## Organization

### `GET /org/overview`

Aggregated organization-wide health dashboard data.

**Response:**
```json
{
  "total_employees": 15,
  "total_teams": 8,
  "burnout_risk_distribution": { "Low": 8, "Medium": 4, "High": 3 },
  "pressure_distribution": { "Low": 9, "Medium": 3, "High": 3 },
  "potential_distribution": { "Low": 5, "Medium": 6, "High": 4 },
  "degradation_distribution": { "Low": 10, "Medium": 3, "High": 2 },
  "trending_alerts": [
    {
      "type": "burnout_risk",
      "employee": "Jordan Rivera",
      "team": "Engineering",
      "score": 78,
      "message": "Burnout risk score 78 — after-hours activity trending up"
    }
  ],
  "overloaded_teams": [
    { "team": "Data Science", "avg_workload": 82.3 }
  ],
  "collaboration_bottlenecks": []
}
```

| Field | Type | Description |
|---|---|---|
| `burnout_risk_distribution` | `Record<string, number>` | Count of employees per risk level |
| `trending_alerts` | `Alert[]` | Employees with rising risk scores |
| `overloaded_teams` | `object[]` | Teams with high average workload |

---

## Teams

### `GET /teams`

List all teams with aggregated score summaries.

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Engineering",
    "department": "Technology",
    "employee_count": 4,
    "avg_burnout_risk": 45.2,
    "avg_high_potential": 58.1,
    "avg_performance_degradation": 32.0,
    "workload_imbalance": 12.5,
    "trend": "stable"
  }
]
```

| Field | Type | Description |
|---|---|---|
| `workload_imbalance` | float | Standard deviation of workload across team members (higher = less fair) |
| `trend` | string | `"improving"`, `"stable"`, or `"declining"` based on 4-week score trend |

---

## Employees

### `GET /employees`

List all employees with their latest scores.

**Query Parameters:**

| Name | Type | Description |
|---|---|---|
| `risk_filter` | string | Filter by burnout risk level: `"low"`, `"medium"`, `"high"` |
| `team` | string | Filter by team name (partial match) |

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Alice Chen",
    "email": "alice.chen@talentpulse.dev",
    "role": "Senior Software Engineer",
    "seniority": "senior",
    "tenure_months": 24,
    "team_name": "Engineering",
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "burnout_risk": 72.4,
    "burnout_label": "High",
    "high_potential": 55.0,
    "potential_label": "Medium",
    "performance_degradation": 38.0,
    "degradation_label": "Medium",
    "high_pressure": 65.0,
    "pressure_label": "High"
  }
]
```

---

### `GET /employees/{id}/insights`

Full employee insight panel with scores, explainability, signals, predictions, and recommendations.

**Path Parameters:**

| Name | Type | Description |
|---|---|---|
| `id` | UUID | Employee ID |

**Response:**
```json
{
  "employee": { /* EmployeeSummary (see above) */ },
  "signals": [
    {
      "week_start": "2026-02-02",
      "tasks_completed": 12,
      "missed_deadlines": 1,
      "workload_items": 15,
      "cycle_time_days": 3.2,
      "meeting_hours": 22.5,
      "meeting_count": 18,
      "avg_meeting_length_min": 42,
      "fragmentation_score": 0.65,
      "focus_blocks": 4,
      "response_time_bucket": "fast",
      "after_hours_events": 8,
      "unique_collaborators": 12,
      "cross_team_ratio": 0.35,
      "support_actions": 3,
      "learning_hours": 2.0,
      "stretch_assignments": 1,
      "skill_progress": 0.6,
      "data_quality": 0.95
    }
  ],
  "scores": [
    {
      "score_name": "burnout_risk",
      "score": 72.4,
      "label": "High",
      "top_contributors": [
        {
          "signal": "after_hours_events",
          "value": 8,
          "normalized": 0.8,
          "weight": 0.25,
          "contribution": 0.20,
          "direction": "up",
          "delta": "+33%"
        }
      ],
      "trend_explanation": "Burnout risk has increased 15% over the past 4 weeks",
      "confidence": 0.85,
      "limitations": "Based on 6 weeks of data (8 recommended)",
      "fairness_warning": ""
    }
  ],
  "recommendations": [
    "🔴 High burnout risk — consider reducing meeting load",
    "⚠️ After-hours activity trending up — review workload balance",
    "💡 Strong cross-team collaboration — potential tech lead candidate"
  ],
  "hidden_talent": false,
  "predictive_burnout": {
    "alert": "high",
    "message": "Burnout risk projected to reach critical in ~3 weeks",
    "current_score": 72.4,
    "projected_weeks": 3,
    "pattern_signals": { "after_hours_events": 8, "meeting_hours": 22.5 },
    "confidence": 0.82,
    "uncertainty": "moderate",
    "recommended_action": "Reduce meeting load by 20% and protect 2 focus blocks per day"
  },
  "skills": [
    { "skill_name": "Python", "proficiency": 4, "is_growing": true },
    { "skill_name": "System Design", "proficiency": 3, "is_growing": false }
  ]
}
```

**Key sections:**

| Section | Description |
|---|---|
| `scores` | 4 scored dimensions with full explainability |
| `top_contributors` | Exact signals driving each score, with weights and direction |
| `predictive_burnout` | Forward-looking burnout prediction (null if not at risk) |
| `hidden_talent` | Boolean flag for quiet-impact detection |
| `recommendations` | Prioritized action items based on score patterns |

**Error:** `404` if employee not found.

---

### `GET /employees/{id}/questions`

Generate data-informed 1:1 coaching questions.

**Response:**
```json
{
  "employee_name": "Alice Chen",
  "questions": [
    "How are you feeling about your work this week, Alice?",
    "I've noticed your workload has been intense. What's been the most challenging part?",
    "Are there meetings or tasks we can deprioritize to give you more focus time?",
    "What's been the most rewarding part of your work recently?",
    "What's one thing I can do to better support you?"
  ],
  "listening_cues": [
    "Listen for energy level, enthusiasm, and any hesitation.",
    "Watch for signs of exhaustion, frustration, or disengagement."
  ],
  "follow_up_actions": [
    "Review and reduce meeting load by 20% next sprint.",
    "Block protected focus time on calendar.",
    "Send summary of action items within 24 hours."
  ],
  "context_notes": [
    "Burnout risk score: 72/100. After-hours activity: 8 events."
  ],
  "generated_by": "template"
}
```

| Field | Type | Description |
|---|---|---|
| `generated_by` | string | `"template"` (rule-based) or `"ollama"` (AI-enhanced) |
| `listening_cues` | string[] | What to watch for during the conversation |
| `follow_up_actions` | string[] | Concrete post-meeting action items |

---

### `POST /employees/{id}/review-draft`

Generate a performance review draft.

**Request Body (optional):**
```json
{
  "tone": "balanced"
}
```

| Field | Type | Default | Options |
|---|---|---|---|
| `tone` | string | `"balanced"` | `"balanced"`, `"supportive"`, `"direct"` |

**Response:**
```json
{
  "employee_name": "Alice Chen",
  "period": "Last 8 weeks",
  "highlights": [
    "Consistently high task completion rate above team average",
    "Strong cross-team collaboration breadth"
  ],
  "growth_areas": [
    "After-hours work pattern suggests workload management opportunity",
    "Meeting-to-focus ratio could be improved"
  ],
  "risks": [
    "Burnout risk score trending upward — monitor closely"
  ],
  "suggested_goals": [
    "Maintain task completion while reducing after-hours by 30%",
    "Increase protected focus blocks from 4 to 6 per week"
  ],
  "summary": "Alice has demonstrated strong technical delivery and collaboration...",
  "generated_by": "template"
}
```

---

### `DELETE /employees/{id}/data`

Delete all data for an employee (GDPR compliance).

Removes: employee record, all weekly signals, all scores, all skills.

**Response:**
```json
{
  "status": "deleted",
  "employee_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Error:** `404` if employee not found.

---

## Settings

### `GET /settings`

Get current application settings.

**Response:**
```json
{
  "working_hours_start": 9,
  "working_hours_end": 18,
  "timezone": "America/New_York",
  "data_retention_days": 90,
  "demo_mode": true,
  "enable_graph": false,
  "scoring_weights": {}
}
```

### `POST /settings`

Update application settings. Only include fields to update.

**Request Body:**
```json
{
  "working_hours_start": 8,
  "data_retention_days": 60,
  "demo_mode": false
}
```

**Response:** Updated settings object (same as `GET /settings`).

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Employee not found"
}
```

| Status Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad request (invalid parameters) |
| `404` | Resource not found |
| `500` | Internal server error |

---

## Signal Columns Reference

The 21 signals collected per employee per week:

| Signal | Type | Description |
|---|---|---|
| `tasks_completed` | int | Number of tasks/tickets marked done |
| `missed_deadlines` | int | Tasks not completed by due date |
| `workload_items` | int | Total active items |
| `cycle_time_days` | float | Average days from start to completion |
| `meeting_hours` | float | Total hours in meetings |
| `meeting_count` | int | Number of meetings attended |
| `avg_meeting_length_min` | float | Average meeting duration in minutes |
| `fragmentation_score` | float | Calendar fragmentation (0-1, higher = more fragmented) |
| `focus_blocks` | int | Number of uninterrupted 90+ min blocks |
| `response_time_bucket` | string | Response speed category (fast/normal/slow) |
| `after_hours_events` | int | Calendar/email events outside working hours |
| `unique_collaborators` | int | Distinct people interacted with |
| `cross_team_ratio` | float | Fraction of collaborators from other teams |
| `support_actions` | int | Mentoring, code reviews, helping actions |
| `learning_hours` | float | Time spent in learning activities |
| `stretch_assignments` | int | Tasks outside comfort zone |
| `skill_progress` | float | Skill growth indicator (0-1) |
| `data_quality` | float | Confidence in data completeness (0-1) |
