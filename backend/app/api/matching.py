from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matching_engine import TransactionRecord, exact_match

router = APIRouter(prefix="/matching", tags=["matching"])


class RecordIn(BaseModel):
    external_id: str
    amount: Decimal
    transaction_date: date
    id: Optional[int] = None
    source: Optional[str] = None


class RecordOut(BaseModel):
    external_id: str
    amount: Decimal
    transaction_date: date
    id: Optional[int] = None
    source: Optional[str] = None


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


def _to_record(r: RecordIn) -> TransactionRecord:
    return TransactionRecord(
        external_id=r.external_id,
        amount=r.amount,
        transaction_date=r.transaction_date,
        id=r.id,
        source=r.source,
    )


def _to_out(r: TransactionRecord) -> RecordOut:
    return RecordOut(
        external_id=r.external_id,
        amount=r.amount,
        transaction_date=r.transaction_date,
        id=r.id,
        source=r.source,
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
