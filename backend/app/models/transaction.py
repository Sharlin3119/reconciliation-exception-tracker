from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False)  # "bank" | "gl"
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="unmatched")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
