def exact_confidence() -> float:
    return 1.0


def fuzzy_confidence(similarity_score: float) -> float:
    return round(similarity_score / 100.0, 4)


def rule_confidence(base: float) -> float:
    return round(max(0.0, min(1.0, base)), 4)
