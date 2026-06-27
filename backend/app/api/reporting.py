from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.recon_exception import ReconException

router = APIRouter(prefix="/reporting", tags=["reporting"])


class StatusCount(BaseModel):
    status: str
    count: int


class TypeCount(BaseModel):
    exception_type: str
    count: int
    total_amount_difference: float


class SummaryResponse(BaseModel):
    total_exceptions: int
    total_resolved: int
    total_amount_difference: float
    by_status: list[StatusCount]
    by_type: list[TypeCount]


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    x_tenant_id: str = Header(default="dev"),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    base = db.query(ReconException).filter(ReconException.tenant_id == x_tenant_id)

    total = base.count()
    resolved = base.filter(ReconException.status == "Resolved").count()
    amount_sum = base.with_entities(func.sum(ReconException.amount_difference)).scalar() or 0.0

    by_status = [
        StatusCount(status=row.status, count=row.cnt)
        for row in db.query(
            ReconException.status,
            func.count(ReconException.id).label("cnt"),
        )
        .filter(ReconException.tenant_id == x_tenant_id)
        .group_by(ReconException.status)
        .all()
    ]

    by_type = [
        TypeCount(
            exception_type=row.exception_type,
            count=row.cnt,
            total_amount_difference=float(row.total_diff or 0),
        )
        for row in db.query(
            ReconException.exception_type,
            func.count(ReconException.id).label("cnt"),
            func.sum(ReconException.amount_difference).label("total_diff"),
        )
        .filter(ReconException.tenant_id == x_tenant_id)
        .group_by(ReconException.exception_type)
        .all()
    ]

    return SummaryResponse(
        total_exceptions=total,
        total_resolved=resolved,
        total_amount_difference=float(amount_sum),
        by_status=by_status,
        by_type=by_type,
    )
