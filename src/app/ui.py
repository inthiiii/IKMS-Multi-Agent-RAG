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
        # Clear summary on new chat
        if "latest_summary" in st.session_state:
            del st.session_state.latest_summary
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
    
    # Check if we have a summary stored in session state
    if "latest_summary" in st.session_state and st.session_state.latest_summary:
        st.success("Summary Generated:")
        st.markdown(st.session_state.latest_summary)
    else:
        st.info("Chat for at least 3 turns to generate a summary.")

# --- Chat Interface ---

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
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
                summary = data.get("conversation_summary", "")

                # Update UI with final answer
                message_placeholder.markdown(answer)
                
                # Show context
                if context:
                    with st.expander("📚 View Retrieved Context (Evidence)"):
                        st.markdown(context)
                
                # Save message BEFORE checking for summary/rerun
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "context": context
                })

                # Handle Summary Update (Green Box)
                if summary:
                    st.session_state.latest_summary = summary
                    st.rerun() # Now it is safe to rerun because message is saved
                    
            else:
                message_placeholder.error(f"API Error: {response.text}")
        except Exception as e:
            message_placeholder.error(f"Connection error. Is the backend running? {e}")