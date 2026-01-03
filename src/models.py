from pydantic import BaseModel
from typing import List, Optional

class Resume(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    skills: List[str]
    experience: List[dict]
    education: List[dict]
    certifications: List[str]