import streamlit as st
import requests
import json
from typing import Dict

st.set_page_config(page_title="Resume Parser", layout="wide")

st.title("📄 Resume Parser")
st.markdown("Upload your resume and extract structured data instantly")

# File uploader
uploaded_file = st.file_uploader(
    "Upload resume (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Uploaded File")
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        
        # Send to backend
        files = {"file": uploaded_file}
        response = requests.post(
            "http://localhost:8000/parse",  # Will be Railway URL in production
            files=files
        )
    
    with col2:
        st.subheader("Extracted Data")
        
        if response.status_code == 200:
            data = response.json()["data"]
            
            # Display structured data
            st.json(data)
            
            # Download button
            st.download_button(
                "📥 Download JSON",
                json.dumps(data, indent=2),
                "resume_data.json",
                "application/json"
            )
        else:
            st.error("Error parsing resume")

# Footer
st.divider()
st.markdown("""
**About:** This tool extracts structured data from resumes using NLP + spaCy.  
**GitHub:** [kunalg06/resume-parser-v2](https://github.com/kunalg06)  
**Tech:** FastAPI + Streamlit + Pydantic
""")
