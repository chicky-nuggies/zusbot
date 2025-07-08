from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

class NewSessionResponse(BaseModel):
    session_id: str
    message: str

class SessionStatsResponse(BaseModel):
    active_sessions: int
    message: str

class HealthResponse(BaseModel):
    status: str
    message: str

class ChatStreamResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

class ChatStreamChunk(BaseModel):
    chunk: Optional[str] = None
    response: Optional[str] = None
    session_id: Optional[str] = None
    message_history: Optional[list] = None
    status: str = "success"
