from fastapi.testclient import TestClient

from main import API_KEY, app

client = TestClient(app)
AUTH = {"X-API-Key": API_KEY}
NEW_DIAMOND = {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
               "price": 1800, "cost": 1100}


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Diamond Shop"}


def test_list_filters_by_max_price():
    response = client.get("/diamonds", params={"max_price": 3000})
    assert response.status_code == 200
    prices = [d["price"] for d in response.json()]
    assert prices == [326, 2376]


def test_get_one_hides_cost():
    response = client.get("/diamonds/3")
    assert response.status_code == 200
    body = response.json()
    assert body["cut"] == "Good"
    assert "cost" not in body


def test_missing_diamond_is_404():
    response = client.get("/diamonds/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Diamond 999 not found"}


def test_unknown_cut_is_422():
    response = client.get("/diamonds", params={"cut": "Excellent"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "cut"]


def test_create_needs_api_key():
    response = client.post("/diamonds", json=NEW_DIAMOND)
    assert response.status_code == 401


def test_create_rejects_bad_data():
    bad = NEW_DIAMOND | {"carat": -1}
    response = client.post("/diamonds", json=bad, headers=AUTH)
    assert response.status_code == 422


def test_create_update_delete():
    created = client.post("/diamonds", json=NEW_DIAMOND, headers=AUTH)
    assert created.status_code == 201
    new_id = created.json()["id"]

    updated = client.patch(f"/diamonds/{new_id}", json={"price": 1750}, headers=AUTH)
    assert updated.status_code == 200
    assert updated.json()["price"] == 1750

    deleted = client.delete(f"/diamonds/{new_id}", headers=AUTH)
    assert deleted.status_code == 204
    assert client.get(f"/diamonds/{new_id}").status_code == 404
