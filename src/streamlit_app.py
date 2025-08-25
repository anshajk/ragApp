import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
import os

# Configure page
st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://rag-app:8000")

# Helper functions
def get_api_health() -> Dict[str, Any]:
    """Check API health status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def upload_document(file) -> Optional[Dict[str, Any]]:
    """Upload a document to the API"""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def query_documents(query: str, max_results: int = 5, include_sources: bool = True) -> Optional[Dict[str, Any]]:
    """Query documents via the API"""
    try:
        payload = {
            "query": query,
            "max_results": max_results,
            "include_sources": include_sources
        }
        response = requests.post(
            f"{API_BASE_URL}/query", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return None

def get_document_stats() -> Optional[Dict[str, Any]]:
    """Get document statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def clear_all_documents() -> bool:
    """Clear all documents"""
    try:
        response = requests.delete(f"{API_BASE_URL}/documents", timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error clearing documents: {str(e)}")
        return False

# Main app
def main():
    st.title("📚 RAG Document Assistant")
    st.markdown("Upload documents and ask questions to get AI-powered answers with source citations.")
    
    # Sidebar with API status and controls
    with st.sidebar:
        st.header("🔧 System Status")
        
        # API Health Check
        health_status = get_api_health()
        if health_status.get("status") == "healthy":
            st.success("✅ API is healthy")
        else:
            st.error(f"❌ API issue: {health_status.get('error', 'Unknown error')}")
        
        st.divider()
        
        # Document Statistics
        st.header("📊 Document Stats")
        stats = get_document_stats()
        if stats:
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.info(f"Collection: {stats.get('collection_name', 'N/A')}")
            
            with st.expander("Supported Formats"):
                formats = stats.get("supported_formats", [])
                for fmt in formats:
                    st.write(f"• {fmt}")
        else:
            st.warning("Could not fetch document statistics")
        
        st.divider()
        
        # Clear Documents
        st.header("🗑️ Clear Data")
        if st.button("Clear All Documents", type="secondary"):
            if st.session_state.get("confirm_clear", False):
                if clear_all_documents():
                    st.success("All documents cleared!")
                    st.rerun()
                else:
                    st.error("Failed to clear documents")
                st.session_state["confirm_clear"] = False
            else:
                st.session_state["confirm_clear"] = True
                st.warning("Click again to confirm deletion")
    
    # Main content area
    tab1, tab2 = st.tabs(["📤 Upload Documents", "💬 Query Documents"])
    
    with tab1:
        st.header("Upload Documents")
        st.markdown("Upload PDF, DOCX, or TXT files to add them to the knowledge base.")
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_files:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📁 Upload All Files", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    total_files = len(uploaded_files)
                    
                    for i, file in enumerate(uploaded_files):
                        status_text.text(f"Uploading {file.name}...")
                        progress_bar.progress((i) / total_files)
                        
                        result = upload_document(file)
                        if result:
                            success_count += 1
                            st.success(f"✅ {file.name} uploaded successfully")
                        else:
                            st.error(f"❌ Failed to upload {file.name}")
                    
                    progress_bar.progress(1.0)
                    status_text.text(f"Upload complete: {success_count}/{total_files} files uploaded")
                    
                    if success_count > 0:
                        time.sleep(1)
                        st.rerun()
            
            with col2:
                st.info(f"📋 {len(uploaded_files)} file(s) selected")
                for file in uploaded_files:
                    st.write(f"• {file.name} ({file.size:,} bytes)")
    
    with tab2:
        st.header("Query Documents")
        st.markdown("Ask questions about your uploaded documents and get AI-powered answers.")
        
        # Query form
        with st.form("query_form"):
            query = st.text_area(
                "Enter your question:",
                placeholder="What are the main topics covered in the documents?",
                height=100
            )
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                submitted = st.form_submit_button("🔍 Ask Question", type="primary")
            with col2:
                max_results = st.number_input("Max Results", min_value=1, max_value=20, value=5)
            with col3:
                include_sources = st.checkbox("Include Sources", value=True)
        
        # Process query
        if submitted and query.strip():
            with st.spinner("🤔 Searching and generating answer..."):
                start_time = time.time()
                result = query_documents(query, max_results, include_sources)
                
                if result:
                    response_time = time.time() - start_time
                    
                    # Display answer
                    st.markdown("### 🎯 Answer")
                    st.markdown(result["answer"])
                    
                    # Display metadata
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.metric("Response Time", f"{response_time:.2f}s")
                    with col2:
                        st.metric("Sources Found", len(result.get("sources", [])))
                    
                    # Display sources if available and requested
                    if include_sources and result.get("sources"):
                        st.markdown("### 📚 Sources")
                        
                        for i, source in enumerate(result["sources"], 1):
                            with st.expander(f"Source {i} (Similarity: {source['similarity_score']:.3f})"):
                                st.markdown("**Content:**")
                                st.write(source["content"])
                                
                                if source.get("metadata"):
                                    st.markdown("**Metadata:**")
                                    metadata = source["metadata"]
                                    if metadata.get("filename"):
                                        st.write(f"📄 **File:** {metadata['filename']}")
                                    if metadata.get("chunk_index") is not None:
                                        st.write(f"🔢 **Chunk:** {metadata['chunk_index']}")
                                    if metadata.get("page_number"):
                                        st.write(f"📖 **Page:** {metadata['page_number']}")
                
                else:
                    st.error("Failed to get response from the API")
        
        elif submitted:
            st.warning("Please enter a question to search for.")
        
        # Query history (stored in session state)
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
        
        if st.session_state.query_history:
            st.markdown("### 📜 Recent Queries")
            with st.expander("View Query History"):
                for i, hist_query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                    st.write(f"{i}. {hist_query}")
        
        # Add current query to history if submitted
        if submitted and query.strip():
            if query not in st.session_state.query_history:
                st.session_state.query_history.append(query)
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>🤖 Powered by OpenAI GPT & Embeddings | 🗃️ ChromaDB Vector Database | ⚡ FastAPI Backend</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()