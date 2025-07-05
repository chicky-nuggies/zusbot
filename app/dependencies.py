"""
Shared dependencies for the FastAPI application
"""
from app.features.sessions.session_manager import SessionManager
from app.features.chat.chat_service.agent_run import ChatAgent
from app.config import config

# Global instances
session_manager = SessionManager()
chat_service = ChatAgent(config.CHAT_MODEL_ID)

def get_session_manager() -> SessionManager:
    """Dependency to get the shared session manager instance"""
    return session_manager

def get_chat_service() -> ChatAgent:
    """Dependency to get the shared chat service instance"""
    return chat_service
