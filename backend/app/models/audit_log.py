from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exception_id: Mapped[int] = mapped_column(Integer, nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    from_state: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    to_state: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
