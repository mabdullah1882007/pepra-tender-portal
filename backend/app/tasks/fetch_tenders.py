from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.database import SessionLocal
from app.models.tender import Tender
from app.models.extraction import TenderExtraction
from app.services.parser_service import parse_document
from app.services.extraction_service import extract_tender_info
from app.utils.file_utils import save_uploaded_file
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.tasks.fetch_tenders.schedule_fetch")
def schedule_fetch():
    logger.info("Starting scheduled tender fetch")
    fetch_from_ppra()


@celery_app.task(name="app.tasks.fetch_tenders.fetch_from_ppra")
def fetch_from_ppra():
    db = SessionLocal()
    try:
        urls_to_check = [
            "https://ep.ppra.org.pk",
            "https://ppra.kp.gov.pk",
        ]
        for base_url in urls_to_check:
            try:
                _scrape_portal(db, base_url)
            except Exception as e:
                logger.error(f"Error fetching from {base_url}: {e}")
    finally:
        db.close()


def _scrape_portal(db, base_url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        with httpx.Client(timeout=30, follow_redirects=True, verify=False) as client:
            response = client.get(base_url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {base_url}: {response.status_code}")
                return

            soup = BeautifulSoup(response.text, "lxml")
            tender_links = soup.find_all("a", href=True)

            count = 0
            for link in tender_links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if not text or len(text) < 10:
                    continue
                if any(kw in text.lower() for kw in ["tender", "rfp", "proposal", "procurement", "bid"]):
                    full_url = href if href.startswith("http") else f"{base_url}{href}"
                    existing = db.query(Tender).filter(Tender.source_url == full_url).first()
                    if existing:
                        continue
                    tender = Tender(
                        title=text[:500],
                        source_url=full_url,
                        source_portal=base_url,
                    )
                    db.add(tender)
                    count += 1
                    if count >= 20:
                        break

            db.commit()
            logger.info(f"Added {count} tenders from {base_url}")
    except Exception as e:
        logger.error(f"Scraping error for {base_url}: {e}")


@celery_app.task(name="app.tasks.fetch_tenders.process_tender_document")
def process_tender_document(tender_id: str):
    db = SessionLocal()
    try:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender or not tender.document_path:
            return

        raw_text = parse_document(tender.document_path)
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
        logger.info(f"Processed tender {tender_id} with confidence {extraction_data.get('confidence')}")
    except Exception as e:
        logger.error(f"Error processing tender {tender_id}: {e}")
    finally:
        db.close()
