from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class TransactionRecord:
    external_id: str
    amount: Decimal
    transaction_date: date
    id: Optional[int] = None
    source: Optional[str] = None


@dataclass
class MatchResult:
    matched_pairs: list[tuple["TransactionRecord", "TransactionRecord"]] = field(default_factory=list)
    unmatched_bank: list["TransactionRecord"] = field(default_factory=list)
    unmatched_gl: list["TransactionRecord"] = field(default_factory=list)


def _match_key(record: TransactionRecord) -> tuple:
    return (record.external_id, record.amount, record.transaction_date)


def _group_by_key(
    records: list[TransactionRecord],
) -> dict[tuple, list[TransactionRecord]]:
    groups: dict[tuple, list[TransactionRecord]] = {}
    for record in records:
        groups.setdefault(_match_key(record), []).append(record)
    return groups


def exact_match(
    bank: list[TransactionRecord],
    gl: list[TransactionRecord],
) -> MatchResult:
    bank_by_key = _group_by_key(bank)
    gl_by_key = _group_by_key(gl)

    result = MatchResult()

    for key, bank_group in bank_by_key.items():
        gl_group = gl_by_key.pop(key, [])
        if gl_group:
            result.matched_pairs.append((bank_group[0], gl_group[0]))
            result.unmatched_bank.extend(bank_group[1:])
            result.unmatched_gl.extend(gl_group[1:])
        else:
            result.unmatched_bank.extend(bank_group)

    for gl_group in gl_by_key.values():
        result.unmatched_gl.extend(gl_group)

    return result
