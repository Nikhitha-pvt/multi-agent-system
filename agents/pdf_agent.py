

import io
import re
import json
from typing import Dict, Optional
from PyPDF2 import PdfReader
from utils.llm_client import call_llm
from memory.memory_store import MemoryStore

memory = MemoryStore()

COMPLIANCE_KEYWORDS = ["GDPR", "FDA", "HIPAA", "PCI"]

PDF_EXTRACTION_PROMPT = """
Extract key information from this PDF text. Return a JSON object with:
- invoice_total: number (or null if not found)
- compliance_mentions: list of compliance terms found (GDPR, FDA, HIPAA, PCI)
- intent: one of [Invoice, Regulation, General]

Text to analyze:
{text_excerpt}

Return ONLY a JSON object like this:
{
    "invoice_total": 1234.56,
    "compliance_mentions": ["GDPR"],
    "intent": "Invoice"
}
"""

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def find_invoice_total(text: str) -> Optional[float]:
    """Find invoice total using regex patterns."""
    patterns = [
        r'total[:\s]*[\$]?([\d,]+\.?\d{0,2})',
        r'amount\s+due[:\s]*[\$]?([\d,]+\.?\d{0,2})',
        r'balance\s+due[:\s]*[\$]?([\d,]+\.?\d{0,2})'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text.lower(), re.MULTILINE)
        for match in matches:
            try:
                amount = match.group(1).replace(',', '')
                return float(amount)
            except (ValueError, IndexError):
                continue
    return None

def find_compliance_terms(text: str) -> list:
    """Find compliance-related terms in text."""
    found = []
    text_lower = text.lower()
    for term in COMPLIANCE_KEYWORDS:
        if term.lower() in text_lower:
            found.append(term)
    return found

def process_pdf(pdf_bytes: bytes, source: str = None, input_id: int = None) -> Dict:
    """Main processing function for PDFs."""
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_bytes)
    if text.startswith("Error"):
        return {"error": text}

    # Find invoice total with regex
    invoice_total = find_invoice_total(text)
    
    # Find compliance terms
    compliance_mentions = find_compliance_terms(text)
    
    # Use LLM for intent classification
    text_excerpt = text[:2000]  # First 2000 chars for LLM
    response = call_llm(PDF_EXTRACTION_PROMPT.replace("{text_excerpt}", text_excerpt))
    
    try:
        llm_result = json.loads(response)
    except:
        llm_result = {"intent": "General"}

    # Build result
    result = {
        "invoice_total": invoice_total,
        "compliance_mentions": compliance_mentions,
        "intent": llm_result.get("intent", "General"),
        "flags": []
    }

    # Add flags based on rules
    if invoice_total and invoice_total > 10000:
        result["flags"].append(f"High value invoice: ${invoice_total:,.2f}")
    
    if compliance_mentions:
        result["flags"].append(f"Contains compliance terms: {', '.join(compliance_mentions)}")

    # Log to memory if input_id provided
    if input_id:
        memory.log_extraction(
            agent="PDFAgent",
            extracted_fields=result,
            input_id=input_id
        )
        if result["flags"]:
            memory.log_action(
                action_type="pdf_flag",
                details={"flags": result["flags"]},
                input_id=input_id
            )

    return result