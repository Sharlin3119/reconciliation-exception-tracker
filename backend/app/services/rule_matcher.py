from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from app.services.match_types import rule_confidence
from app.services.matching_engine import TransactionRecord


@dataclass
class RuleConfig:
    amount_tolerance: Decimal = Decimal("0")
    date_tolerance_days: int = 0
    requires_approval: bool = True


@dataclass
class PossibleMatch:
    bank: TransactionRecord
    gl: TransactionRecord
    confidence_score: float
    matched_rules: list[str]


@dataclass
class RuleMatchResult:
    possible_matches: list[PossibleMatch] = field(default_factory=list)
    unmatched_bank: list[TransactionRecord] = field(default_factory=list)
    unmatched_gl: list[TransactionRecord] = field(default_factory=list)


def _evaluate(
    bank: TransactionRecord,
    gl: TransactionRecord,
    rule: RuleConfig,
) -> Optional[tuple[float, list[str]]]:
    fired: list[str] = []

    amount_diff = abs(bank.amount - gl.amount)
    if amount_diff > rule.amount_tolerance:
        return None
    if amount_diff == 0:
        fired.append("amount exact")
    else:
        fired.append(f"amount within {rule.amount_tolerance}")

    date_diff = abs((bank.transaction_date - gl.transaction_date).days)
    if date_diff > rule.date_tolerance_days:
        return None
    if date_diff == 0:
        fired.append("date exact")
    else:
        fired.append(f"date within {rule.date_tolerance_days} day(s)")

    # Confidence decays with how much tolerance was consumed.
    # Start at 0.8; subtract 0.05 per day off and 0.05 if amount differs at all.
    base = 0.8
    if amount_diff > 0:
        base -= 0.05
    base -= 0.05 * date_diff

    return rule_confidence(base), fired


def rule_based_match(
    bank: list[TransactionRecord],
    gl: list[TransactionRecord],
    rules: list[RuleConfig],
) -> RuleMatchResult:
    if not rules:
        return RuleMatchResult(unmatched_bank=list(bank), unmatched_gl=list(gl))

    result = RuleMatchResult()
    available_gl = list(gl)

    for bank_record in bank:
        best_score: float = -1.0
        best_index: int = -1
        best_rules: list[str] = []

        for i, gl_record in enumerate(available_gl):
            for rule in rules:
                evaluation = _evaluate(bank_record, gl_record, rule)
                if evaluation is not None:
                    score, fired = evaluation
                    if score > best_score:
                        best_score = score
                        best_index = i
                        best_rules = fired

        if best_index >= 0:
            matched_gl = available_gl.pop(best_index)
            result.possible_matches.append(
                PossibleMatch(
                    bank=bank_record,
                    gl=matched_gl,
                    confidence_score=best_score,
                    matched_rules=best_rules,
                )
            )
        else:
            result.unmatched_bank.append(bank_record)

    result.unmatched_gl.extend(available_gl)
    return result
