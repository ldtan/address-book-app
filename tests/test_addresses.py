from uuid import uuid4

import pytest

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


async def test_crud_address(client):
    # Create
    r = await client.post("/api/addresses/", json=sample_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == sample_payload["name"]
    addr_uuid = data["uuid"]

    # Retrieve
    r = await client.get(f"/api/addresses/{addr_uuid}")
    assert r.status_code == 200
    assert r.json()["uuid"] == addr_uuid

    # List
    r = await client.get("/api/addresses/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Update
    r = await client.put(f"/api/addresses/{addr_uuid}", json={"name": "Home Updated"})
    assert r.status_code == 200
    assert r.json()["name"] == "Home Updated"

    # Delete
    r = await client.delete(f"/api/addresses/{addr_uuid}")
    assert r.status_code == 204

    # Not found after delete
    r = await client.get(f"/api/addresses/{addr_uuid}")
    assert r.status_code == 404


async def test_nearby_filter(client):
    # Create two addresses at different coordinates
    payload_a = sample_payload.copy()
    payload_a["name"] = "Location A"
    payload_a["latitude"] = 39.7817
    payload_a["longitude"] = -89.6501

    payload_b = sample_payload.copy()
    payload_b["name"] = "Location B"
    payload_b["latitude"] = 34.05
    payload_b["longitude"] = -118.25

    await client.post("/api/addresses/", json=payload_a)
    await client.post("/api/addresses/", json=payload_b)

    # Query near Location A (10 km radius)
    r = await client.get(
        "/api/addresses/", params={"lat": 39.7817, "lon": -89.6501, "radius": 10}
    )
    assert r.status_code == 200
    results = r.json()
    assert any(item["name"] == "Location A" for item in results)
    assert not any(item["name"] == "Location B" for item in results)


@pytest.mark.parametrize(
    "field, value, expected_msg",
    [
        ("country", "INVALID", "Invalid country code"),
        ("phone_number", "12345", "Phone number must start with '+'"),
        ("phone_number", "+123", "Invalid phone number format"),
        ("postal_code", "A", "Invalid postal code format"),
        ("latitude", 100.0, "less than or equal to 90"),
        ("longitude", 200.0, "less than or equal to 180"),
    ],
)
async def test_address_validation_errors(client, field, value, expected_msg):
    payload = sample_payload.copy()
    payload[field] = value
    response = await client.post("/api/addresses/", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(expected_msg in err["msg"] for err in errors)


async def test_pagination(client):
    for i in range(5):
        await client.post(
            "/api/addresses/", json={**sample_payload, "name": f"Addr {i}"}
        )

    response = await client.get("/api/addresses/", params={"skip": 2, "limit": 2})
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Addr 2"


async def test_query_parameter_limits_and_validation(client):
    await client.post(
        "/api/addresses/", json={**sample_payload, "name": "One"}
    )
    await client.post(
        "/api/addresses/", json={**sample_payload, "name": "Two"}
    )

    response = await client.get("/api/addresses/", params={"skip": -1})
    assert response.status_code == 422

    response = await client.get("/api/addresses/", params={"limit": 501})
    assert response.status_code == 422

    response = await client.get("/api/addresses/", params={"lat": 0, "lon": 0, "radius": -1})
    assert response.status_code == 422


async def test_filters_name_postal_code_and_country(client):
    await client.post(
        "/api/addresses/",
        json={
            **sample_payload,
            "name": "Home Central",
            "postal_code": "12345",
            "country": "US",
        },
    )
    await client.post(
        "/api/addresses/",
        json={
            **sample_payload,
            "name": "Work Central",
            "postal_code": "67890",
            "country": "ca",
        },
    )

    response = await client.get("/api/addresses/", params={"name": "Central"})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/api/addresses/", params={"postal_code": "12345"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["postal_code"] == "12345"

    response = await client.get("/api/addresses/", params={"country": "us"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["country"] == "US"


async def test_lat_lon_boundary_values(client):
    await client.post(
        "/api/addresses/",
        json={
            **sample_payload,
            "name": "Pole Station",
            "latitude": -90.0,
            "longitude": -180.0,
        },
    )

    response = await client.get(
        "/api/addresses/",
        params={"lat": -90.0, "lon": -180.0, "radius": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Pole Station"


async def test_non_geo_filters(client):
    await client.post(
        "/api/addresses/",
        json={
            **sample_payload,
            "name": "Office",
            "administrative_area": "NY",
            "country": "US",
        },
    )

    # Test Country Filter
    resp = await client.get("/api/addresses/", params={"country": "us"})
    assert len(resp.json()) == 1

    # Test Admin Area Filter
    resp = await client.get("/api/addresses/", params={"admin_area": "NY"})
    assert len(resp.json()) == 1


async def test_404_and_malformed_uuid(client):
    random_uuid = str(uuid4())

    # 404 paths
    assert (await client.get(f"/api/addresses/{random_uuid}")).status_code == 404
    assert (
        await client.put(f"/api/addresses/{random_uuid}", json={"name": "New"})
    ).status_code == 404
    assert (await client.delete(f"/api/addresses/{random_uuid}")).status_code == 404

    # Malformed UUID
    r = await client.get("/api/addresses/not-a-uuid")
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] == "uuid_parsing"


async def test_partial_update_semantics(client):
    res = await client.post(
        "/api/addresses/", json={**sample_payload, "notes": "Keep Me"}
    )
    addr_uuid = res.json()["uuid"]

    # Update only the name
    await client.put(f"/api/addresses/{addr_uuid}", json={"name": "New Name"})

    # Verify 'notes' was not cleared
    final = await client.get(f"/api/addresses/{addr_uuid}")
    assert final.json()["notes"] == "Keep Me"
    assert final.json()["name"] == "New Name"


async def test_duplicate_name_rejected(client):
    payload = sample_payload.copy()
    payload["name"] = "Unique Name"

    r = await client.post("/api/addresses/", json=payload)
    assert r.status_code == 201

    r = await client.post("/api/addresses/", json=payload)
    assert r.status_code == 409
    assert "already exists" in r.text.lower()
