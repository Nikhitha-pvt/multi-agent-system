# # # # import io
# # # # from PyPDF2 import PdfReader
# # # # from typing import Optional, Dict
# # # # from memory.memory_store import MemoryStore
# # # # from utils.llm_client import call_llm
# # # # import re
# # # # import json

# # # # def extract_last_json(text):
# # # #     matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
# # # #     if matches:
# # # #         last_json = matches[-1].group(0)
# # # #         try:
# # # #             return json.loads(last_json)
# # # #         except Exception:
# # # #             return {"error": "Failed to parse last JSON", "raw_response": last_json}
# # # #     return {"error": "No JSON found", "raw_response": text}

# # # # memory = MemoryStore()

# # # # COMPLIANCE_KEYWORDS = ["GDPR", "FDA", "HIPAA", "PCI"]

# # # # PDF_EXTRACTION_PROMPT = """
# # # # Given the following extracted text from a PDF (invoice or policy document), extract the following fields and flag any risks. Return your answer as a JSON object with keys: invoice_total (float or null), compliance_mentions (list of keywords like GDPR, FDA, etc.), flags (list of risk/compliance flags), intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General).

# # # # Examples:
# # # # ---
# # # # Text:
# # # # Invoice #12345\\nTotal: 12000.00\\nThis invoice is subject to GDPR.\\nOutput:
# # # # {{"invoice_total": 12000.0, "compliance_mentions": ["GDPR"], "flags": ["Invoice total exceeds 10,000: 12000.0", "Mentions compliance keywords: GDPR"], "intent": "Invoice"}}
# # # # ---
# # # # Text:
# # # # Policy Document\\nThis policy is compliant with FDA and HIPAA.\\nOutput:
# # # # {{"invoice_total": null, "compliance_mentions": ["FDA", "HIPAA"], "flags": ["Mentions compliance keywords: FDA, HIPAA"], "intent": "Regulation"}}
# # # # ---
# # # # Text:
# # # # {text_excerpt}
# # # # Output:
# # # # """


# # # # def extract_text_from_pdf(pdf_bytes: bytes) -> str:
# # # #     try:
# # # #         reader = PdfReader(io.BytesIO(pdf_bytes))
# # # #         text = ""
# # # #         for page in reader.pages:
# # # #             text += page.extract_text() or ""
# # # #         return text
# # # #     except Exception as e:
# # # #         return f"Error extracting PDF text: {e}"


# # # # def extract_invoice_total(text: str) -> Optional[float]:
# # # #     # Look for patterns like 'Total: 12345.67' or 'Amount Due: $12,345.67'
# # # #     matches = re.findall(r'(?:total|amount due)[:\s\$]*([\d,]+\.\d{2})', text, re.IGNORECASE)
# # # #     if matches:
# # # #         # Remove commas and convert to float
# # # #         try:
# # # #             return float(matches[0].replace(",", ""))
# # # #         except:
# # # #             return None
# # # #     return None


# # # # def extract_compliance_mentions(text: str) -> list:
# # # #     found = []
# # # #     for keyword in COMPLIANCE_KEYWORDS:
# # # #         if keyword.lower() in text.lower():
# # # #             found.append(keyword)
# # # #     return found


# # # # def process_pdf(pdf_bytes: bytes, source: str = None, input_id: int = None) -> Dict:
# # # #     text = extract_text_from_pdf(pdf_bytes)
# # # #     text_excerpt = text[:2000]
# # # #     prompt = PDF_EXTRACTION_PROMPT.format(text_excerpt=text_excerpt)
# # # #     response = call_llm(prompt)
# # # #     result = extract_last_json(response)
# # # #     # Log extraction to memory
# # # #     if input_id is not None:
# # # #         memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
# # # #         if result.get("flags"):
# # # #             memory.log_action(action_type="pdf_flag", details={"flags": result["flags"]}, input_id=input_id)
# # # #     return result











# # # import io
# # # import re
# # # import json
# # # from typing import Optional, Dict
# # # from PyPDF2 import PdfReader
# # # from memory.memory_store import MemoryStore
# # # from utils.llm_client import call_llm

