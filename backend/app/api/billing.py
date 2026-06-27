# STRIPE_STUB: Replace with real Stripe integration before launch.
# To wire real billing: set STRIPE_SECRET_KEY env var, swap stubs below
# with stripe.Customer / stripe.Subscription SDK calls.

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/billing", tags=["billing"])


class PlanInfo(BaseModel):
    plan: str
    exceptions_used: int
    exceptions_limit: int
    billing_cycle_end: str
    stripe_customer_id: Optional[str]


@router.get("/plan", response_model=PlanInfo)
def get_plan() -> PlanInfo:
    # STRIPE_STUB: hard-coded demo values.
    return PlanInfo(
        plan="Starter",
        exceptions_used=12,
        exceptions_limit=500,
        billing_cycle_end="2024-02-01",
        stripe_customer_id=None,
    )
