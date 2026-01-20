"""LangGraph state schema for the multi-agent QA flow."""

from typing import TypedDict, List, Optional, Any


class QAState(TypedDict):
    """State schema for the conversational multi-agent QA flow.

    The state flows through agents and now retains conversation history.
    """

    question: str
    # Feature 5: Memory fields
    history: List[dict]  # List of {"question": "...", "answer": "..."}
    session_id: str | None
    
    context: str | None
    draft_answer: str | None
    answer: str | None

    # Feature 5 Extension: Conversation Summary
    conversation_summary: Optional[str]