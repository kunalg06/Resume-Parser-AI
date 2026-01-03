import streamlit as st
import requests
import json
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Resume Parser AI", 
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume Parser AI")
st.markdown("**Production-ready resume parsing with AI**")

# Sidebar with API config
# st.sidebar.header("🔧 API Settings")
# api_url = st.sidebar.text_input(
#     "API URL", 
#     value="http://127.0.0.1:8000",
#     help="Local server for testing"
# )

#Update Frontend for Production(Railway Deployment)
api_url = st.sidebar.text_input(
    "API URL", 
    value=st.secrets.get("API_URL", "https://resume-parser-ai-xxx.railway.app"),  # ← YOUR RAILWAY URL
    help="Backend API (Railway)"
)

if api_url:
    st.sidebar.success(f"✅ Connected to {api_url}")

# Main content
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose PDF or DOCX file",
        type=["pdf", "docx"],
        help="Supports PDF and DOCX formats"
    )
    
    if uploaded_file:
        st.info(f"**File:** {uploaded_file.name}")
        st.info(f"**Size:** {uploaded_file.size / 1024:.1f} KB")

with col2:
    if uploaded_file:
        if st.button("🚀 Parse Resume", type="primary"):
            with st.spinner("AI parsing your resume..."):
                try:
                    # Send to your API
                    files = {"file": uploaded_file.getvalue()}
                    response = requests.post(
                        f"{api_url}/parse",
                        files=files,
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Success message
                        st.success("✅ Resume parsed successfully!")
                        
                        # Personal info
                        st.subheader("👤 Personal Information")
                        personal_col1, personal_col2 = st.columns(2)
                        with personal_col1:
                            st.metric("Name", data.get("name", "N/A"))
                            st.metric("Email", data.get("email", "N/A"))
                        with personal_col2:
                            st.metric("Phone", data.get("phone", "N/A"))
                            st.metric("Location", data.get("location", "N/A"))
                        
                        # Summary
                        if data.get("summary"):
                            st.subheader("📝 Professional Summary")
                            st.write(data["summary"])
                        
                        # Skills
                        if data.get("skills"):
                            st.subheader("🔧 Skills")
                            skills = data["skills"]
                            skill_cols = st.columns(3)
                            for i, skill in enumerate(skills[:9]):  # Show top 9
                                with skill_cols[i % 3]:
                                    st.caption(skill)
                            if len(skills) > 9:
                                st.caption(f"... and {len(skills)-9} more")
                        
                        # Experience
                        if data.get("experience"):
                            st.subheader("💼 Experience")
                            for exp in data["experience"]:
                                with st.expander(f"📈 {exp.get('title')} @ {exp.get('company')}"):
                                    if exp.get("duration"):
                                        st.caption(f"**Duration:** {exp['duration']}")
                                    if exp.get("description"):
                                        st.write(exp["description"])
                        
                        # Education
                        if data.get("education"):
                            st.subheader("🎓 Education")
                            for edu in data["education"]:
                                with st.expander(f"📚 {edu.get('degree')}"):
                                    st.caption(f"**{edu.get('institution', 'N/A')}**")
                                    if edu.get("year"):
                                        st.caption(f"**Year:** {edu['year']}")
                                    if edu.get("details"):
                                        st.write(edu["details"])
                        
                        # Download JSON
                        st.divider()
                        json_data = json.dumps(data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_data,
                            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_parsed.json",
                            mime="application/json",
                            type="primary"
                        )
                        
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        st.code(response.text)
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Try a smaller file.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    else:
        st.info("👆 Upload a resume PDF or DOCX to get started!")

# Footer
st.divider()
st.markdown("""
### 🛠️ Tech Stack
- **Backend:** FastAPI + Perplexity AI
- **Frontend:** Streamlit
- **PDF Parsing:** pdfplumber
- **Deployment:** Railway + Hugging Face Spaces

**Source Code:** [GitHub](https://github.com/kunalg06/Resume-Parser-AI)
""")