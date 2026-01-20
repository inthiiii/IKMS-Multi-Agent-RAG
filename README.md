# IKMS Multi-Agent RAG: Conversational Memory Extension

![Status](https://img.shields.io/badge/Status-Completed-success)
![Feature](https://img.shields.io/badge/Feature-Conversational_Memory-blue)
![Stack](https://img.shields.io/badge/Tech-LangGraph_|_Pinecone_|_FastAPI-orange)

## 📌 Project Overview
This project extends a standard Retrieval-Augmented Generation (RAG) system into a **Context-Aware Conversational Assistant**. 

Implemented as **Feature 5** of the IKMS Multi-Agent RAG Assignment, this system solves the "Statelessness" problem. Instead of treating every question in isolation, this application maintains conversation history, resolves pronouns (e.g., "it", "that"), and allows for deep, multi-turn research workflows.

## 🚀 Key Features Implemented

### 🧠 Feature 5: Conversational Multi-Turn QA
- **Context Retention:** The system remembers previous Q&A pairs.
- **Reference Resolution:** Successfully handles follow-up questions like *"What are its advantages?"* by looking back at previous turns to understand what *"it"* refers to.
- **LangGraph State Management:** Updated `QAState` to include `history` and `session_id`.
- **History-Aware Agents:** - **Retrieval Agent:** Rewrites queries based on conversation history.
    - **Summarization Agent:** Synthesizes answers using both new context and past interactions.

### 💻 User Interface (Streamlit)
- **Session Management:** Create new chat sessions or continue existing ones.
- **Visual Feedback:** "Thinking..." indicators during agent processing.
- **Evidence Inspector:** Expandable "View Retrieved Context" section for every answer to verify sources.

## 🛠️ Tech Stack

- **Orchestration:** LangChain v0.3, LangGraph
- **LLM:** OpenAI GPT-3.5 Turbo
- **Vector Database:** Pinecone (Serverless)
- **Embedding Model:** OpenAI `text-embedding-3-small` (Optimized for cost/performance)
- **Document Loader:** PyMuPDF (Handles complex PDF layouts)
- **Backend:** FastAPI
- **Frontend:** Streamlit

## 📂 Project Structure

```bash
src/
├── app/
│   ├── api.py              # FastAPI endpoints with Session Management
│   ├── ui.py               # Streamlit Chat Interface
│   ├── models.py           # Pydantic models for API requests
│   ├── services/
│   │   ├── indexing_service.py  # PDF Ingestion logic
│   ├── core/
│   │   ├── agents/
│   │   │   ├── graph.py    # LangGraph definition (Nodes & Edges)
│   │   │   ├── agents.py   # Agent logic (Retrieval, Summary, Verification)
│   │   │   ├── state.py    # Shared State Schema with History
│   │   │   ├── prompts.py  # History-aware system prompts
│   │   ├── retrieval/
│   │   │   ├── vector_store.py # Pinecone & Embedding setup

## 📂 Setup and Installation
# Create Virtual Environment
git clone [https://github.com/your-username/IKMS-Multi-Agent-RAG.git](https://github.com/your-username/IKMS-Multi-Agent-RAG.git)
cd IKMS-Multi-Agent-RAG

# Install Dependencies
pip install -r requirements.txt
    # OR
pip install fastapi uvicorn streamlit langchain langchain-openai langchain-community langgraph pinecone-client langchain-pinecone python-dotenv langchain_pymupdf4llm python-multipart

# Create  a .env file
OPENAI_API_KEY="..."
PINECONE_API_KEY="..."
PINECONE_ENV="us-east-1"
PINECONE_INDEX_NAME="knowledge-index"

## How to Run

# Frontend 
streamlit run src/app/ui.py

# Backend
python -m uvicorn src.app.api:app --reload