import uuid
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
from pydantic import BaseModel
from .sentiment_utils import analyze_sentiment
from .models import CandidateInfo, TechQuestionsRequest, TechQuestionsResponse, CandidateSessionId
from .llm_client import generate_technical_questions, chat_with_llm
from .qdrant_client import create_collection, store_candidate
from .session_utils import delete_session
from .pdf_parser import extract_text_from_pdf, parse_resume_text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    user_message: str
    conversation_history: list  # List of past messages (user/assistant)

class ChatResponse(BaseModel):
    reply: str

@app.on_event("startup")
async def startup_event():
    create_collection()

@app.get("/")
def root():
    return {"status": "ok", "service": "talentscout-backend"}


@app.get("/greet")
def greet():
    return {
        "message": "Hello! I'm TalentScout's AI Hiring Assistant. "
                   "I will guide you through the initial screening process."
    }

@app.post("/candidate-info")
def save_candidate(candidate: CandidateInfo):
    try:
        session_id = str(uuid.uuid4())
        candidate_dict = candidate.dict()
        candidate_dict["session_id"] = session_id
        store_candidate(candidate_dict)
        return {
            "status": "success",
            "message": "Candidate info stored.",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tech-questions", response_model=TechQuestionsResponse)
def get_technical_questions(req: TechQuestionsRequest):
    questions = generate_technical_questions(req.tech_stack)
    return TechQuestionsResponse(questions=questions)

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    try:
        # Create a temporary file that won't be auto-deleted
        import tempfile
        import os
        
        # Create temp file with proper suffix
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        
        try:
            # Write the uploaded file content to temp file
            contents = await file.read()
            with os.fdopen(temp_fd, 'wb') as tmp_file:
                tmp_file.write(contents)
            
            # Now extract text from the saved temp file
            text = extract_text_from_pdf(temp_path)
            parsed_data = parse_resume_text(text)
            
            return {"status": "success", "parsed_data": parsed_data}
            
        finally:
            # Clean up: remove the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {e}")

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        sentiment = analyze_sentiment(req.user_message)

        # Build properly sanitized messages array
        messages = [{"role": "system", "content": "You are a professional interviewer. Ask candidate questions based on context. Be polite and adaptive."}]
        
        # Safely process conversation history
        for msg in req.conversation_history:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
                if role in ("user", "assistant", "system") and isinstance(content, str) and content.strip():
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": req.user_message})

        reply_text = chat_with_llm(messages)
        return ChatResponse(reply=reply_text, sentiment=sentiment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-session")
def clear_session(session: CandidateSessionId = Body(...)):
    if delete_session(session.session_id):
        return {"status": "success", "message": "Session data cleared."}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear session data.")
