from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.exception_service import transition_exception

router = APIRouter(prefix="/exceptions", tags=["exceptions"])


class TransitionRequest(BaseModel):
    actor_id: str
    to_state: str
    reason: Optional[str] = None


class TransitionResponse(BaseModel):
    id: int
    status: str
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


@router.post("/{exception_id}/transition", response_model=TransitionResponse)
def transition(
    exception_id: int,
    body: TransitionRequest,
    db: Session = Depends(get_db),
) -> TransitionResponse:
    exc = transition_exception(
        db=db,
        exception_id=exception_id,
        actor_id=body.actor_id,
        to_state=body.to_state,
        reason=body.reason,
    )
    return TransitionResponse.model_validate(exc)
