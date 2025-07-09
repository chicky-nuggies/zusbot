from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
import json

from app.models.endpoint_models import ChatRequest, ChatResponse, ChatStreamChunk, ProductSummaryResponse, OutletQueryResponse
from app.dependencies import get_session_manager, get_chat_service
from app.features.sessions.session_manager import SessionManager
from app.features.chat.chat_service.agent_run import ChatAgent

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
            print(f"[CHAT] Created new session: {session_id}")
        else:
            # Use existing session
            session_id = request.session_id
            session_manager.update_session_activity(session_id)
            message_history = session_manager.get_session_history(session_id)
            print(f"[CHAT] Using existing session: {session_id}, history length: {len(message_history) if message_history else 0}")
        
        # Get response from chat service
        response, updated_history, tool_metadata = await chat_service.chat(request.message, message_history)
        
        # Update session with new message history
        session_manager.update_session_history(session_id, updated_history)
        print(f"[CHAT] Updated session {session_id} with {len(updated_history)} messages")
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            status="success",
            tool_calls=tool_metadata
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I encountered an error while processing your request."
        )

@router.get("/products", response_model=ProductSummaryResponse)
async def get_products_summary(
    query: str = Query(..., description="User question about products"),
    session_manager: SessionManager = Depends(get_session_manager),
    chat_service: ChatAgent = Depends(get_chat_service)
):
    """
    Product summary endpoint that uses a dedicated product agent to search for and summarize
    relevant products based on user queries. The agent uses tools to retrieve products and
    generates an AI summary.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Clean up old sessions periodically
        session_manager.cleanup_old_sessions()
        
        # For products endpoint, we'll use a simple session management
        # You could extend this to support session_id as a query parameter if needed
        session_id = session_manager.create_session()
        
        # Use the dedicated product chat agent
        response, updated_history, tool_metadata = await chat_service.product_chat(query, message_history=None)
        
        # Update session with the conversation
        session_manager.update_session_history(session_id, updated_history)
        
        # Extract product information from tool calls for the response
        retrieved_products = []
        for tool_call in tool_metadata:
            if tool_call.get('tool_name') == 'get_similar_products' and isinstance(tool_call.get('result'), list):
                for product_id, chunk, similarity in tool_call.get('result', []):
                    product_info = {
                        "id": product_id,
                        "content": chunk,
                        "similarity_score": float(similarity)
                    }
                    retrieved_products.append(product_info)
        
        return ProductSummaryResponse(
            query=query,
            summary=response,
            retrieved_products=retrieved_products,
            session_id=session_id,
            status="success",
            tool_calls=tool_metadata
        )
    
    except Exception as e:
        print(f"Error in products endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sorry, I encountered an error while processing your request: {str(e)}"
        )


@router.get("/outlets", response_model=OutletQueryResponse)
async def get_outlets_query(
    query: str = Query(..., description="Natural language query about outlets"),
    session_manager: SessionManager = Depends(get_session_manager),
    chat_service: ChatAgent = Depends(get_chat_service)
):
    """
    Outlet query endpoint that uses a dedicated outlet agent to translate natural language
    queries to SQL, execute them against the outlets database, and return formatted results.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Clean up old sessions periodically
        session_manager.cleanup_old_sessions()
        
        # For outlets endpoint, create a new session
        session_id = session_manager.create_session()
        
        # Use the dedicated outlet chat agent
        response, updated_history, tool_metadata = await chat_service.outlet_chat(query, message_history=None)
        
        # Update session with the conversation
        session_manager.update_session_history(session_id, updated_history)
        
        return OutletQueryResponse(
            query=query,
            response=response,
            session_id=session_id,
            status="success",
            tool_calls=tool_metadata
        )
    
    except Exception as e:
        print(f"Error in outlets endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sorry, I encountered an error while processing your request: {str(e)}"
        )


@router.post("/chat-stream")
async def chat_stream(
    request: ChatRequest, 
    session_manager: SessionManager = Depends(get_session_manager),
    chat_service: ChatAgent = Depends(get_chat_service)
):
    """
    Streaming chat endpoint for interacting with the Zus Coffee assistant.
    Returns Server-Sent Events (SSE) stream of response chunks.
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
            print(f"[STREAM] Created new session: {session_id}")
        else:
            # Use existing session
            session_id = request.session_id
            session_manager.update_session_activity(session_id)
            message_history = session_manager.get_session_history(session_id)
            print(f"[STREAM] Using existing session: {session_id}, history length: {len(message_history) if message_history else 0}")
        
        async def generate_stream():
            updated_history = None
            try:
                # Get streaming response from chat service
                async for item in chat_service.chat_stream(request.message, message_history):
                    if 'chunk' in item:
                        # Stream text chunks
                        chunk_data = ChatStreamChunk(
                            chunk=item['chunk'],
                            session_id=session_id,
                            status="streaming"
                        )
                        yield f"data: {chunk_data.model_dump_json()}\n\n"
                    
                    elif 'response' in item:
                        # Final response with complete message
                        updated_history = item['message_history']
                        tool_calls = item.get('tool_calls', [])
                        
                        final_data = ChatStreamChunk(
                            response=item['response'],
                            session_id=session_id,
                            message_history=updated_history,
                            status="complete",
                            tool_calls=tool_calls
                        )
                        yield f"data: {final_data.model_dump_json()}\n\n"
                
                # Update session with new message history after streaming is complete
                if updated_history is not None:
                    session_manager.update_session_history(session_id, updated_history)
                    print(f"Updated session {session_id} with {len(updated_history)} messages")
                
                # Send end of stream marker
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                # Still update session history if we have it, even on error
                if updated_history is not None:
                    session_manager.update_session_history(session_id, updated_history)
                
                error_data = ChatStreamChunk(
                    chunk=f"Error: {str(e)}",
                    session_id=session_id,
                    status="error"
                )
                yield f"data: {error_data.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
    
    except Exception as e:
        print(f"Error in chat-stream endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I encountered an error while processing your request."
        )


