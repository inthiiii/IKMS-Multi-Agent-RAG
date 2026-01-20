from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QuestionRequest(BaseModel):
    """Legacy request body for single-shot QA."""
    question: str

class QAResponse(BaseModel):
    """Legacy response body."""
    answer: str
    context: str

# --- Feature 5: Conversational Models ---

class ConversationalQARequest(BaseModel):
    """Request for conversational QA.
    
    Includes an optional session_id. If provided, the system continues
    that conversation. If missing, a new session is started.
    """
    question: str
    session_id: Optional[str] = None

class ConversationalQAResponse(BaseModel):
    """Response for conversational QA.
    
    Returns the answer and the session_id so the client can 
    continue the chat in the next turn.
    """
    answer: str
    session_id: str
    context: str
    conversation_summary: Optional[str] = None

class ConversationHistory(BaseModel):
    """Model for retrieving full history."""
    session_id: str
    history: List[Dict[str, Any]]