from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from src.parser import ResumeParser
from src.config import settings
import traceback

app = FastAPI(
    title="Resume Parser API",
    description="AI-powered resume parsing with Perplexity LLM",
    version="2.0.0"
)

# CORS setup - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parser
try:
    parser = ResumeParser(api_key=settings.perplexity_api_key)
except Exception as e:
    print(f"Warning: Could not initialize parser: {e}")
    parser = None

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Resume Parser API v2.0",
        "docs": "/docs",
        "endpoints": ["/health", "/parse", "/batch-parse"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "api": "Perplexity"
    }

@app.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    Upload a resume (PDF or DOCX) and get structured data.
    
    Returns JSON with:
    - name, email, phone, location
    - summary, skills
    - experience (list of jobs)
    - education (list of degrees)
    - certifications
    """
    
    if not parser:
        raise HTTPException(
            status_code=500,
            detail="Parser not initialized. Check API_KEY in .env"
        )
    
    # Validate file type
    # Skip strict filename validation (Streamlit sends None)
    filename = file.filename or "uploaded_file.pdf"

    # Log for debugging
    print(f"📁 Processing: {filename} ({file.size} bytes)")

    # Size limit only
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large")

    # Optional: Warn on unknown extension
    if not filename.lower().endswith(('.pdf', '.docx', '.doc')):
        print(f"⚠️ Unknown extension: {filename}")
    
    tmp_path = None
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse the resume
        result = parser.parse(tmp_path)
        
        return JSONResponse(content=result, status_code=200)
    
    except Exception as e:
        return JSONResponse(
            content={
                "error": str(e),
                "type": type(e).__name__
            },
            status_code=500
        )
    
    finally:
        # Always cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

@app.post("/batch-parse")
async def batch_parse(files: list[UploadFile] = File(...)):
    """Parse multiple resumes at once"""
    
    if not parser:
        raise HTTPException(
            status_code=500,
            detail="Parser not initialized"
        )
    
    results = []
    
    for file in files:
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(file.filename)[1]
            ) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # Parse
            result = parser.parse(tmp_path)
            results.append({
                "filename": file.filename,
                "status": "success" if "error" not in result else "error",
                "data": result
            })
            
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "resumes": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
