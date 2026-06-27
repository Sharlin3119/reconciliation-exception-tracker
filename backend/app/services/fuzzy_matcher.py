from dataclasses import dataclass, field
from typing import Optional

from rapidfuzz import fuzz

from app.services.match_types import fuzzy_confidence
from app.services.matching_engine import TransactionRecord


@dataclass
class ProbableMatch:
    bank: TransactionRecord
    gl: TransactionRecord
    similarity_score: float
    confidence_score: float


@dataclass
class FuzzyMatchResult:
    probable_matches: list[ProbableMatch] = field(default_factory=list)
    unmatched_bank: list[TransactionRecord] = field(default_factory=list)
    unmatched_gl: list[TransactionRecord] = field(default_factory=list)


def _similarity(a: Optional[str], b: Optional[str]) -> float:
    if not a or not b:
        return 0.0
    return fuzz.ratio(a, b)


def fuzzy_match(
    bank: list[TransactionRecord],
    gl: list[TransactionRecord],
    threshold: float = 85,
) -> FuzzyMatchResult:
    result = FuzzyMatchResult()
    available_gl = list(gl)

    for bank_record in bank:
        best_score = 0.0
        best_index = -1

        for i, gl_record in enumerate(available_gl):
            score = _similarity(bank_record.description, gl_record.description)
            if score > best_score:
                best_score = score
                best_index = i

        if best_score >= threshold:
            matched_gl = available_gl.pop(best_index)
            result.probable_matches.append(
                ProbableMatch(
                    bank=bank_record,
                    gl=matched_gl,
                    similarity_score=best_score,
                    confidence_score=fuzzy_confidence(best_score),
                )
            )
        else:
            result.unmatched_bank.append(bank_record)

    result.unmatched_gl.extend(available_gl)
    return result
