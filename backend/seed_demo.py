"""
Seed the database with demo data for development / recruiter demo.

Run once before starting the server:
    cd backend
    python seed_demo.py

Safe to re-run — skips tables that already have rows.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db import SessionLocal, engine
from app.models import Base
from app.models.matching_rule import MatchingRule
from app.models.recon_exception import ReconException

Base.metadata.create_all(bind=engine)

TENANT = "dev"

DEMO_EXCEPTIONS = [
    dict(exception_type="Missing GL",      status="Open",      amount_difference=450.00, assigned_to=None),
    dict(exception_type="Amount Mismatch", status="Open",      amount_difference=12.50,  assigned_to=None),
    dict(exception_type="Duplicate Entry", status="Assigned",  amount_difference=0.0,    assigned_to="alice@acme.com"),
    dict(exception_type="Missing GL",      status="In Review", amount_difference=750.00, assigned_to="bob@acme.com"),
    dict(exception_type="Amount Mismatch", status="Resolved",  amount_difference=5.00,   assigned_to="alice@acme.com"),
    dict(exception_type="Timing Diff",     status="Open",      amount_difference=200.00, assigned_to=None),
    dict(exception_type="Timing Diff",     status="Reopened",  amount_difference=150.00, assigned_to="bob@acme.com"),
]

DEMO_RULES = [
    dict(name="Penny tolerance",     amount_tolerance=0.01, date_tolerance_days=0, requires_approval=False),
    dict(name="5-day timing window", amount_tolerance=0.0,  date_tolerance_days=5, requires_approval=True),
    dict(name="Loose reconcile",     amount_tolerance=10.0, date_tolerance_days=3, requires_approval=True),
]


def seed():
    db = SessionLocal()

    exc_count = db.query(ReconException).filter(ReconException.tenant_id == TENANT).count()
    if exc_count == 0:
        for row in DEMO_EXCEPTIONS:
            db.add(ReconException(tenant_id=TENANT, **row))
        db.commit()
        print(f"Seeded {len(DEMO_EXCEPTIONS)} demo exceptions.")
    else:
        print(f"Exceptions already seeded ({exc_count} rows) — skipping.")

    rule_count = db.query(MatchingRule).filter(MatchingRule.tenant_id == TENANT).count()
    if rule_count == 0:
        for row in DEMO_RULES:
            db.add(MatchingRule(tenant_id=TENANT, **row))
        db.commit()
        print(f"Seeded {len(DEMO_RULES)} demo matching rules.")
    else:
        print(f"Rules already seeded ({rule_count} rows) — skipping.")

    db.close()


if __name__ == "__main__":
    seed()
