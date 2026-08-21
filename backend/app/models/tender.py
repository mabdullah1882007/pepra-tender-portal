import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class TenderStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    closed = "closed"


class TenderCategory(str, enum.Enum):
    goods = "goods"
    services = "services"
    works = "works"
    consultancy = "consultancy"


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_portal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tender_number: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    published_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default=TenderCategory.goods)
    estimated_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="PKR")
    status: Mapped[str] = mapped_column(String(20), default=TenderStatus.active, index=True)
    document_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    extraction = relationship("TenderExtraction", back_populates="tender", uselist=False, cascade="all, delete-orphan")
    checklists = relationship("ChecklistItem", back_populates="tender", cascade="all, delete-orphan")
