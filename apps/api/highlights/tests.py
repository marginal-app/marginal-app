def test_ping_requires_token(client) -> None:
    response = client.get("/api/ping")
    assert response.status_code == 401


def test_ping_ok_with_dev_token(client) -> None:
    response = client.get("/api/ping", headers={"Authorization": "Bearer dev-token"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
