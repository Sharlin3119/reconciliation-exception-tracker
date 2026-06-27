from datetime import datetime

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import rule_service

router = APIRouter(prefix="/rules", tags=["rules"])


class RuleCreate(BaseModel):
    name: str
    amount_tolerance: float = 0.0
    date_tolerance_days: int = 0
    requires_approval: bool = True


class RuleUpdate(BaseModel):
    name: str
    amount_tolerance: float
    date_tolerance_days: int
    requires_approval: bool
    is_active: bool


class RuleOut(BaseModel):
    id: int
    name: str
    amount_tolerance: float
    date_tolerance_days: int
    requires_approval: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[RuleOut])
def list_rules(
    x_tenant_id: str = Header(default="dev"),
    db: Session = Depends(get_db),
) -> list[RuleOut]:
    return [RuleOut.model_validate(r) for r in rule_service.list_rules(db, x_tenant_id)]


@router.post("", response_model=RuleOut, status_code=201)
def create_rule(
    body: RuleCreate,
    x_tenant_id: str = Header(default="dev"),
    db: Session = Depends(get_db),
) -> RuleOut:
    rule = rule_service.create_rule(
        db,
        tenant_id=x_tenant_id,
        name=body.name,
        amount_tolerance=body.amount_tolerance,
        date_tolerance_days=body.date_tolerance_days,
        requires_approval=body.requires_approval,
    )
    return RuleOut.model_validate(rule)


@router.put("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: int,
    body: RuleUpdate,
    x_tenant_id: str = Header(default="dev"),
    db: Session = Depends(get_db),
) -> RuleOut:
    rule = rule_service.update_rule(
        db,
        rule_id=rule_id,
        tenant_id=x_tenant_id,
        name=body.name,
        amount_tolerance=body.amount_tolerance,
        date_tolerance_days=body.date_tolerance_days,
        requires_approval=body.requires_approval,
        is_active=body.is_active,
    )
    return RuleOut.model_validate(rule)


@router.delete("/{rule_id}", status_code=204)
def delete_rule(
    rule_id: int,
    x_tenant_id: str = Header(default="dev"),
    db: Session = Depends(get_db),
) -> None:
    rule_service.delete_rule(db, rule_id, x_tenant_id)