# # # memory = MemoryStore()

# # # COMPLIANCE_KEYWORDS = ["GDPR", "FDA", "HIPAA", "PCI"]

# # # PDF_EXTRACTION_PROMPT = """
# # # Given the following extracted text from a PDF (invoice or policy document), extract the following fields and flag any risks. Return your answer as a JSON object with keys: invoice_total (float or null), compliance_mentions (list of keywords like GDPR, FDA, etc.), flags (list of risk/compliance flags), intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General).
# # # Only return a valid JSON.

# # # Examples:
# # # ---
# # # Text:
# # # Invoice #12345\nTotal: 12000.00\nThis invoice is subject to GDPR.\nOutput:
# # # {"invoice_total": 12000.0, "compliance_mentions": ["GDPR"], "flags": ["Invoice total exceeds 10,000: 12000.0", "Mentions compliance keywords: GDPR"], "intent": "Invoice"}
# # # ---
# # # Text:
# # # Policy Document\nThis policy is compliant with FDA and HIPAA.\nOutput:
# # # {"invoice_total": null, "compliance_mentions": ["FDA", "HIPAA"], "flags": ["Mentions compliance keywords: FDA, HIPAA"], "intent": "Regulation"}
# # # ---
# # # Text:
# # # {text_excerpt}
# # # Output:
# # # """

# # # def extract_text_from_pdf(pdf_bytes: bytes) -> str:
# # #     try:
# # #         reader = PdfReader(io.BytesIO(pdf_bytes))
# # #         text = ""
# # #         for page in reader.pages:
# # #             text += page.extract_text() or ""
# # #         return text
# # #     except Exception as e:
# # #         return f"Error extracting PDF text: {e}"

# # # def extract_invoice_total(text: str) -> Optional[float]:
# # #     matches = re.findall(r'(?:total|amount due)[:\s\$]*([\d,]+\.\d{2})', text, re.IGNORECASE)
# # #     if matches:
# # #         try:
# # #             return float(matches[0].replace(",", ""))
# # #         except:
# # #             return None
# # #     return None

# # # def extract_compliance_mentions(text: str) -> list:
# # #     found = []
# # #     for keyword in COMPLIANCE_KEYWORDS:
# # #         if keyword.lower() in text.lower():
# # #             found.append(keyword)
# # #     return found

# # # def process_pdf(pdf_bytes: bytes, source: str = None, input_id: int = None) -> Dict:
# # #     text = extract_text_from_pdf(pdf_bytes)
# # #     text_excerpt = text[:2000]
# # #     prompt = PDF_EXTRACTION_PROMPT.replace("{text_excerpt}", text_excerpt)
# # #     response = call_llm(prompt)
# # #     result = extract_last_json(response)

# # #     # Fallbacks if LLM extraction fails or is incomplete
# # #     if not result.get("invoice_total"):
# # #         total = extract_invoice_total(text)
# # #         if total:
# # #             result["invoice_total"] = total
# # #             if total > 10000:
# # #                 result.setdefault("flags", []).append(f"Invoice total exceeds 10,000: {total}")
# # #             result["intent"] = "Invoice"
# # #     if not result.get("compliance_mentions"):
# # #         mentions = extract_compliance_mentions(text)
# # #         if mentions:
# # #             result["compliance_mentions"] = mentions
# # #             result.setdefault("flags", []).append(f"Mentions compliance keywords: {', '.join(mentions)}")
# # #             result["intent"] = result.get("intent", "Regulation")
# # #     if not result.get("intent"):
# # #         result["intent"] = "General"

# # #     if input_id is not None:
# # #         memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
# # #         if result.get("flags"):
# # #             memory.log_action(action_type="pdf_flag", details={"flags": result["flags"]}, input_id=input_id)

# # #     return result




# # import io
# # import re
# # import json
# # import requests
# # from typing import Optional, Dict
# # from PyPDF2 import PdfReader
# # from memory.memory_store import MemoryStore
# # from utils.llm_client import call_llm
# # import time

