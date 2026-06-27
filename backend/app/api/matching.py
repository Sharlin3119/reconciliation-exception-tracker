from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matching_engine import TransactionRecord, exact_match
from app.services.rule_matcher import RuleConfig
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/matching", tags=["matching"])


class RecordIn(BaseModel):
    external_id: str
    amount: Decimal
    transaction_date: date
    id: Optional[int] = None
    source: Optional[str] = None
    description: Optional[str] = None


class RecordOut(BaseModel):
    external_id: str
    amount: Decimal
    transaction_date: date
    id: Optional[int] = None
    source: Optional[str] = None
    description: Optional[str] = None


class MatchedPair(BaseModel):
    bank: RecordOut
    gl: RecordOut


class MatchResponse(BaseModel):
    matched_pairs: list[MatchedPair]
    unmatched_bank: list[RecordOut]
    unmatched_gl: list[RecordOut]


class MatchRequest(BaseModel):
    bank_records: list[RecordIn]
    gl_records: list[RecordIn]


# --- pipeline endpoint models ---

class RuleIn(BaseModel):
    amount_tolerance: Decimal = Decimal("0")
    date_tolerance_days: int = 0
    requires_approval: bool = True


class ConfirmedPair(BaseModel):
    bank: RecordOut
    gl: RecordOut
    confidence_score: float


class ProbablePair(BaseModel):
    bank: RecordOut
    gl: RecordOut
    similarity_score: float
    confidence_score: float


class PossiblePair(BaseModel):
    bank: RecordOut
    gl: RecordOut
    confidence_score: float
    matched_rules: list[str]


class PipelineResponse(BaseModel):
    confirmed_matches: list[ConfirmedPair]
    probable_matches: list[ProbablePair]
    possible_matches: list[PossiblePair]
    unmatched_bank: list[RecordOut]
    unmatched_gl: list[RecordOut]


class PipelineRequest(BaseModel):
    bank_records: list[RecordIn]
    gl_records: list[RecordIn]
    fuzzy_threshold: float = 85
    rules: list[RuleIn] = []


def _to_record(r: RecordIn) -> TransactionRecord:
    return TransactionRecord(
        external_id=r.external_id,
        amount=r.amount,
        transaction_date=r.transaction_date,
        id=r.id,
        source=r.source,
        description=r.description,
    )


def _to_out(r: TransactionRecord) -> RecordOut:
    return RecordOut(
        external_id=r.external_id,
        amount=r.amount,
        transaction_date=r.transaction_date,
        id=r.id,
        source=r.source,
        description=r.description,
    )


def _to_rule(r: RuleIn) -> RuleConfig:
    return RuleConfig(
        amount_tolerance=r.amount_tolerance,
        date_tolerance_days=r.date_tolerance_days,
        requires_approval=r.requires_approval,
    )


@router.post("/exact", response_model=MatchResponse)
def exact_match_endpoint(body: MatchRequest) -> MatchResponse:
    bank = [_to_record(r) for r in body.bank_records]
    gl = [_to_record(r) for r in body.gl_records]

    result = exact_match(bank, gl)

    return MatchResponse(
        matched_pairs=[
            MatchedPair(bank=_to_out(b), gl=_to_out(g))
            for b, g in result.matched_pairs
        ],
        unmatched_bank=[_to_out(r) for r in result.unmatched_bank],
        unmatched_gl=[_to_out(r) for r in result.unmatched_gl],
    )


@router.post("/run", response_model=PipelineResponse)
def run_pipeline_endpoint(body: PipelineRequest) -> PipelineResponse:
    bank = [_to_record(r) for r in body.bank_records]
    gl = [_to_record(r) for r in body.gl_records]
    rules = [_to_rule(r) for r in body.rules]

    result = run_pipeline(bank, gl, fuzzy_threshold=body.fuzzy_threshold, rules=rules)

    return PipelineResponse(
        confirmed_matches=[
            ConfirmedPair(bank=_to_out(m.bank), gl=_to_out(m.gl), confidence_score=m.confidence_score)
            for m in result.confirmed_matches
        ],
        probable_matches=[
            ProbablePair(
                bank=_to_out(m.bank),
                gl=_to_out(m.gl),
                similarity_score=m.similarity_score,
                confidence_score=m.confidence_score,
            )
            for m in result.probable_matches
        ],
        possible_matches=[
            PossiblePair(
                bank=_to_out(m.bank),
                gl=_to_out(m.gl),
                confidence_score=m.confidence_score,
                matched_rules=m.matched_rules,
            )
            for m in result.possible_matches
        ],
        unmatched_bank=[_to_out(r) for r in result.unmatched_bank],
        unmatched_gl=[_to_out(r) for r in result.unmatched_gl],
    )
