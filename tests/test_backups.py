import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_id(client: TestClient, auth_headers: dict) -> int:
    resp = client.post(
        "/clients",
        json={"name": "Acme Corp", "contact_email": "admin@acme.com"},
        headers=auth_headers,
    )
    return resp.json()["id"]


def test_create_backup_job(client: TestClient, auth_headers: dict, client_id: int) -> None:
    resp = client.post(
        f"/clients/{client_id}/backups",
        json={"source": "Microsoft 365", "status": "SUCCESS", "size_bytes": 1024},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["source"] == "Microsoft 365"
    assert data["status"] == "SUCCESS"
    assert data["client_id"] == client_id


def test_list_backup_jobs(client: TestClient, auth_headers: dict, client_id: int) -> None:
    for source in ["Microsoft 365", "Salesforce", "Google Workspace"]:
        client.post(
            f"/clients/{client_id}/backups",
            json={"source": source, "status": "SUCCESS"},
            headers=auth_headers,
        )
    resp = client.get(f"/clients/{client_id}/backups", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_backup_summary(client: TestClient, auth_headers: dict, client_id: int) -> None:
    client.post(f"/clients/{client_id}/backups", json={"source": "M365", "status": "SUCCESS"}, headers=auth_headers)
    client.post(f"/clients/{client_id}/backups", json={"source": "M365", "status": "FAILED", "error_message": "Timeout"}, headers=auth_headers)
    client.post(f"/clients/{client_id}/backups", json={"source": "M365", "status": "RUNNING"}, headers=auth_headers)

    resp = client.get("/backups/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["by_status"]["FAILED"] == 1
    assert data["latest_failure"]["error_message"] == "Timeout"


def test_backup_job_unknown_client(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/clients/9999/backups",
        json={"source": "M365", "status": "PENDING"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_backup_job_invalid_status(client: TestClient, auth_headers: dict, client_id: int) -> None:
    resp = client.post(
        f"/clients/{client_id}/backups",
        json={"source": "M365", "status": "INVALID_STATUS"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_backup_summary_cross_user_isolation(client: TestClient, auth_headers: dict, client_id: int) -> None:
    # User A creates a FAILED backup job
    client.post(
        f"/clients/{client_id}/backups",
        json={"source": "M365", "status": "FAILED", "error_message": "User A error"},
        headers=auth_headers,
    )

    # User B registers, logs in, and checks their own summary
    client.post("/auth/register", json={"email": "userb@example.com", "password": "password123"})
    resp = client.post("/auth/login", data={"username": "userb@example.com", "password": "password123"})
    user_b_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    summary = client.get("/backups/summary", headers=user_b_headers).json()
    assert summary["total"] == 0
    assert summary["latest_failure"] is None