# # memory = MemoryStore()

# # COMPLIANCE_KEYWORDS = ["GDPR", "FDA", "HIPAA", "PCI"]

# # CRM_ENDPOINT = "http://localhost:9999/crm"
# # RISK_ALERT_ENDPOINT = "http://localhost:9999/risk_alert"

# # PDF_EXTRACTION_PROMPT = """
# # Given the following extracted text from a PDF (invoice or policy document), extract the following fields and flag any risks. Return your answer as a JSON object with keys: invoice_total (float or null), compliance_mentions (list of keywords like GDPR, FDA, etc.), flags (list of risk/compliance flags), intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General).
# # Only return a valid JSON.

# # Examples:
# # ---
# # Text:
# # Invoice #12345\nTotal: 12000.00\nThis invoice is subject to GDPR.\nOutput:
# # {{"invoice_total": 12000.0, "compliance_mentions": ["GDPR"], "flags": ["Invoice total exceeds 10,000: 12000.0", "Mentions compliance keywords: GDPR"], "intent": "Invoice"}}
# # ---
# # Text:
# # Policy Document\nThis policy is compliant with FDA and HIPAA.\nOutput:
# # {{"invoice_total": null, "compliance_mentions": ["FDA", "HIPAA"], "flags": ["Mentions compliance keywords: FDA, HIPAA"], "intent": "Regulation"}}
# # ---
# # Text:
# # {text_excerpt}
# # Output:
# # """

# # def extract_last_json(text):
# #     matches = list(re.finditer(r'\{.*?\}', text, re.DOTALL))
# #     if matches:
# #         for match in reversed(matches):
# #             try:
# #                 return json.loads(match.group(0))
# #             except:
# #                 continue
# #     return {"error": "Failed to parse last JSON", "raw_response": text}

# # def retry_call(func, retries=3, delay=1, *args, **kwargs):
# #     for attempt in range(retries):
# #         try:
# #             return func(*args, **kwargs)
# #         except Exception as e:
# #             if attempt < retries - 1:
# #                 time.sleep(delay)
# #             else:
# #                 raise e

# # def extract_text_from_pdf(pdf_bytes: bytes) -> str:
# #     try:
# #         reader = PdfReader(io.BytesIO(pdf_bytes))
# #         text = ""
# #         for page in reader.pages:
# #             text += page.extract_text() or ""
# #         return text
# #     except Exception as e:
# #         return f"Error extracting PDF text: {e}"

# # def extract_invoice_total(text: str) -> Optional[float]:
# #     matches = re.findall(r'(?:total|amount due)[:\s\$]*([\d,]+\.\d{2})', text, re.IGNORECASE)
# #     if matches:
# #         try:
# #             return float(matches[0].replace(",", ""))
# #         except:
# #             return None
# #     return None

# # def extract_compliance_mentions(text: str) -> list:
# #     found = []
# #     for keyword in COMPLIANCE_KEYWORDS:
# #         if keyword.lower() in text.lower():
# #             found.append(keyword)
# #     return found

# # def process_pdf(pdf_bytes: bytes, source: str = None, input_id: int = None) -> Dict:
# #     text = extract_text_from_pdf(pdf_bytes)
# #     if text.startswith("Error extracting PDF text"):
# #         result = {"error": text, "raw_response": ""}
# #         if input_id is not None:
# #             memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
# #         return result

# #     text_excerpt = text[:2000]
# #     prompt = PDF_EXTRACTION_PROMPT.replace("{text_excerpt}", text_excerpt)

# #     try:
# #         response = retry_call(call_llm, args=(prompt,))
# #     except Exception as e:
# #         response = f"LLM call failed: {e}"
# #         result = {"error": response, "raw_response": ""}
# #         if input_id is not None:
# #             memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
# #         return result

# #     result = extract_last_json(response)
# #     if isinstance(result, str):
# #         result = {"error": "Invalid JSON from LLM", "raw_response": result}

