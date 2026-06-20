"""Integration tests for the Grocery Delivery Platform API.

Uses a throwaway SQLite file so the test run never touches dev data.
"""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Point the app at an isolated DB before importing it.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

from app.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def _startup():
    with TestClient(app):  # triggers startup (create tables + seed)
        yield


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_inventory_listed():
    r = client.get("/api/inventory")
    assert r.status_code == 200
    skus = {p["sku"] for p in r.json()}
    assert "MILK-1L" in skus


def test_place_order_and_track():
    r = client.post(
        "/api/orders",
        json={
            "customer_name": "Test User",
            "address": "1 Test Rd",
            "items": [{"sku": "MILK-1L", "quantity": 2}],
        },
    )
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["status"] == "CONFIRMED"
    assert order["total"] == pytest.approx(2.40)

    track = client.get(f"/api/orders/{order['id']}")
    assert track.status_code == 200
    assert track.json()["id"] == order["id"]


def test_insufficient_stock_rejected():
    r = client.post(
        "/api/orders",
        json={
            "customer_name": "Greedy",
            "address": "9 Bulk Ave",
            "items": [{"sku": "RICE-5KG", "quantity": 99999}],
        },
    )
    assert r.status_code == 400


def test_full_delivery_lifecycle():
    placed = client.post(
        "/api/orders",
        json={
            "customer_name": "Lifecycle",
            "address": "2 Flow St",
            "items": [{"sku": "BREAD-WHT", "quantity": 1}],
        },
    ).json()
    oid = placed["id"]

    assigned = client.post(f"/api/orders/{oid}/assign", json={}).json()
    assert assigned["status"] == "ASSIGNED"
    assert assigned["delivery"]["agent_name"]

    out = client.patch(
        f"/api/orders/{oid}/status", json={"status": "OUT_FOR_DELIVERY"}
    ).json()
    assert out["status"] == "OUT_FOR_DELIVERY"

    done = client.patch(
        f"/api/orders/{oid}/status", json={"status": "DELIVERED"}
    ).json()
    assert done["status"] == "DELIVERED"


def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "grocery_http_requests_total" in r.text
