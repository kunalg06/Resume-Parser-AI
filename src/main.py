from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

app = FastAPI(
    title="Resume Parser API",
    description="Extract structured data from resumes",
    version="1.0.0"
)

# Allow Streamlit frontend to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    """Parse resume and extract structured data"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            
            # Your parsing logic here
            result = parse_file(tmp.name)
            
            os.unlink(tmp.name)
            return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health():
    return {"status": "healthy"}
