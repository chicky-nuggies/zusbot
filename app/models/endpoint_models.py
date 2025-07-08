from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ToolMetadata(BaseModel):
    tool_name: str
    tool_kwargs: Dict[str, Any]
    tool_args: List[Any]
    generated_sql: Optional[str] = None
    result: Any

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"
    tool_calls: Optional[List[ToolMetadata]] = None

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
    tool_calls: Optional[List[ToolMetadata]] = None

class ChatStreamChunk(BaseModel):
    chunk: Optional[str] = None
    response: Optional[str] = None
    session_id: Optional[str] = None
    message_history: Optional[list] = None
    status: str = "success"
    tool_calls: Optional[List[ToolMetadata]] = None