# #     # Fallbacks
# #     if not result.get("invoice_total"):
# #         total = extract_invoice_total(text)
# #         if total:
# #             result["invoice_total"] = total
# #             result.setdefault("flags", []).append(f"Invoice total exceeds 10,000: {total}")
# #             result["intent"] = "Invoice"

# #     if not result.get("compliance_mentions"):
# #         mentions = extract_compliance_mentions(text)
# #         if mentions:
# #             result["compliance_mentions"] = mentions
# #             result.setdefault("flags", []).append(f"Mentions compliance keywords: {', '.join(mentions)}")
# #             result["intent"] = result.get("intent", "Regulation")

# #     if not result.get("intent"):
# #         result["intent"] = "General"

# #     if input_id is not None:
# #         memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
# #         if result.get("flags"):
# #             memory.log_action(action_type="pdf_flag", details={"flags": result["flags"]}, input_id=input_id)

# #     return result


# # def route_action(agent: str, extraction: dict, input_id: int) -> dict:
# #     action = "LOG /unknown_agent"
# #     details = {}
# #     if agent == "EmailAgent":
# #         tone = (extraction.get("tone") or "").lower()
# #         urgency = (extraction.get("urgency") or "").lower()
# #         if tone in ["angry", "escalation"] and urgency == "high":
# #             action = "POST /crm/escalate"
# #             details = {"escalate": True, "reason": f"tone={tone}, urgency={urgency}"}
# #         else:
# #             action = "LOG /crm/close"
# #             details = {"escalate": False}
# #     elif agent == "JSONAgent":
# #         if extraction.get("anomalies"):
# #             action = "POST /risk_alert"
# #             details = {"anomalies": extraction["anomalies"]}
# #         else:
# #             action = "LOG /json/ok"
# #     elif agent == "PDFAgent":
# #         if extraction.get("flags"):
# #             action = "POST /risk_alert"
# #             details = {"flags": extraction["flags"]}
# #         else:
# #             action = "LOG /pdf/ok"

# #     memory.log_action(action_type=action, details=details, input_id=input_id)
# #     return {"action": action, "details": details}








# import io
# import re
# import json
# import time
# from typing import Optional, Dict
# from PyPDF2 import PdfReader

# from memory.memory_store import MemoryStore
# from utils.llm_client import call_llm

# memory = MemoryStore()

# COMPLIANCE_KEYWORDS = ["GDPR", "FDA", "HIPAA", "PCI"]

# # Prompt to the LLM: extract invoice_total, compliance_mentions, flags, and intent.
# PDF_EXTRACTION_PROMPT = """
# Given the following extracted text from a PDF (invoice or policy document), extract the following fields and flag any risks. 
# Return your answer as a JSON object with keys: 
#   - invoice_total (float or null)
#   - compliance_mentions (list of keywords like GDPR, FDA, etc.)
#   - flags (list of risk/compliance flags)
#   - intent (Invoice, Complaint, RFQ, Regulation, Fraud Risk, General).

# Only return a valid JSON.

# Examples:
# ---
# Text:
# Invoice #12345
# Total: 12000.00
# This invoice is subject to GDPR.
# Output:
# {{"invoice_total": 12000.0, 
#  "compliance_mentions": ["GDPR"], 
#  "flags": ["Invoice total exceeds 10,000: 12000.0", "Mentions compliance keywords: GDPR"], 
#  "intent": "Invoice"}}
# ---
# Text:
# Policy Document
# This policy is compliant with FDA and HIPAA.
# Output:
# {{"invoice_total": null, 
#  "compliance_mentions": ["FDA", "HIPAA"], 
#  "flags": ["Mentions compliance keywords: FDA, HIPAA"], 
#  "intent": "Regulation"}}
# ---
# Text:
# {text_excerpt}
# Output:
# """


# def extract_last_json(text: str) -> Dict:
#     """
#     Locate the last {...} block in `text` and attempt to parse it as JSON.
#     If parsing fails entirely, return an error structure.
#     """
#     matches = list(re.finditer(r'\{(?:[^{}]|(?R))*\}', text, re.DOTALL))
#     if matches:
#         for match in reversed(matches):
#             try:
#                 return json.loads(match.group(0))
#             except json.JSONDecodeError:
#                 continue

