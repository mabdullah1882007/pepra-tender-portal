import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TenderExtraction(Base):
    __tablename__ = "tender_extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenders.id"), unique=True, nullable=False)
    terms_and_conditions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    scope_of_work: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_documents: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    eligibility_criteria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    financial_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    technical_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    experience_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    submission_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tender = relationship("Tender", back_populates="extraction")
