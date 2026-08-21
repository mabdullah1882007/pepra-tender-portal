from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.tender import Tender
from app.models.extraction import TenderExtraction
from app.utils.security import require_admin
from app.utils.file_utils import save_uploaded_file
from app.services.parser_service import parse_document
from app.services.extraction_service import extract_tender_info

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/tenders/upload")
async def admin_upload_tender(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    source_portal: Optional[str] = Form(None),
    tender_number: Optional[str] = Form(None),
    category: str = Form("goods"),
    estimated_value: Optional[float] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    content = await file.read()
    doc_filename, doc_path = save_uploaded_file(file.filename, content)

    tender = Tender(
        title=title, description=description, source_url=source_url,
        source_portal=source_portal, tender_number=tender_number,
        category=category, estimated_value=estimated_value,
        document_filename=doc_filename, document_path=doc_path,
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)

    try:
        raw_text = parse_document(doc_path)
        tender.raw_text = raw_text
        extraction_data = extract_tender_info(raw_text)
        extraction = TenderExtraction(
            tender_id=tender.id,
            terms_and_conditions=extraction_data.get("terms_and_conditions"),
            scope_of_work=extraction_data.get("scope_of_work"),
            required_documents=extraction_data.get("required_documents"),
            eligibility_criteria=extraction_data.get("eligibility_criteria"),
            financial_requirements=extraction_data.get("financial_requirements"),
            technical_requirements=extraction_data.get("technical_requirements"),
            experience_requirements=extraction_data.get("experience_requirements"),
            submission_instructions=extraction_data.get("submission_instructions"),
            extraction_confidence=extraction_data.get("confidence", 0.0),
        )
        db.add(extraction)
        db.commit()
    except Exception as e:
        pass

    db.refresh(tender)
    return {"id": tender.id, "title": tender.title, "message": "Tender uploaded and processed"}


@router.post("/tenders/{tender_id}/re-extract")
def re_extract_tender(
    tender_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    if not tender.document_path:
        raise HTTPException(status_code=400, detail="No document to parse")

    raw_text = parse_document(tender.document_path)
    tender.raw_text = raw_text
    extraction_data = extract_tender_info(raw_text)

    existing = db.query(TenderExtraction).filter(TenderExtraction.tender_id == tender_id).first()
    if existing:
        existing.terms_and_conditions = extraction_data.get("terms_and_conditions")
        existing.scope_of_work = extraction_data.get("scope_of_work")
        existing.required_documents = extraction_data.get("required_documents")
        existing.eligibility_criteria = extraction_data.get("eligibility_criteria")
        existing.financial_requirements = extraction_data.get("financial_requirements")
        existing.technical_requirements = extraction_data.get("technical_requirements")
        existing.experience_requirements = extraction_data.get("experience_requirements")
        existing.submission_instructions = extraction_data.get("submission_instructions")
        existing.extraction_confidence = extraction_data.get("confidence", 0.0)
    else:
        extraction = TenderExtraction(
            tender_id=tender_id,
            terms_and_conditions=extraction_data.get("terms_and_conditions"),
            scope_of_work=extraction_data.get("scope_of_work"),
            required_documents=extraction_data.get("required_documents"),
            eligibility_criteria=extraction_data.get("eligibility_criteria"),
            financial_requirements=extraction_data.get("financial_requirements"),
            technical_requirements=extraction_data.get("technical_requirements"),
            experience_requirements=extraction_data.get("experience_requirements"),
            submission_instructions=extraction_data.get("submission_instructions"),
            extraction_confidence=extraction_data.get("confidence", 0.0),
        )
        db.add(extraction)

    db.commit()
    return {"message": "Re-extraction completed", "confidence": extraction_data.get("confidence", 0.0)}


@router.get("/stats")
def get_stats(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    from app.models.tender import Tender
    from app.models.checklist import ChecklistItem

    total_tenders = db.query(Tender).count()
    active_tenders = db.query(Tender).filter(Tender.status == "active").count()
    total_users = db.query(User).filter(User.role == "applicant").count()
    total_checklists = db.query(ChecklistItem).distinct(ChecklistItem.tender_id, ChecklistItem.user_id).count()

    return {
        "total_tenders": total_tenders,
        "active_tenders": active_tenders,
        "total_users": total_users,
        "total_checklists": total_checklists,
    }
