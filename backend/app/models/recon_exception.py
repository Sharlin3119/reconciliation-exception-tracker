from datetime import datetime
from typing import Optional
from sqlalchemy import String, Numeric, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ReconException(Base):
    __tablename__ = "recon_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, default="dev")
    transaction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transactions.id"), nullable=True
    )
    exception_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount_difference: Mapped[Optional[float]] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="Open")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    transaction: Mapped[Optional["Transaction"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Transaction", back_populates=None, foreign_keys=[transaction_id]
    )
