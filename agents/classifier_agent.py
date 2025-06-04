# import json
# import re
# from utils.llm_client import call_llm

# def extract_last_json(text):
#     matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
#     if matches:
#         last_json = matches[-1].group(0)
#         try:
#             return json.loads(last_json)
#         except Exception:
#             return {"error": "Failed to parse last JSON", "raw_response": last_json}
#     return {"error": "No JSON found", "raw_response": text}

# FEW_SHOT_PROMPT = """
# Classify the following input by format and business intent.

# Possible formats: PDF, JSON, Email
# Possible intents: Invoice, Complaint, RFQ, Regulation, Fraud Risk, General

# Examples:
# ---
# Input: Subject: Request for Quotation for Office Supplies\nBody: Hello, We are looking to procure office supplies for our new branch. Could you please provide a quotation for bulk orders of pens, notepads, and staplers? Best, John Smith
# Format: Email
# Intent: RFQ
# ---
# Input: {"id": "evt_12345", "event_type": "payment_success", "timestamp": "2024-06-01T12:00:00Z", "payload": {"customer_id": "cust_001", "amount": 5000.75, "currency": "USD"}}
# Format: JSON
# Intent: Invoice
# ---
# Input: Subject: Invoice #12345 for Services Rendered\nBody: Dear Accounts Payable, Please find attached Invoice #12345 for the consulting services provided in May. The total amount due is $5,000, payable within 30 days. Thank you, Alex Johnson
# Format: Email
# Intent: Invoice
# ---
# Input: Subject: Product Malfunction - Immediate Attention Required\nBody: Dear Customer Support, I purchased your XYZ gadget last week, and it's already malfunctioning. It won't turn on despite following all troubleshooting steps. Please advise on the return or replacement process. Regards, Jane Doe
# Format: Email
# Intent: Complaint
# ---
# Input: {input_excerpt}
# Format:
# Intent:
# Only output the Format and Intent for the last input.
# """

# def detect_format(content: bytes, filename: str) -> str:
#     if filename.endswith(".json"):
#         return "JSON"
#     elif filename.endswith(".pdf"):
#         return "PDF"
#     elif filename.endswith(".txt") or filename.endswith(".eml"):
#         return "Email"
#     else:
#         text_sample = content[:500].decode(errors="ignore").lower()
#         if "<html>" in text_sample or "subject:" in text_sample:
#             return "Email"
#         try:
#             json.loads(content)
#             return "JSON"
#         except:
#             return "PDF"  # fallback if unsure
        

# def detect_intent(text: str) -> str:
#     prompt = f"""Classify the business intent of the following content. Choose one from: [Invoice, Complaint, RFQ, Regulation, Fraud Risk].

# Content:
# {text[:1000]}"""  # LLM cost efficiency

#     return call_llm(prompt).strip().split("\n")[0]  # First line is usually enough


# def classify_input(content: bytes, filename: str):
#     ext = filename.lower().split('.')[-1]
#     try:
#         input_excerpt = content[:1000].decode(errors='ignore')
#     except Exception:
#         input_excerpt = str(content)[:1000]
#     # Add file extension as a hint
#     input_excerpt = f"[File extension: .{ext}]\n" + input_excerpt
#     # Use a different approach to avoid format string issues with curly braces
#     prompt = FEW_SHOT_PROMPT.replace("{input_excerpt}", input_excerpt)
#     response = call_llm(prompt)
#     print("LLM Classifier Response:", response)
#     format_type = "Unknown"
#     intent = "Unknown"
#     for line in response.splitlines():
#         if line.lower().startswith("format:"):
#             format_type = line.split(":", 1)[-1].strip()
#         if line.lower().startswith("intent:"):
#             intent = line.split(":", 1)[-1].strip()
#     return format_type, intent





import json
import re
from utils.llm_client import call_llm

def extract_last_json(text):
    matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
    if matches:
        for match in reversed(matches):
            try:
                return json.loads(match.group(0))
            except:
                continue
    return {"error": "Failed to parse JSON", "raw_response": text}

FEW_SHOT_PROMPT = """
Classify the following input by format and business intent.
Only return the result as a JSON object with two fields: format and intent.
Possible formats: PDF, JSON, Email
Possible intents: Invoice, Complaint, RFQ, Regulation, Fraud Risk, General

Examples:
---
Input: Subject: Request for Quotation for Office Supplies\nBody: Hello, We are looking to procure office supplies for our new branch. Could you please provide a quotation?
Output: {"format": "Email", "intent": "RFQ"}
---
Input: {"id": "evt_12345", "event_type": "payment_success", "timestamp": "2024-06-01T12:00:00Z", "payload": {"customer_id": "cust_001", "amount": 5000.75, "currency": "USD"}}
Output: {"format": "JSON", "intent": "Invoice"}
---
Input: Subject: Invoice #12345\nBody: Attached invoice. Total due $5000.
Output: {"format": "Email", "intent": "Invoice"}
---
Input:
{input_excerpt}
Output:
"""

def detect_format(content: bytes, filename: str) -> str:
    if filename.endswith(".json"):
        return "JSON"
    elif filename.endswith(".pdf"):
        return "PDF"
    elif filename.endswith(".txt") or filename.endswith(".eml"):
        return "Email"
    else:
        text_sample = content[:500].decode(errors="ignore").lower()
        if "subject:" in text_sample:
            return "Email"
        try:
            json.loads(content)
            return "JSON"
        except:
            return "PDF"  # fallback

def classify_input(content: bytes, filename: str):
    ext = filename.lower().split('.')[-1]
    try:
        input_excerpt = content[:1000].decode(errors='ignore')
    except Exception:
        input_excerpt = str(content)[:1000]

    prompt = FEW_SHOT_PROMPT.replace("{input_excerpt}", input_excerpt)
    response = call_llm(prompt)
    print("LLM Classifier Response:", response)
    result = extract_last_json(response)
    format_type = result.get("format", detect_format(content, filename))
    intent = result.get("intent", "General")
    return format_type, intent
