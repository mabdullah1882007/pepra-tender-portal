import re
from typing import Dict, Any, List, Optional


SECTION_PATTERNS = {
    "terms_and_conditions": [
        r"(?i)(terms\s+and\s+conditions?|t\s*&\s*c|general\s+terms)",
        r"(?i)(terms\s+of\s+(?:contract|agreement|reference))",
    ],
    "scope_of_work": [
        r"(?i)(scope\s+of\s+work|statement\s+of\s+work|sow|scope\s+of\s+services?)",
        r"(?i)(description\s+of\s+(?:services?|work|requirements?))",
        r"(?i)(job\s+description|detailed\s+scope)",
    ],
    "required_documents": [
        r"(?i)(documents?\s+required|list\s+of\s+documents?|enclosures?|annexures?)",
        r"(?i)(documents?\s+to\s+be\s+submitted|submission\s+of\s+documents?)",
    ],
    "eligibility_criteria": [
        r"(?i)(eligibility\s+(?:criteria|conditions?|requirements?))",
        r"(?i)(qualification\s+(?:criteria|requirements?))",
        r"(?i)(pre-?qualification| bidder\s+eligibility)",
    ],
    "financial_requirements": [
        r"(?i)(financial\s+(?:requirements?|criteria|capacity))",
        r"(?i)(bid\s+security|earnest\s+money|emd|emdown\s+payment)",
        r"(?i)(tender\s+fee|processing\s+fee|bid\s+bond)",
    ],
    "technical_requirements": [
        r"(?i)(technical\s+(?:requirements?|criteria|specifications?))",
        r"(?i)(technical\s+proposal|methodology|implementation\s+plan)",
        r"(?i)(equipment\s+and\s+machinery|certifications?)",
    ],
    "experience_requirements": [
        r"(?i)(experience\s+(?:requirements?|criteria))",
        r"(?i)(past\s+(?:performance|experience|projects?))",
        r"(?i)(similar\s+(?:projects?|work|experience))",
        r"(?i)(client\s+references?|completed\s+projects?)",
    ],
    "submission_instructions": [
        r"(?i)(submission\s+(?:instructions?|guidelines?|procedure))",
        r"(?i)(how\s+to\s+(?:submit|apply|bid))",
        r"(?i)(bid\s+submission|submission\s+deadline|last\s+date)",
    ],
}


DOCUMENT_KEYWORDS = [
    "NTN", "NTN certificate", "incorporation certificate", "registration certificate",
    "partnership deed", "memorandum of association", "articles of association",
    "financial statements", "audited accounts", "audit reports", "balance sheet",
    "bank statement", "bank solvency certificate", "bid security", "bid bond",
    "EMD", "earnest money", "tender fee", "processing fee",
    "power of attorney", "undertaking", "affidavit", "compliance certificate",
    "tax clearance certificate", "GST registration", "sales tax certificate",
    "income tax certificate", "withholding tax certificate",
    "ISO certification", "ISO 9001", "ISO 14001", "OHSAS 18001",
    "PEC registration", "Pakistan Engineering Council",
    "experience certificates", "completion certificates", "noc",
    "technical proposal", "financial proposal", "price schedule",
    "company profile", "organizational chart", "CV of key personnel",
    "machinery list", "equipment list", "insurance certificate",
]

ELIGIBILITY_KEYWORDS = [
    "minimum turnover", "annual turnover", "revenue requirement",
    "years of experience", "years in business", "minimum experience",
    "similarity", "similar project", "comparable experience",
    "not blacklisted", "not suspended", "active taxpayer",
    "tax compliance", "no criminal record", "clean chit",
    "registered company", "registered firm", "SECP registered",
    "pec registered", "licensed", "accredited",
]

FINANCIAL_AMOUNT_PATTERN = r"(?:PKR|Rs\.?|Pakistani\s+Rupees?)\s*[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|lakh|crore))?"
PERCENTAGE_PATTERN = r"\d+(?:\.\d+)?\s*%"
EMD_PATTERN = r"(?i)(?:EMD|earnest\s+money|bid\s+security)\s*(?:of|:)?\s*(?:" + FINANCIAL_AMOUNT_PATTERN + r")"


def _find_section(text: str, section_type: str) -> Optional[str]:
    patterns = SECTION_PATTERNS.get(section_type, [])
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            start = match.start()
            end = len(text)
            for other_type, other_patterns in SECTION_PATTERNS.items():
                if other_type == section_type:
                    continue
                for other_pattern in other_patterns:
                    other_match = re.search(other_pattern, text[start + 50:])
                    if other_match:
                        candidate = start + 50 + other_match.start()
                        if candidate < end:
                            end = candidate
            section_text = text[start:end].strip()
            if len(section_text) > 20:
                return section_text[:5000]
    return None


def _extract_items_from_text(text: str, keywords: List[str]) -> List[str]:
    found = []
    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower().strip()
        for kw in keywords:
            if kw.lower() in line_lower and len(line.strip()) > 5:
                cleaned = line.strip().rstrip(".,;:")
                if cleaned not in found:
                    found.append(cleaned)
                break
    return found


def _extract_list_items(text: str) -> List[str]:
    items = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"^[•\-\*\d+\.\)]+\s*", line):
            cleaned = re.sub(r"^[•\-\*\d+\.\)]+\s*", "", line).strip()
            if len(cleaned) > 5:
                items.append(cleaned.rstrip(".,;:"))
    return items


def _extract_financial_items(text: str) -> List[str]:
    items = []
    amounts = re.findall(FINANCIAL_AMOUNT_PATTERN, text, re.IGNORECASE)
    for amt in amounts:
        context_start = max(0, text.lower().find(amt.lower()) - 100)
        context = text[context_start:text.lower().find(amt.lower()) + len(amt)].strip()
        last_newline = context.rfind("\n")
        if last_newline > 0:
            context = context[last_newline:].strip()
        if context not in items:
            items.append(context.rstrip(".,;:"))

    percentages = re.findall(r"(?:retention|performance\s+bond|advance\s+payment)\s*(?:of|:)?\s*" + PERCENTAGE_PATTERN, text, re.IGNORECASE)
    for p in percentages:
        if p not in items:
            items.append(p.strip())

    return items


def extract_tender_info(raw_text: str) -> Dict[str, Any]:
    result = {}
    total_sections = 0
    found_sections = 0

    for section_type in SECTION_PATTERNS:
        total_sections += 1
        section_text = _find_section(raw_text, section_type)
        if section_text:
            found_sections += 1
            if section_type == "scope_of_work":
                result[section_type] = section_text
            else:
                items = _extract_list_items(section_text)
                if not items and section_type in ["required_documents", "eligibility_criteria"]:
                    items = _extract_items_from_text(section_text, DOCUMENT_KEYWORDS if section_type == "required_documents" else ELIGIBILITY_KEYWORDS)
                if not items and section_type == "financial_requirements":
                    items = _extract_financial_items(section_text)
                if not items:
                    items = [line.strip() for line in section_text.split("\n") if line.strip() and len(line.strip()) > 10][:10]
                result[section_type] = {"items": items, "raw_section": section_text[:2000]}

    result["confidence"] = round(found_sections / total_sections * 100, 1) if total_sections > 0 else 0.0
    return result
