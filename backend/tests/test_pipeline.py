from datetime import date
from decimal import Decimal
from typing import Optional

from app.services.matching_engine import TransactionRecord
from app.services.rule_matcher import RuleConfig
from app.services.pipeline import run_pipeline


def rec(eid: str, amount: str, txn_date: str, description: Optional[str] = None, source: str = "bank") -> TransactionRecord:
    return TransactionRecord(
        external_id=eid,
        amount=Decimal(amount),
        transaction_date=date.fromisoformat(txn_date),
        source=source,
        description=description,
    )


def gl(eid: str, amount: str, txn_date: str, description: Optional[str] = None) -> TransactionRecord:
    return rec(eid, amount, txn_date, description=description, source="gl")


RULE = RuleConfig(amount_tolerance=Decimal("0.05"), date_tolerance_days=1)


# ---------------------------------------------------------------------------
# Stage ordering: exact before fuzzy before rule-based
# ---------------------------------------------------------------------------

def test_exact_match_never_reaches_fuzzy_or_rule():
    bank = [rec("TXN-1", "100.00", "2024-01-15", description="ACH vendor payment")]
    gl_  = [gl("TXN-1",  "100.00", "2024-01-15", description="ACH vendor payment")]

    result = run_pipeline(bank, gl_, rules=[RULE])

    assert len(result.confirmed_matches) == 1
    assert result.probable_matches == []
    assert result.possible_matches  == []
    assert result.unmatched_bank    == []
    assert result.unmatched_gl      == []


def test_fuzzy_match_never_reaches_rule_based():
    bank = [rec("TXN-1", "100.00", "2024-01-15", description="ACH vendor payment")]
    gl_  = [gl("TXN-X",  "200.00", "2024-02-01", description="ACH vendor payment")]

    result = run_pipeline(bank, gl_, rules=[RULE])

    assert result.confirmed_matches == []
    assert len(result.probable_matches) == 1
    assert result.possible_matches  == []
    assert result.unmatched_bank    == []
    assert result.unmatched_gl      == []


def test_rule_based_runs_on_leftover_after_exact_and_fuzzy():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl_  = [gl("TXN-X",  "100.04", "2024-01-16")]

    result = run_pipeline(bank, gl_, rules=[RULE])

    assert result.confirmed_matches == []
    assert result.probable_matches  == []
    assert len(result.possible_matches) == 1
    assert result.unmatched_bank == []
    assert result.unmatched_gl   == []


def test_all_three_stages_fire_independently():
    bank = [
        rec("TXN-A", "100.00", "2024-01-15"),                          # exact
        rec("TXN-B", "200.00", "2024-01-15", description="Payroll"),   # fuzzy
        rec("TXN-C", "300.00", "2024-01-15"),                          # rule-based
    ]
    gl_ = [
        gl("TXN-A", "100.00", "2024-01-15"),                           # exact
        gl("TXN-X", "200.00", "2024-01-15", description="Payroll"),    # fuzzy
        gl("TXN-Y", "300.03", "2024-01-16"),                           # rule-based
    ]

    result = run_pipeline(bank, gl_, rules=[RULE])

    assert len(result.confirmed_matches) == 1
    assert len(result.probable_matches)  == 1
    assert len(result.possible_matches)  == 1
    assert result.unmatched_bank == []
    assert result.unmatched_gl   == []


# ---------------------------------------------------------------------------
# Confidence scores
# ---------------------------------------------------------------------------

def test_confirmed_match_confidence_is_one():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl_  = [gl("TXN-1",  "100.00", "2024-01-15")]

    result = run_pipeline(bank, gl_)

    assert result.confirmed_matches[0].confidence_score == 1.0


def test_probable_match_confidence_derived_from_similarity():
    bank = [rec("TXN-X", "100.00", "2024-01-15", description="ACH vendor payment")]
    gl_  = [gl("TXN-Y",  "999.00", "2024-02-01", description="ACH vendor payment")]

    result = run_pipeline(bank, gl_)

    score = result.probable_matches[0].confidence_score
    assert 0.0 < score <= 1.0


def test_possible_match_confidence_is_float_in_range():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl_  = [gl("TXN-X",  "100.04", "2024-01-16")]

    result = run_pipeline(bank, gl_, rules=[RULE])

    score = result.possible_matches[0].confidence_score
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# No rules — rule stage is a no-op, leftovers stay unmatched
# ---------------------------------------------------------------------------

def test_no_rules_leaves_unmatched_after_fuzzy():
    bank = [rec("TXN-1", "100.00", "2024-01-15")]
    gl_  = [gl("TXN-X",  "100.04", "2024-01-16")]

    result = run_pipeline(bank, gl_, rules=[])

    assert result.possible_matches == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl)   == 1


# ---------------------------------------------------------------------------
# Empty inputs
# ---------------------------------------------------------------------------

def test_empty_inputs():
    result = run_pipeline([], [], rules=[RULE])

    assert result.confirmed_matches == []
    assert result.probable_matches  == []
    assert result.possible_matches  == []
    assert result.unmatched_bank    == []
    assert result.unmatched_gl      == []
