from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MatchingRule(Base):
    __tablename__ = "matching_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, default="dev")
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_tolerance: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    date_tolerance_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
