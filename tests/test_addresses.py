sample_payload = {
    "name": "Home",
    "street": "123 Main St",
    "sub_locality": "Downtown",
    "locality": "Springfield",
    "administrative_area": "IL",
    "postal_code": "62701",
    "country": "US",
    "latitude": 39.7817,
    "longitude": -89.6501,
    "notes": "Primary residence",
    "email": "example@example.com",
    "phone_number": "+12175551234",
    "website": "https://example.com",
}


def test_crud_address(client):
    # Create
    r = client.post("/api/addresses", json=sample_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == sample_payload["name"]
    addr_uuid = data["uuid"]

    # Retrieve
    r = client.get(f"/api/addresses/{addr_uuid}")
    assert r.status_code == 200
    assert r.json()["uuid"] == addr_uuid

    # List
    r = client.get("/api/addresses")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Update
    r = client.put(f"/api/addresses/{addr_uuid}", json={"name": "Home Updated"})
    assert r.status_code == 200
    assert r.json()["name"] == "Home Updated"

    # Delete
    r = client.delete(f"/api/addresses/{addr_uuid}")
    assert r.status_code == 204

    # Not found after delete
    r = client.get(f"/api/addresses/{addr_uuid}")
    assert r.status_code == 404


def test_nearby_filter(client):
    # Create two addresses at different coordinates
    payload_a = sample_payload.copy()
    payload_a["name"] = "Location A"
    payload_a["latitude"] = 39.7817
    payload_a["longitude"] = -89.6501

    payload_b = sample_payload.copy()
    payload_b["name"] = "Location B"
    payload_b["latitude"] = 34.05
    payload_b["longitude"] = -118.25

    r = client.post("/api/addresses", json=payload_a)
    assert r.status_code == 201
    r = client.post("/api/addresses", json=payload_b)
    assert r.status_code == 201

    # Query near Location A (10 km radius)
    r = client.get(
        "/api/addresses", params={"lat": 39.7817, "lon": -89.6501, "radius": 10}
    )
    assert r.status_code == 200
    results = r.json()
    assert any(item["name"] == "Location A" for item in results)
    assert not any(item["name"] == "Location B" for item in results)


def test_invalid_country_code(client):
    payload = sample_payload.copy()
    payload["name"] = "Bad Country"
    payload["country"] = "XX"

    r = client.post("/api/addresses", json=payload)
    # Pydantic validation errors are returned as 422 Unprocessable Entity
    assert r.status_code == 422
    assert any(
        "country" in err.get("loc", []) or "country" in err.get("msg", "")
        for err in r.json().get("detail", [])
    )


def test_invalid_phone_number(client):
    payload = sample_payload.copy()
    payload["name"] = "Bad Phone"
    payload["phone_number"] = "12345"

    r = client.post("/api/addresses", json=payload)
    assert r.status_code == 422
    assert any(
        "phone_number" in err.get("loc", []) or "phone" in err.get("msg", "").lower()
        for err in r.json().get("detail", [])
    )


def test_invalid_postal_code(client):
    payload = sample_payload.copy()
    payload["name"] = "Bad Postal"
    payload["postal_code"] = "!@#$"

    r = client.post("/api/addresses", json=payload)
    assert r.status_code == 422
    assert any(
        "postal_code" in err.get("loc", []) or "postal" in err.get("msg", "").lower()
        for err in r.json().get("detail", [])
    )


def test_duplicate_name_rejected(client):
    payload = sample_payload.copy()
    payload["name"] = "Unique Name"

    r = client.post("/api/addresses", json=payload)
    assert r.status_code == 201

    # Attempt to create another with same name
    r = client.post("/api/addresses", json=payload)
    assert r.status_code == 400
    assert "already exists" in r.text.lower()
