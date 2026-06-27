from datetime import date
from decimal import Decimal

from app.services.matching_engine import TransactionRecord
from app.services.rule_matcher import RuleConfig, rule_based_match


def bank(amount: str, txn_date: str, eid: str = "TXN-1") -> TransactionRecord:
    return TransactionRecord(
        external_id=eid,
        amount=Decimal(amount),
        transaction_date=date.fromisoformat(txn_date),
        source="bank",
    )


def gl(amount: str, txn_date: str, eid: str = "TXN-1") -> TransactionRecord:
    return TransactionRecord(
        external_id=eid,
        amount=Decimal(amount),
        transaction_date=date.fromisoformat(txn_date),
        source="gl",
    )


LOOSE = RuleConfig(amount_tolerance=Decimal("0.01"), date_tolerance_days=2)


# ---------------------------------------------------------------------------
# No rules
# ---------------------------------------------------------------------------

def test_no_rules_returns_all_unmatched():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.00", "2024-01-15")]

    result = rule_based_match(b, g, rules=[])

    assert result.possible_matches == []
    assert result.unmatched_bank == b
    assert result.unmatched_gl == g


# ---------------------------------------------------------------------------
# Amount tolerance
# ---------------------------------------------------------------------------

def test_amount_within_tolerance_matches():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.005", "2024-01-15")]

    result = rule_based_match(b, g, [LOOSE])

    assert len(result.possible_matches) == 1
    assert result.unmatched_bank == []
    assert result.unmatched_gl == []


def test_amount_outside_tolerance_unmatched():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.02", "2024-01-15")]

    result = rule_based_match(b, g, [LOOSE])

    assert result.possible_matches == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl) == 1


def test_exact_amount_match_labelled_correctly():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.00", "2024-01-15")]

    result = rule_based_match(b, g, [LOOSE])

    assert "amount exact" in result.possible_matches[0].matched_rules


# ---------------------------------------------------------------------------
# Date tolerance
# ---------------------------------------------------------------------------

def test_date_within_tolerance_matches():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.00", "2024-01-17")]

    result = rule_based_match(b, g, [LOOSE])

    assert len(result.possible_matches) == 1


def test_date_outside_tolerance_unmatched():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.00", "2024-01-18")]

    result = rule_based_match(b, g, [LOOSE])

    assert result.possible_matches == []
    assert len(result.unmatched_bank) == 1


def test_exact_date_match_labelled_correctly():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.00", "2024-01-15")]

    result = rule_based_match(b, g, [LOOSE])

    assert "date exact" in result.possible_matches[0].matched_rules


def test_date_offset_label_shows_days():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.00", "2024-01-16")]

    result = rule_based_match(b, g, [LOOSE])

    assert any("day" in r for r in result.possible_matches[0].matched_rules)


# ---------------------------------------------------------------------------
# matched_rules audit trail
# ---------------------------------------------------------------------------

def test_matched_rules_is_non_empty_on_every_possible_match():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.005", "2024-01-16")]

    result = rule_based_match(b, g, [LOOSE])

    assert len(result.possible_matches[0].matched_rules) > 0


# ---------------------------------------------------------------------------
# Confidence score
# ---------------------------------------------------------------------------

def test_confidence_score_is_float_in_range():
    b = [bank("100.00", "2024-01-15")]
    g = [gl("100.005", "2024-01-17")]

    result = rule_based_match(b, g, [LOOSE])

    score = result.possible_matches[0].confidence_score
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_exact_amount_and_date_gives_higher_score_than_offset():
    b = [bank("100.00", "2024-01-15")]
    g_exact  = [gl("100.00",  "2024-01-15")]
    g_offset = [gl("100.005", "2024-01-17")]

    exact_score  = rule_based_match(b, g_exact,  [LOOSE]).possible_matches[0].confidence_score
    offset_score = rule_based_match(b, g_offset, [LOOSE]).possible_matches[0].confidence_score

    assert exact_score > offset_score


# ---------------------------------------------------------------------------
# Greedy allocation
# ---------------------------------------------------------------------------

def test_greedy_first_bank_claims_gl():
    b1 = bank("100.00", "2024-01-15", eid="B1")
    b2 = bank("100.00", "2024-01-15", eid="B2")
    g  = [gl("100.00", "2024-01-15")]

    result = rule_based_match([b1, b2], g, [LOOSE])

    assert len(result.possible_matches) == 1
    assert result.possible_matches[0].bank is b1
    assert len(result.unmatched_bank) == 1
    assert result.unmatched_bank[0] is b2


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_inputs():
    result = rule_based_match([], [], [LOOSE])

    assert result.possible_matches == []
    assert result.unmatched_bank == []
    assert result.unmatched_gl == []


def test_unmatched_gl_with_no_bank():
    g = [gl("100.00", "2024-01-15")]

    result = rule_based_match([], g, [LOOSE])

    assert result.possible_matches == []
    assert result.unmatched_gl == [g[0]]
