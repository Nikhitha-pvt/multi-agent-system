
import re
from typing import Optional, Dict
from memory.memory_store import MemoryStore
from utils.llm_client import call_llm
import json

def extract_last_json(text):
    matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
    if matches:
        for match in reversed(matches):
            try:
                return json.loads(match.group(0))
            except:
                continue
    return {"error": "Failed to parse last JSON", "raw_response": text}

memory = MemoryStore()

EMAIL_EXTRACTION_PROMPT = """
Extract the following fields from the email content below. Return your answer as a JSON object with keys: sender, urgency (low/medium/high), tone (polite/angry/threatening/escalation/neutral), intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General), request_or_issue (short summary).
Only return the JSON. No explanation or text.

Examples:
---
Email:
From: John Doe <john@example.com>\nSubject: Urgent Complaint\n\nHello,\nThis is unacceptable. I need this fixed immediately!\n\nRegards,\nJohn
Output:
{{"sender": "John Doe", "urgency": "high", "tone": "angry", "intent": "Complaint", "request_or_issue": "Customer is angry and wants an urgent fix."}}
---
Email:
From: Jane Smith <jane@company.com>\nSubject: Invoice Request\n\nHi,\nCan you please send me the latest invoice?\nThanks!\nJane
Output:
{{"sender": "Jane Smith", "urgency": "low", "tone": "polite", "intent": "Invoice", "request_or_issue": "Request for latest invoice."}}
---
Email:
{email_excerpt}
Output:
"""

def extract_sender(email_text: str) -> Optional[str]:
    match = re.search(r'From:\s*(.*?)(?:<.*?>)?\n', email_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r'[\w\.-]+@[\w\.-]+', email_text)
    if match:
        return match.group(0)
    return None

def extract_urgency(email_text: str) -> str:
    text = email_text.lower()
    if any(word in text for word in ["urgent", "immediately", "asap", "as soon as possible", "critical"]):
        return "high"
    elif any(word in text for word in ["soon", "priority", "important"]):
        return "medium"
    else:
        return "low"

def extract_tone(email_text: str) -> str:
    text = email_text.lower()
    if any(word in text for word in ["angry", "unacceptable", "complain", "escalate", "threaten", "disappointed"]):
        return "angry"
    elif any(word in text for word in ["please", "kindly", "thank you", "appreciate"]):
        return "polite"
    elif any(word in text for word in ["immediately", "now", "asap"]):
        return "escalation"
    else:
        return "neutral"

def extract_intent(email_text: str) -> str:
    text = email_text.lower()
    if "invoice" in text:
        return "Invoice"
    elif "rfq" in text or "request for quote" in text or "quotation" in text:
        return "RFQ"
    elif "complaint" in text or "issue" in text:
        return "Complaint"
    elif "regulation" in text or "policy" in text:
        return "Regulation"
    elif "fraud" in text or "risk" in text:
        return "Fraud Risk"
    else:
        return "General"

def extract_conversation_id(email_text: str) -> Optional[str]:
    match = re.search(r'(Conversation-ID|Thread-ID):\s*(\S+)', email_text, re.IGNORECASE)
    if match:
        return match.group(2)
    return None

def route_email_action(tone: str, urgency: str) -> str:
    if tone in ["angry", "escalation"] and urgency == "high":
        return "POST /crm/escalate"
    else:
        return "LOG /crm/close"

def process_email(email_text: str, source: str = None, input_id: int = None) -> Dict:
    email_excerpt = email_text[:1500]
    prompt = EMAIL_EXTRACTION_PROMPT.format(email_excerpt=email_excerpt)
    response = call_llm(prompt)
    metadata = extract_last_json(response)

    # Fallback if sender or intent is missing
    if not metadata.get("sender"):
        metadata["sender"] = extract_sender(email_text)
    if not metadata.get("intent") or metadata["intent"] == "General":
        metadata["intent"] = extract_intent(email_text)
    if not metadata.get("urgency"):
        metadata["urgency"] = extract_urgency(email_text)
    if not metadata.get("tone"):
        metadata["tone"] = extract_tone(email_text)

    # Log extraction to memory
    if input_id is not None:
        memory.log_extraction(agent="EmailAgent", extracted_fields=metadata, input_id=input_id)
    return metadata
