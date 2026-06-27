"""
Seed the database with demo exceptions for development / recruiter demo.
Run from the backend/ directory:
    python seed_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db import SessionLocal, engine
from app.models import Base
from app.models.recon_exception import ReconException

Base.metadata.create_all(bind=engine)

TENANT = "dev"

DEMO_ROWS = [
    dict(exception_type="Missing GL",      status="Open",      amount_difference=450.00, assigned_to=None),
    dict(exception_type="Amount Mismatch", status="Open",      amount_difference=12.50,  assigned_to=None),
    dict(exception_type="Duplicate Entry", status="Assigned",  amount_difference=0.0,    assigned_to="alice@acme.com"),
    dict(exception_type="Missing GL",      status="In Review", amount_difference=750.00, assigned_to="bob@acme.com"),
    dict(exception_type="Amount Mismatch", status="Resolved",  amount_difference=5.00,   assigned_to="alice@acme.com"),
    dict(exception_type="Timing Diff",     status="Open",      amount_difference=200.00, assigned_to=None),
    dict(exception_type="Timing Diff",     status="Reopened",  amount_difference=150.00, assigned_to="bob@acme.com"),
]


def seed():
    db = SessionLocal()
    existing = db.query(ReconException).filter(ReconException.tenant_id == TENANT).count()
    if existing >= len(DEMO_ROWS):
        print(f"Already have {existing} demo rows for tenant '{TENANT}' — skipping.")
        db.close()
        return

    for row in DEMO_ROWS:
        db.add(ReconException(tenant_id=TENANT, **row))
    db.commit()
    print(f"Seeded {len(DEMO_ROWS)} demo exceptions for tenant '{TENANT}'.")
    db.close()


if __name__ == "__main__":
    seed()
