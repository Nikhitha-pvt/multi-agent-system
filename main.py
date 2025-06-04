from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from memory.memory_store import MemoryStore
from typing import Optional
from agents.classifier_agent import classify_input
from agents.email_agent import process_email
from agents.json_agent import process_json
from agents.pdf_agent import process_pdf
from mcp.action_router import route_action
from utils.serializers import serialize_datetime
import json

app = FastAPI()
memory_store = MemoryStore()

# --- Ingest endpoint (now uses classifier agent) ---
@app.post("/ingest/")
async def ingest_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    format_type, intent = classify_input(content, filename)
    input_id = memory_store.log_input(source=filename, input_type=format_type, intent=intent, metadata=None)

    extraction_result = None
    action_result = None
    if format_type == "Email":
        email_text = content.decode("utf-8", errors="ignore")
        extraction_result = process_email(email_text, source=filename, input_id=input_id)
        action_result = route_action("EmailAgent", extraction_result, input_id)
    elif format_type == "JSON":
        try:
            data = json.loads(content)
            extraction_result = process_json(data, source=filename, input_id=input_id)
            action_result = route_action("JSONAgent", extraction_result, input_id)
        except Exception as e:
            extraction_result = {"error": f"Invalid JSON: {str(e)}"}
    elif format_type == "PDF":
        extraction_result = process_pdf(content, source=filename, input_id=input_id)
        action_result = route_action("PDFAgent", extraction_result, input_id)

    return {
        "filename": filename,
        "format": format_type,
        "intent": intent,
        "input_id": input_id,
        "status": "classified",
        "extraction": extraction_result,
        "action": action_result
    }

# --- Memory logs endpoint ---
@app.get("/memory/")
def get_memory():
    logs = memory_store.get_logs()  # Your existing log retrieval
    serialized_logs = json.loads(
        json.dumps(logs, default=serialize_datetime)
    )
    return JSONResponse(content=serialized_logs)

# (Other agent endpoints will be added/updated in later steps)

from pydantic import BaseModel
from typing import Any

class JSONPayload(BaseModel):
    {
    "data": {
    "id": "evt_12345",
    "event_type": "payment_success",
    "timestamp": "2024-06-01T12:00:00",
    "payload": {
      "customer_id": "cust_001",
      "amount": 5000.75,
      "currency": "USD"
    }
  }
}

@app.post("/process/json/")
async def handle_json(request: Request):
    data = await request.json()
    # For direct JSON, we don't have a filename, so use 'direct_payload' as source
    input_id = memory_store.log_input(source="direct_payload", input_type="JSON", intent="Unknown", metadata=None)
    result = process_json(data, source="direct_payload", input_id=input_id)
    action_result = route_action("JSONAgent", result, input_id)
    return {"extraction": result, "action": action_result}
