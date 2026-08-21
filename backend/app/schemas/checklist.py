from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChecklistCategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    display_order: int

    class Config:
        from_attributes = True


class ChecklistItemCreate(BaseModel):
    category_id: str
    description: str


class ChecklistItemUpdate(BaseModel):
    is_completed: Optional[bool] = None
    notes: Optional[str] = None


class ChecklistItemResponse(BaseModel):
    id: str
    tender_id: str
    user_id: str
    category_id: str
    category_name: str = ""
    description: str
    is_completed: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChecklistSummary(BaseModel):
    tender_id: str
    total_items: int
    completed_items: int
    completion_percentage: float
    categories: List["CategoryProgress"]
    missing_items: List[ChecklistItemResponse]


class CategoryProgress(BaseModel):
    category_id: str
    category_name: str
    total: int
    completed: int
    percentage: float


class ChecklistGenerateResponse(BaseModel):
    message: str
    items_created: int
    checklist: List[ChecklistItemResponse]


ChecklistSummary.model_rebuild()
