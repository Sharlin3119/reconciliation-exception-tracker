from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.matching_rule import MatchingRule
from app.services.rule_matcher import RuleConfig


def list_rules(db: Session, tenant_id: str) -> list[MatchingRule]:
    return (
        db.query(MatchingRule)
        .filter(MatchingRule.tenant_id == tenant_id)
        .order_by(MatchingRule.id)
        .all()
    )


def get_rule(db: Session, rule_id: int, tenant_id: str) -> MatchingRule:
    rule = (
        db.query(MatchingRule)
        .filter(MatchingRule.id == rule_id, MatchingRule.tenant_id == tenant_id)
        .first()
    )
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    return rule


def create_rule(
    db: Session,
    tenant_id: str,
    name: str,
    amount_tolerance: float,
    date_tolerance_days: int,
    requires_approval: bool,
) -> MatchingRule:
    rule = MatchingRule(
        tenant_id=tenant_id,
        name=name,
        amount_tolerance=amount_tolerance,
        date_tolerance_days=date_tolerance_days,
        requires_approval=requires_approval,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(
    db: Session,
    rule_id: int,
    tenant_id: str,
    name: str,
    amount_tolerance: float,
    date_tolerance_days: int,
    requires_approval: bool,
    is_active: bool,
) -> MatchingRule:
    rule = get_rule(db, rule_id, tenant_id)
    rule.name = name
    rule.amount_tolerance = amount_tolerance
    rule.date_tolerance_days = date_tolerance_days
    rule.requires_approval = requires_approval
    rule.is_active = is_active
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: int, tenant_id: str) -> None:
    rule = get_rule(db, rule_id, tenant_id)
    db.delete(rule)
    db.commit()


def active_rules_as_configs(db: Session, tenant_id: str) -> list[RuleConfig]:
    rules = (
        db.query(MatchingRule)
        .filter(MatchingRule.tenant_id == tenant_id, MatchingRule.is_active.is_(True))
        .all()
    )
    return [
        RuleConfig(
            amount_tolerance=Decimal(str(r.amount_tolerance)),
            date_tolerance_days=r.date_tolerance_days,
            requires_approval=r.requires_approval,
        )
        for r in rules
    ]
