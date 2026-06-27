from dataclasses import dataclass, field
from typing import Optional

from app.services.match_types import exact_confidence
from app.services.matching_engine import TransactionRecord, exact_match
from app.services.fuzzy_matcher import ProbableMatch, fuzzy_match
from app.services.rule_matcher import PossibleMatch, RuleConfig, rule_based_match


@dataclass
class ConfirmedMatch:
    bank: TransactionRecord
    gl: TransactionRecord
    confidence_score: float = field(default_factory=exact_confidence)


@dataclass
class PipelineResult:
    confirmed_matches: list[ConfirmedMatch] = field(default_factory=list)
    probable_matches: list[ProbableMatch] = field(default_factory=list)
    possible_matches: list[PossibleMatch] = field(default_factory=list)
    unmatched_bank: list[TransactionRecord] = field(default_factory=list)
    unmatched_gl: list[TransactionRecord] = field(default_factory=list)


def run_pipeline(
    bank: list[TransactionRecord],
    gl: list[TransactionRecord],
    fuzzy_threshold: float = 85,
    rules: Optional[list[RuleConfig]] = None,
) -> PipelineResult:
    # Stage 1: exact match — confirmed, no human review needed
    exact_result = exact_match(bank, gl)
    confirmed = [
        ConfirmedMatch(bank=b, gl=g, confidence_score=exact_confidence())
        for b, g in exact_result.matched_pairs
    ]

    # Stage 2: fuzzy match on leftovers — probable, human review required
    fuzzy_result = fuzzy_match(
        exact_result.unmatched_bank,
        exact_result.unmatched_gl,
        threshold=fuzzy_threshold,
    )

    # Stage 3: rule-based match on remaining leftovers — possible, explicit approval required
    rule_result = rule_based_match(
        fuzzy_result.unmatched_bank,
        fuzzy_result.unmatched_gl,
        rules=rules or [],
    )

    return PipelineResult(
        confirmed_matches=confirmed,
        probable_matches=fuzzy_result.probable_matches,
        possible_matches=rule_result.possible_matches,
        unmatched_bank=rule_result.unmatched_bank,
        unmatched_gl=rule_result.unmatched_gl,
    )
