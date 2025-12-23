"""
API versioning and contract tests.
"""

from fastapi.testclient import TestClient

from nagatha_core.main import app


def test_ping_v1():
    """Ensure v1 ping endpoint is available."""
    with TestClient(app) as client:
        response = client.get("/api/v1/ping")

    assert response.status_code == 200
    payload = response.json()
    assert "request_id" in payload
    assert payload["data"]["status"] == "healthy"


def test_legacy_ping_deprecated_headers():
    """Legacy ping should include deprecation headers."""
    with TestClient(app) as client:
        response = client.get("/ping")

    assert response.status_code == 200
    assert response.headers.get("Deprecation") == "true"
    assert "Sunset" in response.headers
    assert response.headers.get("Link") == "</api/v1/ping>; rel=\"successor-version\""


def test_task_run_validation():
    """Invalid payloads should return consistent 422 schema."""
    with TestClient(app) as client:
        response = client.post("/api/v1/tasks/run", json={"kwargs": {"message": "hi"}})

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "validation_error"
    assert "request_id" in payload
    assert payload["details"]


def test_invalid_task_name():
    """Invalid task_name should return consistent 404 schema."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/tasks/run",
            json={"task_name": "missing.task", "kwargs": {}},
        )

    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == "http_error"
    assert "Task not found" in payload["message"]


def test_tasks_list():
    """Task listing should include registry allowlist."""
    with TestClient(app) as client:
        response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    payload = response.json()
    assert "request_id" in payload
    assert isinstance(payload["data"], list)
