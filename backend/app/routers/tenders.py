from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
import os

from app.database import get_db
from app.models.user import User
from app.models.tender import Tender, TenderStatus
from app.schemas.tender import (
    TenderCreate, TenderResponse, TenderListResponse, TenderDetailResponse, ExtractionResponse,
)
from app.utils.security import get_current_user, require_admin
from app.utils.file_utils import save_uploaded_file, delete_file

router = APIRouter(prefix="/api/tenders", tags=["tenders"])


@router.get("", response_model=TenderListResponse)
def list_tenders(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    portal: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Tender)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(Tender.title.ilike(search_term), Tender.description.ilike(search_term), Tender.tender_number.ilike(search_term))
        )
    if category:
        query = query.filter(Tender.category == category)
    if status:
        query = query.filter(Tender.status == status)
    if portal:
        query = query.filter(Tender.source_portal.ilike(f"%{portal}%"))

    total = query.count()
    tenders = query.order_by(Tender.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for t in tenders:
        item = TenderResponse(
            id=t.id, title=t.title, description=t.description, source_url=t.source_url,
            source_portal=t.source_portal, tender_number=t.tender_number,
            published_date=t.published_date, deadline=t.deadline, category=t.category,
            estimated_value=t.estimated_value, currency=t.currency, status=t.status,
            document_filename=t.document_filename, created_at=t.created_at, updated_at=t.updated_at,
            has_extraction=t.extraction is not None,
        )
        items.append(item)

    return TenderListResponse(tenders=items, total=total, page=page, page_size=page_size)


@router.get("/{tender_id}", response_model=TenderDetailResponse)
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    tender = db.query(Tender).options(joinedload(Tender.extraction)).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    extraction_resp = None
    if tender.extraction:
        extraction_resp = ExtractionResponse.model_validate(tender.extraction)

    return TenderDetailResponse(
        id=tender.id, title=tender.title, description=tender.description,
        source_url=tender.source_url, source_portal=tender.source_portal,
        tender_number=tender.tender_number, published_date=tender.published_date,
        deadline=tender.deadline, category=tender.category,
        estimated_value=tender.estimated_value, currency=tender.currency,
        status=tender.status, document_filename=tender.document_filename,
        created_at=tender.created_at, updated_at=tender.updated_at,
        raw_text=tender.raw_text, extraction=extraction_resp,
        has_extraction=tender.extraction is not None,
    )


@router.get("/{tender_id}/download")
def download_tender(tender_id: str, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    if not tender.document_path or not os.path.exists(tender.document_path):
        raise HTTPException(status_code=404, detail="Document file not found")
    return FileResponse(
        path=tender.document_path,
        filename=tender.document_filename or "tender_document",
        media_type="application/octet-stream",
    )


@router.post("", response_model=TenderResponse, status_code=201)
async def create_tender(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    source_portal: Optional[str] = Form(None),
    tender_number: Optional[str] = Form(None),
    published_date: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    category: str = Form("goods"),
    estimated_value: Optional[float] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doc_filename = None
    doc_path = None
    if file:
        content = await file.read()
        doc_filename, doc_path = save_uploaded_file(file.filename, content)

    pub_date = None
    if published_date:
        try:
            pub_date = datetime.strptime(published_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    deadline_dt = None
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline)
        except ValueError:
            pass

    tender = Tender(
        title=title, description=description, source_url=source_url,
        source_portal=source_portal, tender_number=tender_number,
        published_date=pub_date, deadline=deadline_dt, category=category,
        estimated_value=estimated_value, document_filename=doc_filename,
        document_path=doc_path,
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)

    return TenderResponse(
        id=tender.id, title=tender.title, description=tender.description,
        source_url=tender.source_url, source_portal=tender.source_portal,
        tender_number=tender.tender_number, published_date=tender.published_date,
        deadline=tender.deadline, category=tender.category,
        estimated_value=tender.estimated_value, currency=tender.currency,
        status=tender.status, document_filename=tender.document_filename,
        created_at=tender.created_at, updated_at=tender.updated_at,
    )


@router.delete("/{tender_id}", status_code=204)
def delete_tender(tender_id: str, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    if tender.document_path:
        delete_file(tender.document_path)
    db.delete(tender)
    db.commit()
