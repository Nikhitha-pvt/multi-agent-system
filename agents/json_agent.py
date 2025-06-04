# import json
# from datetime import datetime
# from memory.memory_store import MemoryStore
# from typing import Dict, Any
# from utils.llm_client import call_llm
# import re

# def extract_last_json(text):
#     matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
#     if matches:
#         last_json = matches[-1].group(0)
#         try:
#             return json.loads(last_json)
#         except Exception:
#             return {"error": "Failed to parse last JSON", "raw_response": last_json}
#     return {"error": "No JSON found", "raw_response": text}

# def is_iso_timestamp(ts: str) -> bool:
#     try:
#         datetime.fromisoformat(ts)
#         return True
#     except:
#         return False

# def validate_schema(data: dict) -> dict:
#     issues = []

#     # Top level checks
#     if "id" not in data or not isinstance(data["id"], str):
#         issues.append("Missing or invalid 'id'")
#     if "event_type" not in data or not isinstance(data["event_type"], str):
#         issues.append("Missing or invalid 'event_type'")
#     if "timestamp" not in data or not is_iso_timestamp(data["timestamp"]):
#         issues.append("Missing or invalid 'timestamp'")

#     payload = data.get("payload", {})
#     if not isinstance(payload, dict):
#         issues.append("Missing or invalid 'payload' object")
#     else:
#         if "customer_id" not in payload or not isinstance(payload["customer_id"], str):
#             issues.append("Missing or invalid 'customer_id'")
#         if "amount" not in payload or not isinstance(payload["amount"], (float, int)):
#             issues.append("Missing or invalid 'amount'")
#         if "currency" not in payload or not isinstance(payload["currency"], str):
#             issues.append("Missing or invalid 'currency'")

#     return {
#         "valid": len(issues) == 0,
#         "issues": issues
#     }

# memory = MemoryStore()

# # Example FlowBit schema for demonstration
# REQUIRED_FIELDS = ["id", "event_type", "timestamp", "payload"]
# PAYLOAD_FIELDS = ["customer_id", "amount", "currency"]

# JSON_EXTRACTION_PROMPT = """
# Given the following JSON payload, extract the following fields and validate the schema. Return your answer as a JSON object with keys: extracted (dict of all fields), anomalies (list of missing/invalid fields), intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General).

# Examples:
# ---
# Input:
# {{"id": "evt_12345", "event_type": "payment_success", "timestamp": "2024-06-01T12:00:00", "payload": {{"customer_id": "cust_001", "amount": 15000.0, "currency": "USD"}}}}
# Output:
# {{"extracted": {{"id": "evt_12345", "event_type": "payment_success", "timestamp": "2024-06-01T12:00:00", "payload": {{"customer_id": "cust_001", "amount": 15000.0, "currency": "USD"}}}}, "anomalies": [], "intent": "Invoice"}}
# ---
# Input:
# {{"id": "evt_12345", "event_type": "payment_success", "payload": {{"customer_id": "cust_001", "currency": "USD"}}}}
# Output:
# {{"extracted": {{"id": "evt_12345", "event_type": "payment_success", "payload": {{"customer_id": "cust_001", "currency": "USD"}}}}, "anomalies": ["Missing field: timestamp", "Missing payload field: amount"], "intent": "Invoice"}}
# ---
# Input:
# {json_excerpt}
# Output:
# """

# def process_json(data: Dict[str, Any], source: str = None, input_id: int = None) -> Dict:
#     json_excerpt = json.dumps(data)[:1500]
#     prompt = JSON_EXTRACTION_PROMPT.format(json_excerpt=json_excerpt)
#     response = call_llm(prompt)
#     result = extract_last_json(response)
#     # Log extraction to memory
#     if input_id is not None:
#         memory.log_extraction(agent="JSONAgent", extracted_fields=result, input_id=input_id)
#         if result.get("anomalies"):
#             memory.log_action(action_type="json_anomaly", details={"anomalies": result["anomalies"]}, input_id=input_id)
#     return result

















import json
import re
from datetime import datetime
from typing import Dict, Any
from memory.memory_store import MemoryStore
from utils.llm_client import call_llm

memory = MemoryStore()

def extract_last_json(text):
    matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
    if matches:
        for match in reversed(matches):
            try:
                return json.loads(match.group(0))
            except:
                continue
    return {"error": "Failed to parse last JSON", "raw_response": text}

def is_iso_timestamp(ts: str) -> bool:
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except:
        return False

def determine_intent(data: Dict[str, Any]) -> str:
    event = data.get("event_type", "").lower()
    if "complaint" in event:
        return "Complaint"
    if "fraud" in event or "risk" in event:
        return "Fraud Risk"
    if "invoice" in event or "payment" in event or "billing" in event:
        return "Invoice"
    return "General"

def validate_complaint_schema(data: dict) -> Dict:
    issues = []
    if "id" not in data or not isinstance(data["id"], str):
        issues.append("Missing or invalid 'id'")
    if "event_type" not in data or not isinstance(data["event_type"], str):
        issues.append("Missing or invalid 'event_type'")
    if "timestamp" not in data or not is_iso_timestamp(data["timestamp"]):
        issues.append("Missing or invalid 'timestamp'")
    payload = data.get("payload", {})
    if not isinstance(payload, dict):
        issues.append("Missing or invalid 'payload'")
    else:
        if "customer_id" not in payload:
            issues.append("Missing 'customer_id'")
        if "issue" not in payload:
            issues.append("Missing 'issue'")
        if "details" not in payload:
            issues.append("Missing 'details'")
    return issues

def validate_invoice_schema(data: dict) -> Dict:
    issues = []
    if "id" not in data or not isinstance(data["id"], str):
        issues.append("Missing or invalid 'id'")
    if "event_type" not in data or not isinstance(data["event_type"], str):
        issues.append("Missing or invalid 'event_type'")
    if "timestamp" not in data or not is_iso_timestamp(data["timestamp"]):
        issues.append("Missing or invalid 'timestamp'")
    payload = data.get("payload", {})
    if not isinstance(payload, dict):
        issues.append("Missing or invalid 'payload'")
    else:
        if "customer_id" not in payload or not isinstance(payload.get("customer_id"), str):
            issues.append("Missing or invalid 'customer_id'")
        if "amount" not in payload or not isinstance(payload.get("amount"), (int, float)):
            issues.append("Missing or invalid 'amount'")
        if "currency" not in payload or not isinstance(payload.get("currency"), str):
            issues.append("Missing or invalid 'currency'")
    return issues

def process_json(data: Dict[str, Any], source: str = None, input_id: int = None) -> Dict:
    intent = determine_intent(data)
    if intent == "Complaint":
        anomalies = validate_complaint_schema(data)
    else:
        anomalies = validate_invoice_schema(data)

    result = {
        "extracted": data,
        "anomalies": anomalies,
        "intent": intent
    }

    if input_id is not None:
        memory.log_extraction(agent="JSONAgent", extracted_fields=result, input_id=input_id)
        if anomalies:
            memory.log_action(action_type="json_anomaly", details={"anomalies": anomalies}, input_id=input_id)

    return result
