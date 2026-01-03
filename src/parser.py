import pdfplumber
from docx import Document
import requests
import json
from typing import Dict, Optional
import os

class ResumeParser:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.perplexity_endpoint = "https://api.perplexity.ai/chat/completions"
    
    def extract_text(self, file_path: str) -> str:
        """Extract text - handle generic 'file' names"""
        filename = os.path.basename(file_path).lower()
        
        if filename.endswith('.pdf') or 'pdf' in file_path.lower():
            return self._extract_from_pdf(file_path)
        elif filename.endswith(('.docx', '.doc')):
            return self._extract_from_docx(file_path)
        else:
            # Default to PDF (most common)
            print(f"📄 Assuming PDF: {file_path}")
            return self._extract_from_pdf(file_path)
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Use pdfplumber to extract text"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract from DOCX"""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def parse_with_llm(self, resume_text: str) -> Dict:
        """Use Perplexity API to structure resume data"""
        
        if len(resume_text) > 5000:
            resume_text = resume_text[:5000]
        
        prompt = f"""Parse this resume. Return ONLY valid JSON. No markdown. No explanations.

    {{
    "name": null,
    "email": null,
    "phone": null,
    "location": null,
    "summary": null,
    "skills": [],
    "experience": [{{"title":null,"company":null,"duration":null,"description":null}}],
    "education": [{{"degree":null,"institution":null,"year":null,"details":null}}],
    "certifications": []
    }}

    Resume:
    {resume_text}"""

        try:
            response = requests.post(
                self.perplexity_endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,  # Even more deterministic
                    "max_tokens": 1500
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}", "details": response.text}
            
            result = response.json()
            
            # Extract content safely
            content = ""
            if 'choices' in result and result['choices']:
                choice = result['choices'][0]
                if isinstance(choice, dict) and 'message' in choice:
                    message = choice['message']
                    content = message.get('content', '') if isinstance(message, dict) else str(message)
            
            if not content:
                return {"error": "No content in response", "raw": result}
            
            # Robust JSON extraction
            content = content.strip()
            
            # Remove markdown code blocks
            while '```json' in content:
                start = content.find('```json')
                end = content.find('```', start + 7)
                if end != -1:
                    content = content[start+7:end].strip()
                else:
                    break
            
            while '```' in content:
                start = content.find('```')
                end = content.find('```', start + 3)
                if end != -1 and end > start + 3:
                    content = content[:start] + content[end+3:].strip()
                else:
                    break
            
            # Parse JSON
            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                # Last resort: return first 500 chars for debugging
                return {"error": "JSON Parse Failed", "debug_content": content[:500]}
                
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}
    def parse(self, file_path: str) -> Dict:
        """Full pipeline: extract text → parse with LLM"""
        try:
            text = self.extract_text(file_path)
            if not text or len(text.strip()) < 10:
                return {"error": "No text extracted from file"}
            return self.parse_with_llm(text)
        except Exception as e:
            return {"error": f"Pipeline failed: {str(e)}"}
