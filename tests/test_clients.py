from fastapi.testclient import TestClient


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
