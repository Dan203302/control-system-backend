import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Numeric, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .db import Base


class OrderStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    done = "done"
    canceled = "canceled"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "orders"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    items: Mapped[list] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=OrderStatus.created.value)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
