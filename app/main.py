from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from .config import config
from .chat.chat_service import ChatService
from .features.sessions.session_manager import SessionManager

from app.models.endpoint_models import *

# Initialize FastAPI app
app = FastAPI(
    title="Zus Coffee Chatbot API",
    description="API for Zus Coffee customer service chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
chat_service = ChatService()
session_manager = SessionManager()

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Zus Coffee Chatbot API is running"
    )

@app.post("/session/new", response_model=NewSessionResponse)
async def create_new_session():
    """Create a new chat session"""
    session_id = session_manager.create_session()
    return NewSessionResponse(
        session_id=session_id,
        message="New chat session created"
    )

@app.get("/session/stats", response_model=SessionStatsResponse)
async def get_session_stats():
    """Get statistics about active sessions"""
    active_count = session_manager.get_session_count()
    return SessionStatsResponse(
        active_sessions=active_count,
        message=f"Currently {active_count} active sessions"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for interacting with the Zus Coffee assistant.
    Maintains conversation history within the session.
    If no session_id is provided, a new session will be created.
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Clean up old sessions periodically
        session_manager.cleanup_old_sessions()
        
        # Handle session management
        if not request.session_id or not session_manager.session_exists(request.session_id):
            # Create new session
            session_id = session_manager.create_session()
            message_history = None
        else:
            # Use existing session
            session_id = request.session_id
            session_manager.update_session_activity(session_id)
            message_history = session_manager.get_session_history(session_id)
        
        # Get response from chat service
        response, updated_history = await chat_service.chat(request.message, message_history)
        
        # Update session with new message history
        session_manager.update_session_history(session_id, updated_history)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            status="success"
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I encountered an error while processing your request."
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Zus Coffee Chatbot API",
        "endpoints": {
            "docs": "/docs",
            "health": "/health", 
            "new_session": "/session/new",
            "session_stats": "/session/stats",
            "chat": "/chat"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
