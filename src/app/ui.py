# src/app/ui.py
import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="IKMS RAG Assistant", page_icon="🤖", layout="wide")

st.title("🤖 IKMS Multi-Agent Conversational RAG")
st.markdown("*Feature 5: Conversational Multi-Turn QA with Memory*")

# --- Session Management ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("Session Management")
    st.info(f"Session ID:\n{st.session_state.session_id}")
    
    if st.button("Start New Conversation", type="primary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("Knowledge Base")
    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])
    
    if uploaded_file and st.button("Index Document"):
        with st.spinner("Indexing PDF into Pinecone..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            try:
                response = requests.post(f"{API_URL}/index-pdf", files=files)
                if response.status_code == 200:
                    st.success("✅ Document indexed successfully!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

    st.divider()
    st.subheader("🧠 Memory Inspector")
    
    # Fetch summary (You might need a new API endpoint for this, 
    # but for now let's just assume the API returns it or we fetch history)
    # To keep it simple, we will just show a placeholder or fetch if you add the endpoint.
    
    # Ideally, add this endpoint to api.py:
    # @app.get("/qa/session/{session_id}/summary")
    
    st.info("Conversation Summary will appear here after 5 turns.")

# --- Chat Interface ---

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there is context saved with the message, show it
        if "context" in message and message["context"]:
            with st.expander("📚 View Retrieved Context (Evidence)"):
                st.markdown(message["context"])

# User Input
if prompt := st.chat_input("Ask a question about your PDF..."):
    # 1. Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 *Thinking and searching...*")
        
        payload = {
            "question": prompt,
            "session_id": st.session_state.session_id
        }
        
        try:
            response = requests.post(f"{API_URL}/qa/conversation", json=payload)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer received.")
                context = data.get("context", "")
                
                # Update UI with final answer
                message_placeholder.markdown(answer)
                
                # Show context in an expander (Requirements: "Visual feedback")
                if context:
                    with st.expander("📚 View Retrieved Context (Evidence)"):
                        st.markdown(context)
                
                # Save to local state so it persists on refresh
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "context": context
                })
            else:
                message_placeholder.error(f"API Error: {response.text}")
        except Exception as e:
            message_placeholder.error(f"Connection error. Is the backend running? {e}")