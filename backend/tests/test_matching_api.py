import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def rec(external_id: str, amount: str, txn_date: str, source: str = "bank") -> dict:
    return {
        "external_id": external_id,
        "amount": amount,
        "transaction_date": txn_date,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Response shape
# ---------------------------------------------------------------------------

def test_exact_match_response_shape(client):
    body = {
        "bank_records": [rec("TXN-1", "100.00", "2024-01-15")],
        "gl_records":   [rec("TXN-1", "100.00", "2024-01-15", source="gl")],
    }

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matched_pairs"]) == 1
    assert "bank" in data["matched_pairs"][0]
    assert "gl" in data["matched_pairs"][0]
    assert data["unmatched_bank"] == []
    assert data["unmatched_gl"] == []


# ---------------------------------------------------------------------------
# Unmatched records
# ---------------------------------------------------------------------------

def test_unmatched_bank_record(client):
    body = {
        "bank_records": [rec("TXN-1", "100.00", "2024-01-15")],
        "gl_records":   [],
    }

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert data["matched_pairs"] == []
    assert len(data["unmatched_bank"]) == 1
    assert data["unmatched_bank"][0]["external_id"] == "TXN-1"
    assert data["unmatched_gl"] == []


def test_unmatched_gl_record(client):
    body = {
        "bank_records": [],
        "gl_records":   [rec("TXN-1", "100.00", "2024-01-15", source="gl")],
    }

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert data["matched_pairs"] == []
    assert data["unmatched_bank"] == []
    assert len(data["unmatched_gl"]) == 1
    assert data["unmatched_gl"][0]["external_id"] == "TXN-1"


# ---------------------------------------------------------------------------
# Duplicate keys
# ---------------------------------------------------------------------------

def test_duplicate_bank_keys(client):
    body = {
        "bank_records": [
            rec("TXN-1", "100.00", "2024-01-15"),
            rec("TXN-1", "100.00", "2024-01-15"),
        ],
        "gl_records": [rec("TXN-1", "100.00", "2024-01-15", source="gl")],
    }

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matched_pairs"]) == 1
    assert len(data["unmatched_bank"]) == 1
    assert data["unmatched_gl"] == []


def test_duplicate_gl_keys(client):
    body = {
        "bank_records": [rec("TXN-1", "100.00", "2024-01-15")],
        "gl_records": [
            rec("TXN-1", "100.00", "2024-01-15", source="gl"),
            rec("TXN-1", "100.00", "2024-01-15", source="gl"),
        ],
    }

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matched_pairs"]) == 1
    assert data["unmatched_bank"] == []
    assert len(data["unmatched_gl"]) == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_request(client):
    body = {"bank_records": [], "gl_records": []}

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert data["matched_pairs"] == []
    assert data["unmatched_bank"] == []
    assert data["unmatched_gl"] == []


def test_invalid_body_returns_422(client):
    body = {"bank_records": "not-a-list", "gl_records": []}

    resp = client.post("/matching/exact", json=body)

    assert resp.status_code == 422
