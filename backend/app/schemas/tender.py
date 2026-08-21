from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class TenderBase(BaseModel):
    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_portal: Optional[str] = None
    tender_number: Optional[str] = None
    published_date: Optional[date] = None
    deadline: Optional[datetime] = None
    category: str = "goods"
    estimated_value: Optional[float] = None
    currency: str = "PKR"


class TenderCreate(TenderBase):
    pass


class TenderResponse(TenderBase):
    id: str
    status: str
    document_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    has_extraction: bool = False

    class Config:
        from_attributes = True


class TenderListResponse(BaseModel):
    tenders: List[TenderResponse]
    total: int
    page: int
    page_size: int


class TenderDetailResponse(TenderResponse):
    source_portal: Optional[str] = None
    raw_text: Optional[str] = None
    extraction: Optional["ExtractionResponse"] = None

    class Config:
        from_attributes = True


class ExtractionResponse(BaseModel):
    id: str
    terms_and_conditions: Optional[dict] = None
    scope_of_work: Optional[str] = None
    required_documents: Optional[dict] = None
    eligibility_criteria: Optional[dict] = None
    financial_requirements: Optional[dict] = None
    technical_requirements: Optional[dict] = None
    experience_requirements: Optional[dict] = None
    submission_instructions: Optional[str] = None
    extraction_confidence: Optional[float] = None
    extracted_at: datetime

    class Config:
        from_attributes = True


TenderDetailResponse.model_rebuild()