#     return {"error": "Failed to parse last JSON", "raw_response": text}


# def retry_call(func, retries: int = 3, delay: float = 1, *args, **kwargs):
#     """
#     Retry `func(*args, **kwargs)` up to `retries` times, sleeping `delay` seconds between attempts.
#     """
#     for attempt in range(retries):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             if attempt < retries - 1:
#                 time.sleep(delay)
#             else:
#                 # Last attempt failed, re‐raise
#                 raise e


# def extract_text_from_pdf(pdf_bytes: bytes) -> str:
#     """
#     Read all pages from pdf_bytes using PyPDF2 and return concatenated text.
#     If PyPDF2 fails, return an error string.
#     """
#     try:
#         reader = PdfReader(io.BytesIO(pdf_bytes))
#         text = ""
#         for page in reader.pages:
#             page_text = page.extract_text() or ""
#             text += page_text
#         return text
#     except Exception as e:
#         return f"Error extracting PDF text: {e}"


# def extract_invoice_total(text: str) -> Optional[float]:
#     """
#     Use a regex to find a monetary amount after keywords like "Total", "Amount Due", or "Total Due".
#     Return a float if found, else None.
#     """
#     # Look for patterns like "Total Due $93.50" or "Total: 12000.00"
#     matches = re.findall(r'(?:total\s+due|total|amount\s+due|sub\s+total)[:\s\$]*([\d,]+\.\d{2})',
#                          text, re.IGNORECASE)
#     if matches:
#         try:
#             # Take the first match, strip commas, cast to float
#             return float(matches[0].replace(",", ""))
#         except ValueError:
#             return None
#     return None


# def extract_compliance_mentions(text: str) -> list:
#     """
#     Scan `text` for any of the COMPLIANCE_KEYWORDS (case-insensitive).
#     Return all found keywords in a list (empty list if none found).
#     """
#     found = []
#     lower_text = text.lower()
#     for kw in COMPLIANCE_KEYWORDS:
#         if kw.lower() in lower_text:
#             found.append(kw)
#     return found


# def process_pdf(pdf_bytes: bytes, source: str = None, input_id: int = None) -> Dict:
#     """
#     1. Extract raw text from PDF.
#     2. Send up to 2,000 characters to the LLM for JSON extraction of invoice_total, compliance_mentions, flags, intent.
#     3. If LLM fails or is incomplete, fallback to regex-based invoice_total and compliance_mentions.
#     4. Only add a flag if invoice_total > 10,000 or compliance_mentions is non-empty.
#     5. Top-level 'intent' is set to whatever was extracted.
#     6. Log extraction and any flags into shared memory.

#     Returns a dict with keys: 
#       "invoice_total", "compliance_mentions", "flags", "intent",
#       or an error structure if PDF extraction / LLM fails.
#     """
#     # 1) Extract full text from PDF
#     text = extract_text_from_pdf(pdf_bytes)
#     if text.startswith("Error extracting PDF text"):
#         # If PyPDF2 failed, bail out with error
#         result = {"error": text, "raw_response": ""}
#         if input_id is not None:
#             memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
#         return result

#     # 2) Call the LLM on the first ~2,000 chars for structured JSON output
#     text_excerpt = text[:2000]
#     prompt = PDF_EXTRACTION_PROMPT.replace("{text_excerpt}", text_excerpt)

#     try:
#         # Use a lambda so retry_call invokes call_llm with prompt=prompt
#         response = retry_call(lambda: call_llm(prompt=prompt))
#     except Exception as e:
#         # LLM call failed completely; log and return error
#         response_str = f"LLM call failed: {e}"
#         result = {"error": response_str, "raw_response": ""}
#         if input_id is not None:
#             memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
#         return result

