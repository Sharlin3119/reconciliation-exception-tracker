from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.recon_exception import ReconException

VALID_TRANSITIONS: dict[str, list[str]] = {
    "Open":      ["Assigned", "In Review"],
    "Assigned":  ["In Review", "Resolved"],
    "In Review": ["Resolved", "Open"],
    "Resolved":  ["Reopened"],
    "Reopened":  ["Assigned", "In Review", "Resolved"],
}


def transition_exception(
    db: Session,
    exception_id: int,
    actor_id: str,
    to_state: str,
    reason: Optional[str] = None,
) -> ReconException:
    to_state = to_state.strip()

    exc = db.get(ReconException, exception_id)
    if exc is None:
        raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found")

    from_state = exc.status
    allowed = VALID_TRANSITIONS.get(from_state, [])
    if to_state not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{from_state}' to '{to_state}'. "
                   f"Allowed: {allowed}",
        )

    exc.status = to_state
    if to_state == "Resolved":
        exc.resolved_at = datetime.now(timezone.utc)

    db.add(AuditLog(
        exception_id=exception_id,
        actor_id=actor_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
    ))

    db.commit()
    db.refresh(exc)
    return exc
