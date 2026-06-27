from typing import Optional

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def bank(eid: str, amount: str, txn_date: str, description: Optional[str] = None) -> dict:
    r = {"external_id": eid, "amount": amount, "transaction_date": txn_date, "source": "bank"}
    if description is not None:
        r["description"] = description
    return r


def gl(eid: str, amount: str, txn_date: str, description: Optional[str] = None) -> dict:
    r = {"external_id": eid, "amount": amount, "transaction_date": txn_date, "source": "gl"}
    if description is not None:
        r["description"] = description
    return r


LOOSE_RULE = {"amount_tolerance": "0.05", "date_tolerance_days": 1}


# ---------------------------------------------------------------------------
# Response shape
# ---------------------------------------------------------------------------

def test_pipeline_response_has_all_five_fields(client):
    body = {"bank_records": [], "gl_records": []}
    resp = client.post("/matching/run", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert "confirmed_matches" in data
    assert "probable_matches"  in data
    assert "possible_matches"  in data
    assert "unmatched_bank"    in data
    assert "unmatched_gl"      in data


# ---------------------------------------------------------------------------
# Confirmed match
# ---------------------------------------------------------------------------

def test_exact_match_lands_in_confirmed(client):
    body = {
        "bank_records": [bank("TXN-1", "100.00", "2024-01-15")],
        "gl_records":   [gl("TXN-1",  "100.00", "2024-01-15")],
    }
    resp = client.post("/matching/run", json=body)

    data = resp.json()
    assert len(data["confirmed_matches"]) == 1
    assert data["confirmed_matches"][0]["confidence_score"] == 1.0
    assert data["probable_matches"] == []
    assert data["possible_matches"] == []


# ---------------------------------------------------------------------------
# Probable match
# ---------------------------------------------------------------------------

def test_fuzzy_match_lands_in_probable(client):
    body = {
        "bank_records": [bank("TXN-X", "100.00", "2024-01-15", description="ACH vendor payment")],
        "gl_records":   [gl("TXN-Y",   "999.00", "2024-02-01", description="ACH vendor payment")],
    }
    resp = client.post("/matching/run", json=body)

    data = resp.json()
    assert data["confirmed_matches"] == []
    assert len(data["probable_matches"]) == 1
    pair = data["probable_matches"][0]
    assert "similarity_score" in pair
    assert "confidence_score" in pair
    assert 0 < pair["confidence_score"] <= 1.0


# ---------------------------------------------------------------------------
# Possible match
# ---------------------------------------------------------------------------

def test_rule_match_lands_in_possible(client):
    body = {
        "bank_records": [bank("TXN-1", "100.00", "2024-01-15")],
        "gl_records":   [gl("TXN-X",   "100.04", "2024-01-16")],
        "rules": [LOOSE_RULE],
    }
    resp = client.post("/matching/run", json=body)

    data = resp.json()
    assert data["confirmed_matches"] == []
    assert data["probable_matches"]  == []
    assert len(data["possible_matches"]) == 1
    pair = data["possible_matches"][0]
    assert "matched_rules" in pair
    assert len(pair["matched_rules"]) > 0
    assert 0 < pair["confidence_score"] <= 1.0


# ---------------------------------------------------------------------------
# All three stages in one request
# ---------------------------------------------------------------------------

def test_all_three_categories_in_one_request(client):
    body = {
        "bank_records": [
            bank("TXN-A", "100.00", "2024-01-15"),
            bank("TXN-B", "200.00", "2024-01-15", description="Payroll run"),
            bank("TXN-C", "300.00", "2024-01-15"),
        ],
        "gl_records": [
            gl("TXN-A", "100.00", "2024-01-15"),
            gl("TXN-X", "200.00", "2024-01-15", description="Payroll run"),
            gl("TXN-Y", "300.03", "2024-01-16"),
        ],
        "rules": [LOOSE_RULE],
    }
    resp = client.post("/matching/run", json=body)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["confirmed_matches"]) == 1
    assert len(data["probable_matches"])  == 1
    assert len(data["possible_matches"])  == 1
    assert data["unmatched_bank"] == []
    assert data["unmatched_gl"]   == []


# ---------------------------------------------------------------------------
# Unmatched
# ---------------------------------------------------------------------------

def test_unmatched_records_surfaced_correctly(client):
    body = {
        "bank_records": [bank("TXN-1", "100.00", "2024-01-15")],
        "gl_records":   [gl("TXN-2",   "999.00", "2024-06-01")],
    }
    resp = client.post("/matching/run", json=body)

    data = resp.json()
    assert data["confirmed_matches"] == []
    assert data["probable_matches"]  == []
    assert data["possible_matches"]  == []
    assert len(data["unmatched_bank"]) == 1
    assert len(data["unmatched_gl"])   == 1


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_invalid_body_returns_422(client):
    resp = client.post("/matching/run", json={"bank_records": "bad", "gl_records": []})
    assert resp.status_code == 422


def test_invalid_rule_returns_422(client):
    body = {
        "bank_records": [],
        "gl_records": [],
        "rules": [{"date_tolerance_days": "not-an-int"}],
    }
    resp = client.post("/matching/run", json=body)
    assert resp.status_code == 422
