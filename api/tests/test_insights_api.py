"""Tests for insights API endpoints (integration tests)."""

import pytest


@pytest.mark.asyncio
async def test_sync_run_creates_data(client):
    """POST /sync/run should populate demo data."""
    resp = await client.post("/sync/run")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["employees_processed"] >= 10
    assert data["weeks_generated"] > 0
    assert data["scores_computed"] > 0


@pytest.mark.asyncio
async def test_org_overview_after_sync(client):
    """GET /org/overview should return distribution data."""
    await client.post("/sync/run")
    resp = await client.get("/org/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_employees"] >= 10
    assert data["total_teams"] >= 4
    assert "Low" in data["burnout_risk_distribution"]


@pytest.mark.asyncio
async def test_teams_endpoint(client):
    """GET /teams should return team summaries."""
    await client.post("/sync/run")
    resp = await client.get("/teams")
    assert resp.status_code == 200
    teams = resp.json()
    assert len(teams) >= 4
    for team in teams:
        assert "name" in team
        assert "avg_burnout_risk" in team
        assert "workload_imbalance" in team


@pytest.mark.asyncio
async def test_employees_list(client):
    """GET /employees should return employee summaries."""
    await client.post("/sync/run")
    resp = await client.get("/employees")
    assert resp.status_code == 200
    employees = resp.json()
    assert len(employees) >= 10
    for emp in employees:
        assert "name" in emp
        assert "burnout_risk" in emp
        assert "burnout_label" in emp


@pytest.mark.asyncio
async def test_employees_risk_filter(client):
    """GET /employees?risk_filter=High should filter correctly."""
    await client.post("/sync/run")
    resp = await client.get("/employees?risk_filter=High")
    assert resp.status_code == 200
    employees = resp.json()
    for emp in employees:
        assert emp["burnout_label"] == "High"


@pytest.mark.asyncio
async def test_employee_insights(client):
    """GET /employees/{id}/insights should return full insights."""
    await client.post("/sync/run")

    # Get first employee
    emps = (await client.get("/employees")).json()
    emp_id = emps[0]["id"]

    resp = await client.get(f"/employees/{emp_id}/insights")
    assert resp.status_code == 200
    data = resp.json()

    assert "employee" in data
    assert "signals" in data
    assert "scores" in data
    assert "recommendations" in data
    assert len(data["signals"]) > 0
    assert len(data["scores"]) == 4

    # Verify explainability
    for score in data["scores"]:
        assert "score_name" in score
        assert "top_contributors" in score
        assert "trend_explanation" in score
        assert "confidence" in score
        assert "limitations" in score


@pytest.mark.asyncio
async def test_employee_insights_not_found(client):
    """GET /employees/{bad_id}/insights should 404."""
    import uuid
    resp = await client.get(f"/employees/{uuid.uuid4()}/insights")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_employee_questions(client):
    """GET /employees/{id}/questions should return coaching agenda."""
    await client.post("/sync/run")
    emps = (await client.get("/employees")).json()
    emp_id = emps[0]["id"]

    resp = await client.get(f"/employees/{emp_id}/questions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) >= 3
    assert len(data["listening_cues"]) >= 1
    assert data["generated_by"] == "template"  # Ollama unreachable in tests


@pytest.mark.asyncio
async def test_employee_review_draft(client):
    """POST /employees/{id}/review-draft should generate review."""
    await client.post("/sync/run")
    emps = (await client.get("/employees")).json()
    emp_id = emps[0]["id"]

    resp = await client.post(f"/employees/{emp_id}/review-draft")
    assert resp.status_code == 200
    data = resp.json()
    assert "highlights" in data
    assert "growth_areas" in data
    assert "risks" in data
    assert "summary" in data
    assert data["generated_by"] == "template"


@pytest.mark.asyncio
async def test_delete_employee_data(client):
    """DELETE /employees/{id}/data should remove all data."""
    await client.post("/sync/run")
    emps = (await client.get("/employees")).json()
    emp_id = emps[0]["id"]

    resp = await client.delete(f"/employees/{emp_id}/data")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    # Employee should no longer appear in active list
    emps_after = (await client.get("/employees")).json()
    ids_after = [e["id"] for e in emps_after]
    assert emp_id not in ids_after


@pytest.mark.asyncio
async def test_settings_get_and_update(client):
    """Settings round-trip."""
    # Get defaults
    resp = await client.get("/settings")
    assert resp.status_code == 200

    # Update
    resp = await client.post("/settings", json={"working_hours_start": 8, "timezone": "UTC"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["working_hours_start"] == 8
    assert data["timezone"] == "UTC"
