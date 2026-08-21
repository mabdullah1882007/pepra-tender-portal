from sqlalchemy import text
from app.database import engine, Base
from app.models import *  # noqa
from app.models.checklist import ChecklistCategory


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_categories():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        existing = db.query(ChecklistCategory).count()
        if existing == 0:
            categories = [
                ("Documents", "Required documents and certificates", 1),
                ("Eligibility", "Eligibility criteria and qualifications", 2),
                ("Financial", "Financial requirements and deposits", 3),
                ("Technical", "Technical capabilities and certifications", 4),
                ("Experience", "Past experience and project history", 5),
            ]
            for name, desc, order in categories:
                db.add(ChecklistCategory(name=name, description=desc, display_order=order))
            db.commit()
    finally:
        db.close()
