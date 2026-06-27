from datetime import date
from decimal import Decimal
from typing import Optional

from app.services.matching_engine import TransactionRecord
from app.services.fuzzy_matcher import fuzzy_match


def rec(description: Optional[str] = None, source: str = "bank") -> TransactionRecord:
    return TransactionRecord(
        external_id="TXN-1",
        amount=Decimal("100.00"),
        transaction_date=date(2024, 1, 15),
        source=source,
        description=description,
    )


# ---------------------------------------------------------------------------
# Basic match / no-match
# ---------------------------------------------------------------------------

def test_identical_descriptions_match():
    bank = [rec("ACH payment from vendor")]
    gl   = [rec("ACH payment from vendor", source="gl")]

    result = fuzzy_match(bank, gl)

    assert len(result.probable_matches) == 1
    assert result.unmatched_bank == []
    assert result.unmatched_gl == []


def test_very_different_descriptions_unmatched():
    # fuzz.ratio("ACH payment from vendor", "refund processed") == 35.9
    bank = [rec("ACH payment from vendor")]
    gl   = [rec("refund processed", source="gl")]

    result = fuzzy_match(bank, gl)

    assert result.probable_matches == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl) == 1


# ---------------------------------------------------------------------------
# None / empty descriptions
# ---------------------------------------------------------------------------

def test_none_description_unmatched():
    bank = [rec(None)]
    gl   = [rec("ACH payment from vendor", source="gl")]

    result = fuzzy_match(bank, gl)

    assert result.probable_matches == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl) == 1


def test_empty_description_unmatched():
    bank = [rec("")]
    gl   = [rec("ACH payment from vendor", source="gl")]

    result = fuzzy_match(bank, gl)

    assert result.probable_matches == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl) == 1


# ---------------------------------------------------------------------------
# similarity_score on the result
# ---------------------------------------------------------------------------

def test_similarity_score_present_and_in_range():
    bank = [rec("ACH payment from vendor")]
    gl   = [rec("ACH payment from vendor", source="gl")]

    result = fuzzy_match(bank, gl)

    score = result.probable_matches[0].similarity_score
    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# Threshold boundary
# ---------------------------------------------------------------------------

def test_custom_threshold_match():
    # fuzz.ratio("hello", "hello!") == 90.9 — above 85, below 100
    bank = [rec("hello")]
    gl   = [rec("hello!", source="gl")]

    above = fuzzy_match(bank, gl, threshold=85)
    assert len(above.probable_matches) == 1

    below = fuzzy_match(bank, gl, threshold=100)
    assert below.probable_matches == []
    assert len(below.unmatched_bank) == 1
    assert len(below.unmatched_gl) == 1


def test_below_default_threshold_unmatched():
    # fuzz.ratio("ACH payment January", "ACH payment February") == 82.1 — below 85
    bank = [rec("ACH payment January")]
    gl   = [rec("ACH payment February", source="gl")]

    result = fuzzy_match(bank, gl)

    assert result.probable_matches == []
    assert len(result.unmatched_bank) == 1
    assert len(result.unmatched_gl) == 1


# ---------------------------------------------------------------------------
# Greedy: first bank record wins
# ---------------------------------------------------------------------------

def test_greedy_first_bank_record_wins():
    b1 = rec("ACH payment from vendor")
    b2 = rec("ACH payment from vendor")
    gl = [rec("ACH payment from vendor", source="gl")]

    result = fuzzy_match([b1, b2], gl)

    assert len(result.probable_matches) == 1
    assert result.probable_matches[0].bank is b1
    assert len(result.unmatched_bank) == 1
    assert result.unmatched_bank[0] is b2
    assert result.unmatched_gl == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_both_sides():
    result = fuzzy_match([], [])

    assert result.probable_matches == []
    assert result.unmatched_bank == []
    assert result.unmatched_gl == []


def test_empty_bank_gl_goes_unmatched():
    gl = [rec("ACH payment from vendor", source="gl")]

    result = fuzzy_match([], gl)

    assert result.probable_matches == []
    assert result.unmatched_bank == []
    assert result.unmatched_gl == [gl[0]]