#     # 3) Attempt to parse the LLM’s JSON
#     parsed = extract_last_json(response)
#     # If extract_last_json returns a string (unlikely, but just in case), wrap in error
#     if not isinstance(parsed, dict):
#         parsed = {"error": "Invalid JSON from LLM", "raw_response": response}

#     # Ensure we have keys in `parsed`. If missing, initialize defaults:
#     invoice_total = parsed.get("invoice_total")
#     compliance_mentions = parsed.get("compliance_mentions")
#     flags = parsed.get("flags") or []
#     extracted_intent = parsed.get("intent") or ""

#     # 4) FALLBACKS FOR MISSING FIELDS
#     # If LLM didn’t return invoice_total, try regex-based fallback
#     if invoice_total is None:
#         total = extract_invoice_total(text)
#         if total is not None:
#             invoice_total = total
#         else:
#             invoice_total = None

#     # If LLM didn’t return compliance_mentions (or returned null), do fallback
#     if not isinstance(compliance_mentions, list):
#         compliance_mentions = extract_compliance_mentions(text)

#     # 5) DETERMINE FLAGS (only if real risk/compliance conditions)
#     new_flags = []
#     # a) If invoice_total > 10,000, flag it
#     if isinstance(invoice_total, (int, float)) and invoice_total > 10000:
#         new_flags.append(f"Invoice total exceeds 10,000: {invoice_total}")

#     # b) If we found any compliance keyword, flag it
#     if compliance_mentions:
#         joined = ", ".join(compliance_mentions)
#         new_flags.append(f"Mentions compliance keywords: {joined}")

#     # c) Don’t add any other flags (e.g. <10k or "due within 30 days" are not risks per spec)

#     # If LLM returned some flags (and they look valid), append them as well
#     # But we should only trust LLM’s flags if they match the above conditions.
#     # For simplicity, we’ll ignore LLM’s “flags” array entirely, and rebuild from our rules.
#     flags = new_flags

#     # 6) Determine final intent
#     # If LLM gave an intent, use that; otherwise, if invoice_total != None => "Invoice"; else "General"
#     if extracted_intent:
#         final_intent = extracted_intent
#     else:
#         final_intent = "Invoice" if invoice_total is not None else "General"

#     # 7) Build the result dict
#     result = {
#         "invoice_total": invoice_total,
#         "compliance_mentions": compliance_mentions,
#         "flags": flags,
#         "intent": final_intent
#     }

#     # 8) Log extraction + flags into memory
#     if input_id is not None:
#         memory.log_extraction(agent="PDFAgent", extracted_fields=result, input_id=input_id)
#         if flags:
#             memory.log_action(action_type="pdf_flag", details={"flags": flags}, input_id=input_id)

#     return result


# def route_action(agent: str, extraction: dict, input_id: int) -> dict:
#     """
#     Given an agent name ("EmailAgent", "JSONAgent", or "PDFAgent") and its `extraction`,
#     choose the correct follow‐up action. Log into memory and return {"action": ..., "details": ...}.
#     """
#     action = "LOG /unknown_agent"
#     details = {}

#     if agent == "EmailAgent":
#         tone = (extraction.get("tone") or "").lower()
#         urgency = (extraction.get("urgency") or "").lower()
#         if tone in ["angry", "escalation"] and urgency == "high":
#             action = "POST /crm/escalate"
#             details = {
#                 "escalate": True,
#                 "reason": f"tone={tone}, urgency={urgency}"
#             }
#         else:
#             action = "LOG /crm/close"
#             details = {"escalate": False}

#     elif agent == "JSONAgent":
#         if extraction.get("anomalies"):
#             action = "POST /risk_alert"
#             details = {"anomalies": extraction["anomalies"]}
#         else:
#             action = "LOG /json/ok"

#     elif agent == "PDFAgent":
#         # Only escalate if there are genuine flags
#         if extraction.get("flags"):
#             action = "POST /risk_alert"
#             details = {"flags": extraction["flags"]}
#         else:
#             action = "LOG /pdf/ok"

#     # Write to shared memory
#     memory.log_action(action_type=action, details=details, input_id=input_id)
#     return {"action": action, "details": details}


























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