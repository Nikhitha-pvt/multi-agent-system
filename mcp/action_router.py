# from memory.memory_store import MemoryStore
# import requests

# memory = MemoryStore()

# # Simulated endpoints (for demo)
# CRM_ENDPOINT = "http://localhost:9999/crm"
# RISK_ALERT_ENDPOINT = "http://localhost:9999/risk_alert"


# def route_action(agent: str, extraction: dict, input_id: int) -> dict:
#     action = None
#     details = {}
#     # Email agent: escalate if angry/high urgency
#     if agent == "EmailAgent":
#         tone = extraction.get("tone", "").lower()
#         urgency = extraction.get("urgency", "").lower()
#         if tone in ["angry", "escalation"] and urgency == "high":
#             action = "POST /crm/escalate"
#             details = {"escalate": True, "reason": f"tone={tone}, urgency={urgency}"}
#             # Simulate REST call (commented out for demo)
#             # requests.post(CRM_ENDPOINT + "/escalate", json=extraction)
#         else:
#             action = "LOG /crm/close"
#             details = {"escalate": False}
#     # JSON agent: flag anomalies
#     elif agent == "JSONAgent":
#         if extraction.get("anomalies"):
#             action = "POST /risk_alert"
#             details = {"anomalies": extraction["anomalies"]}
#             # Simulate REST call
#             # requests.post(RISK_ALERT_ENDPOINT, json=extraction)
#         else:
#             action = "LOG /json/ok"
#     # PDF agent: flag compliance or high invoice
#     elif agent == "PDFAgent":
#         flags = extraction.get("flags", [])
#         if flags:
#             action = "POST /risk_alert"
#             details = {"flags": flags}
#             # Simulate REST call
#             # requests.post(RISK_ALERT_ENDPOINT, json=extraction)
#         else:
#             action = "LOG /pdf/ok"
#     else:
#         action = "LOG /unknown_agent"
#     # Log action to memory
#     memory.log_action(action_type=action, details=details, input_id=input_id)
#     return {"action": action, "details": details}





import io
import re
import json
import requests
from typing import Optional, Dict
from PyPDF2 import PdfReader
from memory.memory_store import MemoryStore
from utils.llm_client import call_llm

memory = MemoryStore()

COMPLIANCE_KEYWORDS = ["GDPR", "FDA", "HIPAA", "PCI"]

CRM_ENDPOINT = "http://localhost:9999/crm"
RISK_ALERT_ENDPOINT = "http://localhost:9999/risk_alert"

PDF_EXTRACTION_PROMPT = """
Given the following extracted text from a PDF (invoice or policy document), extract the following fields and flag any risks. Return your answer as a JSON object with keys: invoice_total (float or null), compliance_mentions (list of keywords like GDPR, FDA, etc.), flags (list of risk/compliance flags), intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General).
Only return a valid JSON.

Examples:
---
Text:
Invoice #12345\nTotal: 12000.00\nThis invoice is subject to GDPR.\nOutput:
{"invoice_total": 12000.0, "compliance_mentions": ["GDPR"], "flags": ["Invoice total exceeds 10,000: 12000.0", "Mentions compliance keywords: GDPR"], "intent": "Invoice"}
---
Text:
Policy Document\nThis policy is compliant with FDA and HIPAA.\nOutput:
{"invoice_total": null, "compliance_mentions": ["FDA", "HIPAA"], "flags": ["Mentions compliance keywords: FDA, HIPAA"], "intent": "Regulation"}
---
Text:
{text_excerpt}
Output:
"""

def extract_last_json(text):
    matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
    if matches:
        for match in reversed(matches):
            try:
                return json.loads(match.group(0))
            except:
                continue
    return {"error": "Failed to parse last JSON", "raw_response": text}

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting PDF text: {e}"

def extract_invoice_total(text: str) -> Optional[float]:
    matches = re.findall(r'(?:total|amount due)[:\s\$]*([\d,]+\.\d{2})', text, re.IGNORECASE)
    if matches:
        try:
            return float(matches[0].replace(",", ""))
        except:
            return None
    return None

def extract_compliance_mentions(text: str) -> list:
    found = []
    for keyword in COMPLIANCE_KEYWORDS:
        if keyword.lower() in text.lower():
            found.append(keyword)
    return found

def process_pdf(pdf_bytes: bytes, source: str = None, input_id: int = None) -> Dict:
    text = extract_text_from_pdf(pdf_bytes)
    text_excerpt = text[:2000]
    prompt = PDF_EXTRACTION_PROMPT.replace("{text_excerpt}", text_excerpt)
    response = call_llm(prompt)
    result = extract_last_json(response)

    # Fallbacks if LLM extraction fails or is incomplete
    if not result.get("invoice_total"):
        total = extract_invoice_total(text)
        if total:
            result["invoice_total"] = total
            if total > 10000:
                result.setdefault("flags", []).append(f"Invoice total exceeds 10,000: {total}")
            result["intent"] = "Invoice"
    if not result.get("compliance_mentions"):
        mentions = extract_compliance_mentions(text)
        if mentions:
            result["compliance_mentions"] = mentions
            result.setdefault("flags", []).append(f"Mentions compliance keywords: {', '.join(mentions)}")
            result["intent"] = result.get("intent", "Regulation")
    if not result.get("intent"):
        result["intent"] = "General"

    if input_id is not None:
        memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
        if result.get("flags"):
            memory.log_action(action_type="pdf_flag", details={"flags": result["flags"]}, input_id=input_id)

    return result

def route_action(agent: str, extraction: dict, input_id: int) -> dict:
    action = "LOG /unknown_agent"
    details = {}
    if agent == "EmailAgent":
        tone = (extraction.get("tone") or "").lower()
        urgency = (extraction.get("urgency") or "").lower()
        if tone in ["angry", "escalation"] and urgency == "high":
            action = "POST /crm/escalate"
            details = {"escalate": True, "reason": f"tone={tone}, urgency={urgency}"}
            # requests.post(CRM_ENDPOINT + "/escalate", json=extraction)
        else:
            action = "LOG /crm/close"
            details = {"escalate": False}
    elif agent == "JSONAgent":
        if extraction.get("anomalies"):
            action = "POST /risk_alert"
            details = {"anomalies": extraction["anomalies"]}
            # requests.post(RISK_ALERT_ENDPOINT, json=extraction)
        else:
            action = "LOG /json/ok"
    elif agent == "PDFAgent":
        if extraction.get("flags"):
            action = "POST /risk_alert"
            details = {"flags": extraction["flags"]}
            # requests.post(RISK_ALERT_ENDPOINT, json=extraction)
        else:
            action = "LOG /pdf/ok"

    memory.log_action(action_type=action, details=details, input_id=input_id)
    return {"action": action, "details": details}
