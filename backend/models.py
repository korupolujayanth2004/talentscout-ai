from pydantic import BaseModel, EmailStr
from typing import List, Optional

class CandidateInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    years_experience: int
    desired_position: str
    current_location: str
    tech_stack: List[str]
    education: Optional[str] = None
    current_role: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

class TechQuestionsRequest(BaseModel):
    tech_stack: List[str]

class TechQuestionsResponse(BaseModel):
    questions: List[str]

class CandidateSessionId(BaseModel):
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    sentiment: str  
