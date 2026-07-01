import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models.recon_exception import ReconException

TENANT = "files-matching-test-tenant"
HDR = {"X-Tenant-ID": TENANT}

# E1 appears on both sides (exact match); E2 (bank-only) and E3 (gl-only) are
# unmatched -> 2 exceptions. Descriptions differ enough not to fuzzy-match.
CSV = (
    "external_id,date,amount,description,source\n"
    "E1,2026-01-01,100.00,Coffee,bank\n"
    "E1,2026-01-01,100.00,Coffee,gl\n"
    "E2,2026-01-02,50.00,Lunch,bank\n"
    "E3,2026-01-03,75.00,Books,gl\n"
)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    db = SessionLocal()
    db.query(ReconException).filter(ReconException.tenant_id == TENANT).delete(
        synchronize_session=False
    )
    db.commit()
    db.close()


def test_run_matching_from_upload(client):
    files = [("files", ("recon.csv", io.BytesIO(CSV.encode()), "text/csv"))]
    res = client.post("/files/run_matching_from_upload", files=files, headers=HDR)
    assert res.status_code == 200

    data = res.json()
    assert set(data) == {"total_transactions", "matched", "exceptions_created", "run_id"}
    assert data["total_transactions"] == 4
    assert data["matched"] == 1
    assert data["exceptions_created"] == 2
    assert data["run_id"] is None


def test_exceptions_visible_via_existing_apis(client):
    # /exceptions (Exception Queue) sees the created exceptions for this tenant
    rows = client.get("/exceptions", headers=HDR).json()
    assert len(rows) == 2
    assert all(r["exception_type"] == "Unmatched" for r in rows)

    # /reporting/summary (Dashboard KPIs) counts them too
    summary = client.get("/reporting/summary", headers=HDR).json()
    assert summary["total_exceptions"] == 2
    assert abs(summary["total_amount_difference"] - 125.0) < 0.01
