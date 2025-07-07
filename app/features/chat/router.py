from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.models.endpoint_models import ChatRequest, ChatResponse
from app.dependencies import get_session_manager, get_chat_service
from app.features.sessions.session_manager import SessionManager
from app.features.chat.chat_service.agent_run import ChatAgent
import json

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    session_manager: SessionManager = Depends(get_session_manager),
    chat_service: ChatAgent = Depends(get_chat_service)
):
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

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    session_manager: SessionManager = Depends(get_session_manager),
    chat_service: ChatAgent = Depends(get_chat_service)
):
    """
    Streaming chat endpoint that yields tool call information in real-time.
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
        
        async def generate():
            final_response = None
            updated_history = None
            
            # Yield session information
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
            
            # Stream chat response with tool call information
            async for chunk in chat_service.chat_stream(request.message, message_history):
                if chunk["type"] == "response":
                    final_response = chunk["response"]
                    updated_history = chunk["message_history"]
                
                yield f"data: {json.dumps(chunk)}\n\n"
            
            # Update session with new message history
            if updated_history:
                session_manager.update_session_history(session_id, updated_history)
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    
    except Exception as e:
        print(f"Error in chat stream endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I encountered an error while processing your request."
        )


