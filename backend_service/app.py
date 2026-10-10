import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from pydantic import BaseModel

from services.memory import MemoryService
from core.agent import AgentOrchestrator
from services.database import DatabaseService
from services.knowledge import KnowledgeBaseService

app = FastAPI(title="RideWise Assist API")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
db_service = DatabaseService()
kb_service = KnowledgeBaseService()
memory_service = MemoryService()
orchestrator = AgentOrchestrator(db_service, kb_service, memory_service)

# Ensure FAISS index is built on startup
@app.on_event("startup")
async def startup_event():
    print("Initializing FAISS Knowledge Base...")
    kb_service.initialize_index()

class ChatRequest(BaseModel):
    role: str # "Customer" or "Support Agent"
    message: str
    session_id: str
    mobile_number: Optional[str] = None
    customer_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        if request.role.lower() not in ["customer", "support agent"]:
            raise HTTPException(status_code=400, detail="Invalid role.")
            
        if request.role.lower() == "customer":
            if not request.customer_id or not request.mobile_number:
                raise HTTPException(status_code=401, detail="Both Customer ID and Mobile Number are required for login.")
            if not db_service.verify_credentials(request.customer_id, request.mobile_number):
                raise HTTPException(status_code=401, detail="Invalid Customer ID or Mobile Number. Authentication failed.")
            
        answer = orchestrator.chat(
            user_message=request.message,
            session_id=request.session_id,
            role=request.role,
            mobile_number=request.mobile_number,
            customer_id=request.customer_id
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LoginRequest(BaseModel):
    customer_id: str
    mobile_number: str

@app.post("/api/login")
async def login_endpoint(request: LoginRequest):
    if not db_service.verify_credentials(request.customer_id, request.mobile_number):
        raise HTTPException(status_code=401, detail="Invalid Customer ID or Mobile Number.")
    return {"status": "success"}

@app.get("/api/sessions")
async def get_sessions(customer_id: Optional[str] = None):
    try:
        return memory_service.get_sessions_for_user(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    try:
        return memory_service.get_all_messages(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
