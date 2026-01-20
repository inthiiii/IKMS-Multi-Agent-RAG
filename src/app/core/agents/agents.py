"""Agent implementations for the multi-agent RAG flow."""

from typing import List, Dict, Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate

from ..llm.factory import create_chat_model
from .prompts import (
    RETRIEVAL_SYSTEM_PROMPT,
    SUMMARIZATION_SYSTEM_PROMPT,
    VERIFICATION_SYSTEM_PROMPT,
)
from .state import QAState
from .tools import retrieval_tool


def _extract_last_ai_content(messages: List[object]) -> str:
    """Extract the content of the last AIMessage in a messages list."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return str(msg.content)
    return ""


def _format_history(history: List[Dict[str, Any]]) -> str:
    """Helper to format conversation history into a string for the LLM."""
    if not history:
        return "No previous conversation."
    
    formatted = []
    for turn in history:
        q = turn.get("question", "")
        a = turn.get("answer", "")
        if q and a:
            formatted.append(f"User: {q}\nAssistant: {a}")
    
    return "\n---\n".join(formatted)


# Define agents
retrieval_agent = create_agent(
    model=create_chat_model(),
    tools=[retrieval_tool],
    system_prompt=RETRIEVAL_SYSTEM_PROMPT,
)

summarization_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=SUMMARIZATION_SYSTEM_PROMPT,
)

verification_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=VERIFICATION_SYSTEM_PROMPT,
)


def retrieval_node(state: QAState) -> QAState:
    """Retrieval Agent node: gathers context considering history."""
    question = state["question"]
    history = state.get("history", [])
    
    # Format the input to include history
    history_str = _format_history(history)
    user_content = (
        f"Conversation History:\n{history_str}\n\n"
        f"Current Question: {question}"
    )

    result = retrieval_agent.invoke({"messages": [HumanMessage(content=user_content)]})

    messages = result.get("messages", [])
    context = ""

    # Prefer the last ToolMessage content
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            context = str(msg.content)
            break

    return {
        "context": context,
    }


def summarization_node(state: QAState) -> QAState:
    """Summarization Agent node: generates draft answer using context & history."""
    question = state["question"]
    context = state.get("context")
    history = state.get("history", [])

    history_str = _format_history(history)
    user_content = (
        f"Conversation History:\n{history_str}\n\n"
        f"Current Question: {question}\n\n"
        f"Context:\n{context}"
    )

    result = summarization_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    draft_answer = _extract_last_ai_content(messages)

    return {
        "draft_answer": draft_answer,
    }


def verification_node(state: QAState) -> QAState:
    """Verification Agent node: verifies answer."""
    question = state["question"]
    context = state.get("context", "")
    draft_answer = state.get("draft_answer", "")
    
    user_content = f"""Question: {question}

Context:
{context}

Draft Answer:
{draft_answer}

Please verify and correct the draft answer."""

    result = verification_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    answer = _extract_last_ai_content(messages)

    return {
        "answer": answer,
    }

# --- Feature 5 Extension: Memory Summarizer ---

def summarize_conversation(history: List[Dict[str, Any]]) -> str:
    """Helper to compress history using an LLM."""
    llm = create_chat_model()
    history_text = _format_history(history)
    
    # Simple direct invocation
    msg = HumanMessage(content=(
        f"Summarize the key points of this conversation in 3-4 sentences:\n\n{history_text}"
    ))
    response = llm.invoke([msg])
    return str(response.content)

def memory_summarizer_node(state: QAState) -> QAState:
    """Optional: Summarize conversation if it gets too long."""
    history = state.get("history", [])
    existing_summary = state.get("conversation_summary", "")

    # Only summarize if we have more than 2 turns (lowered for testing)
    if len(history) > 2:
        new_summary = summarize_conversation(history)
        return {"conversation_summary": new_summary}
    
    return {"conversation_summary": existing_summary}