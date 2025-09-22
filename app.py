import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="AARVIK - AI Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .session-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .upload-section {
        background: #e8f5e8;
        border: 2px dashed #28a745;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .chat-container {
        background: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .answer-box {
        background: #f0f8ff;
        border-left: 4px solid #007bff;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .sidebar-content {
        padding: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/api"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# Functions
def create_session():
    try:
        with st.spinner("Creating new session..."):
            response = requests.post(f"{API_URL}/sessions")
            response.raise_for_status()
            session_id = response.json()["session_id"]
            st.session_state.session_id = session_id
            st.session_state.sessions.append(session_id)
            st.session_state.chat_history[session_id] = []
            st.session_state.uploaded_files[session_id] = []
            st.success(f"✅ Created session: {session_id[:8]}...")
            time.sleep(1)
            st.rerun()
    except requests.RequestException as e:
        st.error(f"❌ Error creating session: {str(e)}")

def delete_session(session_id):
    try:
        with st.spinner(f"Deleting session {session_id[:8]}..."):
            response = requests.delete(f"{API_URL}/sessions/{session_id}")
            response.raise_for_status()
            st.session_state.sessions.remove(session_id)
            if st.session_state.session_id == session_id:
                st.session_state.session_id = None
            if session_id in st.session_state.chat_history:
                del st.session_state.chat_history[session_id]
            if session_id in st.session_state.uploaded_files:
                del st.session_state.uploaded_files[session_id]
            st.success(f"✅ Deleted session: {session_id[:8]}...")
            time.sleep(1)
            st.rerun()
    except requests.RequestException as e:
        st.error(f"❌ Error deleting session: {str(e)}")

def upload_pdf(session_id, file):
    try:
        with st.spinner(f"Uploading {file.name}..."):
            files = {"file": (file.name, file, "application/pdf")}
            response = requests.post(f"{API_URL}/upload_pdf?session_id={session_id}", files=files)
            response.raise_for_status()
            
            # Track uploaded files
            if session_id not in st.session_state.uploaded_files:
                st.session_state.uploaded_files[session_id] = []
            st.session_state.uploaded_files[session_id].append({
                "name": file.name,
                "size": file.size,
                "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            st.success(f"✅ {response.json()['message']}")
            time.sleep(1)
            st.rerun()
    except requests.RequestException as e:
        st.error(f"❌ Error uploading PDF: {str(e)}")

def ask_question(session_id, question):
    try:
        with st.spinner("🤔 Thinking..."):
            response = requests.post(
                f"{API_URL}/ask_question",
                json={"session_id": session_id, "question": question}
            )
            response.raise_for_status()
            answer = response.json()["answer"]
            
            # Add to chat history
            if session_id not in st.session_state.chat_history:
                st.session_state.chat_history[session_id] = []
            
            st.session_state.chat_history[session_id].append({
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            return answer
    except requests.RequestException as e:
        st.error(f"❌ Error asking question: {str(e)}")
        return None

# Main App Layout
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AARVIK</h1>
        <p>AI-powered Answering with Retrieval, Vectorization, and Interactive Knowledgebase</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        st.header("📋 Session Management")
        
        # Create new session button
        if st.button("🆕 Create New Session", use_container_width=True, type="primary"):
            create_session()
        
        st.markdown("---")
        
        # Session selector
        if st.session_state.sessions:
            st.subheader("🔄 Active Sessions")
            
            selected_session = st.selectbox(
                "Choose a session:",
                options=st.session_state.sessions,
                format_func=lambda x: f"Session {x[:8]}...",
                key="session_select"
            )
            
            if selected_session:
                st.session_state.session_id = selected_session
                
                # Session info
                session_files = st.session_state.uploaded_files.get(selected_session, [])
                session_chats = st.session_state.chat_history.get(selected_session, [])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📄 Files", len(session_files))
                with col2:
                    st.metric("💬 Chats", len(session_chats))
                
                # Delete session
                if st.button("🗑️ Delete Session", use_container_width=True, type="secondary"):
                    delete_session(selected_session)
        else:
            st.info("No active sessions. Create one to get started!")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area
    if st.session_state.session_id:
        current_session = st.session_state.session_id
        
        # Two column layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📤 Document Upload")
            
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Drop your PDF here or click to browse",
                type="pdf",
                help="Upload PDF documents to analyze"
            )
            
            if uploaded_file:
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{uploaded_file.size / 1024:.2f} KB"
                }
                st.json(file_details)
                
                if st.button("📤 Upload PDF", use_container_width=True, type="primary"):
                    upload_pdf(current_session, uploaded_file)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show uploaded files
            uploaded_files = st.session_state.uploaded_files.get(current_session, [])
            if uploaded_files:
                st.subheader("📁 Uploaded Files")
                for file in uploaded_files:
                    with st.expander(f"📄 {file['name']}"):
                        st.write(f"**Size:** {file['size'] / 1024:.2f} KB")
                        st.write(f"**Uploaded:** {file['uploaded_at']}")
        
        with col2:
            st.subheader("💬 Chat with Your Documents")
            
            # Chat interface
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Question input
            question = st.text_input(
                "Ask a question about your documents:",
                placeholder="What would you like to know?",
                key="question_input"
            )
            
            col_ask, col_clear = st.columns([3, 1])
            with col_ask:
                ask_button = st.button("🚀 Ask Question", use_container_width=True, type="primary")
            with col_clear:
                if st.button("🧹 Clear Chat", use_container_width=True):
                    if current_session in st.session_state.chat_history:
                        st.session_state.chat_history[current_session] = []
                    st.rerun()
            
            if ask_button and question:
                answer = ask_question(current_session, question)
                if answer:
                    st.rerun()  # Refresh to show new chat
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display chat history
            chat_history = st.session_state.chat_history.get(current_session, [])
            if chat_history:
                st.subheader("📜 Chat History")
                
                # Reverse to show latest first
                for i, chat in enumerate(reversed(chat_history)):
                    with st.expander(f"Q: {chat['question'][:50]}..." if len(chat['question']) > 50 else f"Q: {chat['question']}", expanded=(i == 0)):
                        st.write(f"**🕒 {chat['timestamp']}**")
                        st.write(f"**❓ Question:** {chat['question']}")
                        st.markdown(f'<div class="answer-box"><strong>🤖 Answer:</strong><br>{chat["answer"]}</div>', unsafe_allow_html=True)
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Welcome to AARVIK!
        
        **Get started by creating a new session:**
        
        1. 🆕 Click "Create New Session" in the sidebar
        2. 📤 Upload your PDF documents  
        3. 💬 Ask questions about your documents
        4. 🤖 Get AI-powered answers with context
        
        ### Features:
        - 📄 **Multi-document support** - Upload multiple PDFs per session
        - 🧠 **Smart retrieval** - Vector-based document search
        - 💾 **Session management** - Organize your work in separate sessions
        - 📊 **Chat history** - Keep track of all your questions and answers
        - 🎨 **Modern interface** - Clean and intuitive design
        """)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>🚀 Fast Processing</h4>
                <p>Quick document analysis and question answering powered by advanced AI</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>🔒 Secure Sessions</h4>
                <p>Your documents and conversations are isolated in separate sessions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h4>📈 Smart Analytics</h4>
                <p>Track your uploaded files and chat history for better productivity</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()