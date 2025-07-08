from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timedelta


class SessionManager:
    """Manages chat sessions with in-memory storage"""
    
    def __init__(self, session_timeout_hours: int = 24):
        # In-memory session storage (resets when server restarts)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Session cleanup settings
        self.session_timeout_hours = session_timeout_hours
    
    def create_session(self) -> str:
        """Create a new chat session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'message_history': []
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update the last activity time for a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = datetime.now()
            return True
        return False
    
    def update_session_history(self, session_id: str, message_history: list) -> bool:
        """Update the message history for a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['message_history'] = message_history
            return True
        return False
    
    def get_session_history(self, session_id: str) -> Optional[list]:
        """Get the message history for a session"""
        session = self.get_session(session_id)
        if session:
            return session['message_history']
        return None
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        return session_id in self.sessions
    
    def cleanup_old_sessions(self) -> int:
        """Remove sessions older than timeout period. Returns number of cleaned sessions."""
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        expired_sessions = [
            session_id for session_id, session_data in self.sessions.items()
            if session_data['last_activity'] < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            print(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """Get the total number of active sessions"""
        return len(self.sessions)
    
    def clear_all_sessions(self):
        """Clear all sessions (useful for testing or cleanup)"""
        self.sessions.clear()
