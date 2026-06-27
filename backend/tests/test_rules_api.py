import pytest
from fastapi.testclient import TestClient

from app.main import app


HDR   = {"X-Tenant-ID": "dev"}
HDR_A = {"X-Tenant-ID": "tenant-a"}
HDR_B = {"X-Tenant-ID": "tenant-b"}


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def test_create_rule_returns_201(client):
    body = {"name": "Penny tolerance", "amount_tolerance": 0.01, "date_tolerance_days": 0}
    resp = client.post("/rules", json=body, headers=HDR)

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Penny tolerance"
    assert data["amount_tolerance"] == 0.01
    assert data["is_active"] is True
    assert "id" in data


def test_create_rule_defaults(client):
    body = {"name": "Minimal rule"}
    resp = client.post("/rules", json=body, headers=HDR)

    assert resp.status_code == 201
    data = resp.json()
    assert data["amount_tolerance"] == 0.0
    assert data["date_tolerance_days"] == 0
    assert data["requires_approval"] is True


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def test_list_rules_returns_all(client):
    resp = client.get("/rules", headers=HDR)

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def test_update_rule(client):
    created = client.post("/rules", json={"name": "To update", "amount_tolerance": 0.0}, headers=HDR).json()
    rule_id = created["id"]

    update_body = {
        "name": "Updated rule",
        "amount_tolerance": 0.05,
        "date_tolerance_days": 2,
        "requires_approval": True,
        "is_active": True,
    }
    resp = client.put(f"/rules/{rule_id}", json=update_body, headers=HDR)

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated rule"
    assert data["amount_tolerance"] == 0.05
    assert data["date_tolerance_days"] == 2


def test_update_nonexistent_rule_returns_404(client):
    body = {
        "name": "x", "amount_tolerance": 0,
        "date_tolerance_days": 0, "requires_approval": True, "is_active": True,
    }
    resp = client.put("/rules/99999", json=body, headers=HDR)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Deactivation
# ---------------------------------------------------------------------------

def test_deactivated_rule_visible_in_list(client):
    created = client.post("/rules", json={"name": "To deactivate"}, headers=HDR).json()
    rule_id = created["id"]

    client.put(f"/rules/{rule_id}", json={
        "name": "To deactivate", "amount_tolerance": 0,
        "date_tolerance_days": 0, "requires_approval": True, "is_active": False,
    }, headers=HDR)

    rules = client.get("/rules", headers=HDR).json()
    ids = [r["id"] for r in rules]
    assert rule_id in ids

    deactivated = next(r for r in rules if r["id"] == rule_id)
    assert deactivated["is_active"] is False


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def test_delete_rule_returns_204(client):
    created = client.post("/rules", json={"name": "To delete"}, headers=HDR).json()
    rule_id = created["id"]

    resp = client.delete(f"/rules/{rule_id}", headers=HDR)
    assert resp.status_code == 204

    rules = client.get("/rules", headers=HDR).json()
    assert all(r["id"] != rule_id for r in rules)


def test_delete_nonexistent_rule_returns_404(client):
    resp = client.delete("/rules/99999", headers=HDR)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_create_rule_missing_name_returns_422(client):
    resp = client.post("/rules", json={"amount_tolerance": 0.01}, headers=HDR)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------------

def test_rules_are_tenant_isolated(client):
    client.post("/rules", json={"name": "Tenant A only rule"}, headers=HDR_A)

    resp_b = client.get("/rules", headers=HDR_B)
    names_b = [r["name"] for r in resp_b.json()]
    assert "Tenant A only rule" not in names_b


def test_cross_tenant_delete_returns_404(client):
    created = client.post("/rules", json={"name": "Protected rule"}, headers=HDR_A).json()
    rule_id = created["id"]

    resp = client.delete(f"/rules/{rule_id}", headers=HDR_B)
    assert resp.status_code == 404

    resp_a = client.get("/rules", headers=HDR_A)
    ids = [r["id"] for r in resp_a.json()]
    assert rule_id in ids
