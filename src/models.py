from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    title: str
    company: str
    duration: Optional[str] = None
    description: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None
    details: Optional[str] = None

class ResumeData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    certifications: List[str] = []
