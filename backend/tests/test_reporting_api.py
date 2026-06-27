import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models.recon_exception import ReconException

TENANT = "reporting-test-tenant"
HDR = {"X-Tenant-ID": TENANT}
OTHER_TENANT = "reporting-other-tenant"


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def seed(client):
    db = SessionLocal()
    rows = [
        ReconException(tenant_id=TENANT, exception_type="Missing GL",     status="Open",     amount_difference=100.0),
        ReconException(tenant_id=TENANT, exception_type="Missing GL",     status="Open",     amount_difference=50.0),
        ReconException(tenant_id=TENANT, exception_type="Amount Mismatch",status="Resolved", amount_difference=25.0),
        ReconException(tenant_id=OTHER_TENANT, exception_type="Duplicate",status="Open",     amount_difference=999.0),
    ]
    for r in rows:
        db.add(r)
    db.commit()
    db.close()
    yield
    # cleanup
    db = SessionLocal()
    db.query(ReconException).filter(ReconException.tenant_id.in_([TENANT, OTHER_TENANT])).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_summary_structure(client):
    res = client.get("/reporting/summary", headers=HDR)
    assert res.status_code == 200
    data = res.json()
    assert "total_exceptions" in data
    assert "total_resolved" in data
    assert "total_amount_difference" in data
    assert "by_status" in data
    assert "by_type" in data


def test_summary_counts(client):
    res = client.get("/reporting/summary", headers=HDR)
    data = res.json()
    assert data["total_exceptions"] == 3
    assert data["total_resolved"] == 1
    assert abs(data["total_amount_difference"] - 175.0) < 0.01

    statuses = {s["status"]: s["count"] for s in data["by_status"]}
    assert statuses["Open"] == 2
    assert statuses["Resolved"] == 1


def test_summary_tenant_isolation(client):
    res = client.get("/reporting/summary", headers=HDR)
    data = res.json()
    # The OTHER_TENANT's $999 row must not appear in this tenant's totals.
    assert data["total_amount_difference"] < 999.0
    # only our 3 rows
    assert data["total_exceptions"] == 3
