from app.services.match_types import (
    exact_confidence,
    fuzzy_confidence,
    rule_confidence,
)


def test_exact_confidence_is_always_one():
    assert exact_confidence() == 1.0


def test_fuzzy_confidence_scales_from_similarity():
    assert fuzzy_confidence(100.0) == 1.0
    assert fuzzy_confidence(85.0)  == 0.85
    assert fuzzy_confidence(0.0)   == 0.0


def test_fuzzy_confidence_rounds_to_four_places():
    # 91 / 100 = 0.91 exactly; check rounding doesn't explode on floats
    result = fuzzy_confidence(91.0)
    assert result == 0.91


def test_rule_confidence_clamps_to_range():
    assert rule_confidence(0.75) == 0.75
    assert rule_confidence(1.5)  == 1.0
    assert rule_confidence(-0.1) == 0.0


def test_rule_confidence_rounds_to_four_places():
    assert rule_confidence(0.6667) == 0.6667
