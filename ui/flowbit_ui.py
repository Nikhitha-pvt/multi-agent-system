import streamlit as st
import requests
from requests.exceptions import ConnectionError
from datetime import datetime
import json

st.title("Flowbit AI - Multi-Format Intake Demo")

st.write("Upload a PDF, JSON, or Email file. The system will classify, extract, and route automatically.")

API_URL = "http://localhost:8000"

# Check if API is available
def check_api_health():
    try:
        requests.get(API_URL)
        return True
    except ConnectionError:
        st.error("⚠️ API server is not running. Please start the FastAPI server with 'uvicorn main:app --reload'")
        return False

api_available = check_api_health()

uploaded_file = st.file_uploader("Choose a file (PDF, JSON, or Email)")

if uploaded_file is not None and api_available:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    try:
        with st.spinner("Processing..."):
            response = requests.post(f"{API_URL}/ingest/", files=files)
        if response.ok:
            st.success("Extraction and routing complete!")
            st.json(response.json())
        else:
            st.error(f"Error during processing: {response.text}")
    except Exception as e:
        st.error(f"Failed to process file: {str(e)}")

if st.button("View Memory Logs") and api_available:
    try:
        with st.spinner("Fetching logs..."):
            resp = requests.get(f"{API_URL}/memory/")
        if resp.ok:
            st.subheader("Memory Logs")
            try:
                # Try to parse the response as JSON
                if isinstance(resp.text, str):
                    try:
                        logs = json.loads(resp.text)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON response from server")
                        st.code(resp.text, language="json")
                        raise ValueError("Response is not valid JSON")
                else:
                    logs = resp.json()

                if not isinstance(logs, list):
                    st.error("Expected a list of logs but got a different format")
                    st.code(logs, language="json")
                    raise ValueError("Invalid log format")

                # Format the logs for better display
                st.write("### Processing History")
                for log in logs:
                    if not isinstance(log, dict):
                        continue
                        
                    st.write("---")
                    # Display timestamp if available
                    if 'timestamp' in log:
                        try:
                            timestamp = datetime.fromisoformat(log['timestamp'])
                            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                            st.write(f"**Time:** {formatted_time}")
                        except (ValueError, TypeError):
                            st.write(f"**Time:** {log['timestamp']} (raw)")
                    
                    # Display other fields with fallbacks
                    st.write(f"**Format:** {log.get('format', 'N/A')}")
                    st.write(f"**Intent:** {log.get('intent', 'N/A')}")
                    
                    # Display any additional fields
                    for key, value in log.items():
                        if key not in ['timestamp', 'format', 'intent']:
                            st.write(f"**{key}:** {value}")
                
            except ValueError as e:
                st.error(f"Error parsing logs: {str(e)}")
        else:
            st.error(f"Error fetching logs: {resp.text}")
            if resp.status_code == 500:
                st.info("Server error - please check the FastAPI server logs")
    except Exception as e:
        st.error(f"Failed to fetch logs: {str(e)}")