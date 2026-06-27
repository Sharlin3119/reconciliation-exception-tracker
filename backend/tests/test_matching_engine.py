from datetime import date
from decimal import Decimal

import pytest

from app.services.matching_engine import TransactionRecord, exact_match


def rec(external_id: str, amount: str, txn_date: str, source: str = "bank") -> TransactionRecord:
    return TransactionRecord(
        external_id=external_id,
        amount=Decimal(amount),
        transaction_date=date.fromisoformat(txn_date),
        source=source,
    )


# ---------------------------------------------------------------------------
# Basic cases
# ---------------------------------------------------------------------------

def test_single_exact_match():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl   = [rec("TXN-1", "100.00", "2024-01-15", source="gl")]

    result = exact_match(bank, gl)

    assert len(result.matched_pairs) == 1
    assert result.matched_pairs[0] == (bank[0], gl[0])
    assert result.unmatched_bank == []
    assert result.unmatched_gl == []


def test_no_match_different_amount():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl   = [rec("TXN-1", "200.00", "2024-01-15", source="gl")]

    result = exact_match(bank, gl)

    assert result.matched_pairs == []
    assert result.unmatched_bank == [bank[0]]
    assert result.unmatched_gl == [gl[0]]


def test_no_match_different_date():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl   = [rec("TXN-1", "100.00", "2024-01-16", source="gl")]

    result = exact_match(bank, gl)

    assert result.matched_pairs == []
    assert result.unmatched_bank == [bank[0]]
    assert result.unmatched_gl == [gl[0]]


def test_no_match_different_external_id():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl   = [rec("TXN-2", "100.00", "2024-01-15", source="gl")]

    result = exact_match(bank, gl)

    assert result.matched_pairs == []
    assert result.unmatched_bank == [bank[0]]
    assert result.unmatched_gl == [gl[0]]


def test_empty_both_sides():
    result = exact_match([], [])

    assert result.matched_pairs == []
    assert result.unmatched_bank == []
    assert result.unmatched_gl == []


def test_empty_bank():
    gl = [rec("TXN-1", "100.00", "2024-01-15", source="gl")]

    result = exact_match([], gl)

    assert result.matched_pairs == []
    assert result.unmatched_bank == []
    assert result.unmatched_gl == [gl[0]]


def test_empty_gl():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]

    result = exact_match(bank, [])

    assert result.matched_pairs == []
    assert result.unmatched_bank == [bank[0]]
    assert result.unmatched_gl == []


# ---------------------------------------------------------------------------
# Multiple records, partial matches
# ---------------------------------------------------------------------------

def test_multiple_records_some_match():
    bank = [
        rec("TXN-1", "100.00", "2024-01-15"),
        rec("TXN-2", "250.00", "2024-01-16"),
        rec("TXN-3", "999.99", "2024-01-17"),
    ]
    gl = [
        rec("TXN-1", "100.00", "2024-01-15", source="gl"),
        rec("TXN-3", "999.99", "2024-01-17", source="gl"),
        rec("TXN-9", "500.00", "2024-01-18", source="gl"),
    ]

    result = exact_match(bank, gl)

    matched_bank_ids = {b.external_id for b, _ in result.matched_pairs}
    assert matched_bank_ids == {"TXN-1", "TXN-3"}
    assert len(result.matched_pairs) == 2
    assert result.unmatched_bank == [bank[1]]
    assert result.unmatched_gl == [gl[2]]


# ---------------------------------------------------------------------------
# Duplicate-key handling
# ---------------------------------------------------------------------------

def test_duplicate_bank_keys_only_first_matches():
    b1 = rec("TXN-1", "100.00", "2024-01-15")
    b2 = rec("TXN-1", "100.00", "2024-01-15")
    gl = [rec("TXN-1", "100.00", "2024-01-15", source="gl")]

    result = exact_match([b1, b2], gl)

    assert len(result.matched_pairs) == 1
    assert result.matched_pairs[0][0] is b1
    assert result.unmatched_bank == [b2]
    assert result.unmatched_gl == []


def test_duplicate_gl_keys_only_first_matches():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    g1 = rec("TXN-1", "100.00", "2024-01-15", source="gl")
    g2 = rec("TXN-1", "100.00", "2024-01-15", source="gl")

    result = exact_match(bank, [g1, g2])

    assert len(result.matched_pairs) == 1
    assert result.matched_pairs[0][1] is g1
    assert result.unmatched_bank == []
    assert result.unmatched_gl == [g2]


def test_duplicate_keys_both_sides():
    b1 = rec("TXN-1", "100.00", "2024-01-15")
    b2 = rec("TXN-1", "100.00", "2024-01-15")
    g1 = rec("TXN-1", "100.00", "2024-01-15", source="gl")
    g2 = rec("TXN-1", "100.00", "2024-01-15", source="gl")

    result = exact_match([b1, b2], [g1, g2])

    assert len(result.matched_pairs) == 1
    assert result.matched_pairs[0] == (b1, g1)
    assert result.unmatched_bank == [b2]
    assert result.unmatched_gl == [g2]


def test_three_duplicate_bank_keys_two_unmatched():
    b1 = rec("TXN-1", "50.00", "2024-03-01")
    b2 = rec("TXN-1", "50.00", "2024-03-01")
    b3 = rec("TXN-1", "50.00", "2024-03-01")
    gl = [rec("TXN-1", "50.00", "2024-03-01", source="gl")]

    result = exact_match([b1, b2, b3], gl)

    assert len(result.matched_pairs) == 1
    assert result.unmatched_bank == [b2, b3]
    assert result.unmatched_gl == []


# ---------------------------------------------------------------------------
# Amount precision
# ---------------------------------------------------------------------------

def test_amount_precision_must_match_exactly():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl   = [rec("TXN-1", "100.001", "2024-01-15", source="gl")]

    result = exact_match(bank, gl)

    assert result.matched_pairs == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl) == 1
