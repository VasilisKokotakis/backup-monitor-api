from fastapi.testclient import TestClient


def test_register_success(client: TestClient) -> None:
    resp = client.post("/auth/register", json={"email": "new@example.com", "password": "secret"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # never leak the hash


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {"email": "dupe@example.com", "password": "secret"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(client: TestClient) -> None:
    client.post("/auth/register", json={"email": "user@example.com", "password": "pass123"})
    resp = client.post("/auth/login", data={"username": "user@example.com", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client: TestClient) -> None:
    client.post("/auth/register", json={"email": "user@example.com", "password": "correct"})
    resp = client.post("/auth/login", data={"username": "user@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_protected_endpoint_without_token(client: TestClient) -> None:
    resp = client.get("/clients")
    assert resp.status_code == 401
