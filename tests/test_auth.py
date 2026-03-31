from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_success(client: TestClient) -> None:
    resp = client.post("/auth/register", json={"email": "new@example.com", "password": "secret123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # never leak the hash


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {"email": "dupe@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_password_too_short(client: TestClient) -> None:
    resp = client.post("/auth/register", json={"email": "new@example.com", "password": "short"})
    assert resp.status_code == 422


def test_login_success(client: TestClient) -> None:
    client.post("/auth/register", json={"email": "user@example.com", "password": "pass1234"})
    resp = client.post("/auth/login", data={"username": "user@example.com", "password": "pass1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client: TestClient) -> None:
    client.post("/auth/register", json={"email": "user@example.com", "password": "correctpass"})
    resp = client.post("/auth/login", data={"username": "user@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_protected_endpoint_without_token(client: TestClient) -> None:
    resp = client.get("/clients")
    assert resp.status_code == 401


def test_malformed_token_is_rejected(client: TestClient) -> None:
    resp = client.get("/clients", headers={"Authorization": "Bearer not.a.valid.token"})
    assert resp.status_code == 401


def test_expired_token_is_rejected(client: TestClient) -> None:
    from datetime import datetime, timedelta, timezone
    from jose import jwt

    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(expired_payload, "test-secret-key-not-for-production", algorithm="HS256")
    resp = client.get("/clients", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
