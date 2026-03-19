from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, email: str, password: str = "testpassword") -> dict[str, str]:
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_client(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/clients",
        json={"name": "Acme Corp", "contact_email": "admin@acme.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Corp"
    assert data["id"] is not None


def test_list_clients(client: TestClient, auth_headers: dict) -> None:
    client.post("/clients", json={"name": "Alpha", "contact_email": "a@a.com"}, headers=auth_headers)
    client.post("/clients", json={"name": "Beta", "contact_email": "b@b.com"}, headers=auth_headers)
    resp = client.get("/clients", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_client_isolation(client: TestClient, auth_headers: dict) -> None:
    """User B must not be able to see or access User A's clients."""
    # User A creates a client
    resp = client.post(
        "/clients",
        json={"name": "Secret Corp", "contact_email": "secret@corp.com"},
        headers=auth_headers,
    )
    client_id = resp.json()["id"]

    # User B registers and logs in
    user_b_headers = _register_and_login(client, "userb@example.com")

    # User B's list must be empty
    resp = client.get("/clients", headers=user_b_headers)
    assert resp.status_code == 200
    assert resp.json() == []

    # User B must get 404 when accessing User A's client directly
    resp = client.get(f"/clients/{client_id}", headers=user_b_headers)
    assert resp.status_code == 404
