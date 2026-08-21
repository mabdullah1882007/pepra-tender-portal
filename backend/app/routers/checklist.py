from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.tender import Tender
from app.models.checklist import ChecklistItem, ChecklistCategory
from app.schemas.checklist import (
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse,
    ChecklistGenerateResponse, ChecklistSummary, CategoryProgress,
    ChecklistCategoryResponse,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/tenders/{tender_id}/checklist", tags=["checklist"])


@router.get("/categories", response_model=List[ChecklistCategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(ChecklistCategory).order_by(ChecklistCategory.display_order).all()


@router.post("", response_model=ChecklistGenerateResponse)
def generate_checklist(
    tender_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    existing = db.query(ChecklistItem).filter(
        ChecklistItem.tender_id == tender_id,
        ChecklistItem.user_id == current_user.id,
    ).count()
    if existing > 0:
        raise HTTPException(status_code=400, detail="Checklist already exists for this tender")

    categories = {c.name: c for c in db.query(ChecklistCategory).all()}
    if not categories:
        default_cats = [
            ("Documents", "Required documents and certificates", 1),
            ("Eligibility", "Eligibility criteria and qualifications", 2),
            ("Financial", "Financial requirements and deposits", 3),
            ("Technical", "Technical capabilities and certifications", 4),
            ("Experience", "Past experience and project history", 5),
        ]
        for name, desc, order in default_cats:
            cat = ChecklistCategory(name=name, description=desc, display_order=order)
            db.add(cat)
        db.flush()
        categories = {c.name: c for c in db.query(ChecklistCategory).all()}

    items_to_create = []
    extraction = tender.extraction

    if extraction:
        if extraction.required_documents and isinstance(extraction.required_documents, dict):
            for doc in extraction.required_documents.get("items", []):
                items_to_create.append(("Documents", doc))

        if extraction.eligibility_criteria and isinstance(extraction.eligibility_criteria, dict):
            for crit in extraction.eligibility_criteria.get("items", []):
                items_to_create.append(("Eligibility", crit))

        if extraction.financial_requirements and isinstance(extraction.financial_requirements, dict):
            for req in extraction.financial_requirements.get("items", []):
                items_to_create.append(("Financial", req))

        if extraction.technical_requirements and isinstance(extraction.technical_requirements, dict):
            for req in extraction.technical_requirements.get("items", []):
                items_to_create.append(("Technical", req))

        if extraction.experience_requirements and isinstance(extraction.experience_requirements, dict):
            for req in extraction.experience_requirements.get("items", []):
                items_to_create.append(("Experience", req))

    if not items_to_create:
        fallback = [
            ("Documents", "Gather and verify all tender documents"),
            ("Eligibility", "Verify eligibility criteria are met"),
            ("Financial", "Arrange financial deposits and fees"),
            ("Technical", "Prepare technical documents and certifications"),
            ("Experience", "Compile past project references"),
        ]
        for cat_name, desc in fallback:
            items_to_create.append((cat_name, desc))

    created_items = []
    for cat_name, desc in items_to_create:
        cat = categories.get(cat_name)
        if cat:
            item = ChecklistItem(
                tender_id=tender_id,
                user_id=current_user.id,
                category_id=cat.id,
                description=desc,
            )
            db.add(item)
            created_items.append(item)

    db.commit()
    for item in created_items:
        db.refresh(item)

    responses = []
    for item in created_items:
        cat = db.query(ChecklistCategory).filter(ChecklistCategory.id == item.category_id).first()
        responses.append(ChecklistItemResponse(
            id=item.id, tender_id=item.tender_id, user_id=item.user_id,
            category_id=item.category_id, category_name=cat.name if cat else "",
            description=item.description, is_completed=item.is_completed,
            notes=item.notes, created_at=item.created_at,
        ))

    return ChecklistGenerateResponse(
        message="Checklist generated successfully",
        items_created=len(created_items),
        checklist=responses,
    )


@router.get("", response_model=List[ChecklistItemResponse])
def get_checklist(
    tender_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(ChecklistItem).filter(
        ChecklistItem.tender_id == tender_id,
        ChecklistItem.user_id == current_user.id,
    ).all()

    responses = []
    for item in items:
        cat = db.query(ChecklistCategory).filter(ChecklistCategory.id == item.category_id).first()
        responses.append(ChecklistItemResponse(
            id=item.id, tender_id=item.tender_id, user_id=item.user_id,
            category_id=item.category_id, category_name=cat.name if cat else "",
            description=item.description, is_completed=item.is_completed,
            notes=item.notes, created_at=item.created_at,
        ))
    return responses


@router.get("/summary", response_model=ChecklistSummary)
def get_checklist_summary(
    tender_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(ChecklistItem).filter(
        ChecklistItem.tender_id == tender_id,
        ChecklistItem.user_id == current_user.id,
    ).all()

    if not items:
        raise HTTPException(status_code=404, detail="No checklist found. Generate one first.")

    total = len(items)
    completed = sum(1 for i in items if i.is_completed)
    percentage = (completed / total * 100) if total > 0 else 0

    cat_map = {}
    for item in items:
        if item.category_id not in cat_map:
            cat = db.query(ChecklistCategory).filter(ChecklistCategory.id == item.category_id).first()
            cat_map[item.category_id] = {"name": cat.name if cat else "Unknown", "total": 0, "completed": 0}
        cat_map[item.category_id]["total"] += 1
        if item.is_completed:
            cat_map[item.category_id]["completed"] += 1

    categories = [
        CategoryProgress(
            category_id=cid,
            category_name=info["name"],
            total=info["total"],
            completed=info["completed"],
            percentage=(info["completed"] / info["total"] * 100) if info["total"] > 0 else 0,
        )
        for cid, info in cat_map.items()
    ]

    missing = [
        ChecklistItemResponse(
            id=i.id, tender_id=i.tender_id, user_id=i.user_id,
            category_id=i.category_id,
            category_name=cat_map.get(i.category_id, {}).get("name", ""),
            description=i.description, is_completed=i.is_completed,
            notes=i.notes, created_at=i.created_at,
        )
        for i in items if not i.is_completed
    ]

    return ChecklistSummary(
        tender_id=tender_id,
        total_items=total,
        completed_items=completed,
        completion_percentage=round(percentage, 1),
        categories=categories,
        missing_items=missing,
    )


@router.put("/{item_id}", response_model=ChecklistItemResponse)
def update_checklist_item(
    tender_id: str,
    item_id: str,
    data: ChecklistItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(ChecklistItem).filter(
        ChecklistItem.id == item_id,
        ChecklistItem.tender_id == tender_id,
        ChecklistItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    if data.is_completed is not None:
        item.is_completed = data.is_completed
    if data.notes is not None:
        item.notes = data.notes
    db.commit()
    db.refresh(item)

    cat = db.query(ChecklistCategory).filter(ChecklistCategory.id == item.category_id).first()
    return ChecklistItemResponse(
        id=item.id, tender_id=item.tender_id, user_id=item.user_id,
        category_id=item.category_id, category_name=cat.name if cat else "",
        description=item.description, is_completed=item.is_completed,
        notes=item.notes, created_at=item.created_at,
    )


@router.delete("/{item_id}", status_code=204)
def delete_checklist_item(
    tender_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(ChecklistItem).filter(
        ChecklistItem.id == item_id,
        ChecklistItem.tender_id == tender_id,
        ChecklistItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    db.delete(item)
    db.commit()
