"""LangGraph orchestration for the linear multi-agent QA flow."""

from functools import lru_cache
from typing import Any, Dict, List, Optional
import uuid

from langgraph.constants import END, START
from langgraph.graph import StateGraph

# FIX: Added memory_summarizer_node to imports
from .agents import (
    retrieval_node, 
    summarization_node, 
    verification_node, 
    memory_summarizer_node
)
from .state import QAState


def create_qa_graph() -> Any:
    """Create and compile the conversational multi-agent QA graph."""
    builder = StateGraph(QAState)

    # Add nodes for each agent
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("summarization", summarization_node)
    builder.add_node("verification", verification_node)
    builder.add_node("memory_summarizer", memory_summarizer_node) # Max Marks Feature

    # Define flow
    builder.add_edge(START, "retrieval")
    builder.add_edge("retrieval", "summarization")
    builder.add_edge("summarization", "verification")
    builder.add_edge("verification", "memory_summarizer")
    builder.add_edge("memory_summarizer", END)

    return builder.compile()


@lru_cache(maxsize=1)
def get_qa_graph() -> Any:
    """Get the compiled QA graph instance (singleton via LRU cache)."""
    return create_qa_graph()


def run_qa_flow(question: str) -> Dict[str, Any]:
    """Legacy entry point."""
    return run_conversational_qa_flow(question)


def run_conversational_qa_flow(
    question: str,
    history: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Run the complete multi-agent QA flow with memory."""
    graph = get_qa_graph()

    if not session_id:
        session_id = str(uuid.uuid4())

    initial_state: QAState = {
        "question": question,
        "history": history or [],
        "session_id": session_id,
        "context": None,
        "draft_answer": None,
        "answer": None,
        "conversation_summary": None, 
    }

    final_state = graph.invoke(initial_state)

    return final_state