from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader 
from ..core.retrieval.vector_store import index_documents

def index_pdf_file(file_path: Path) -> int:
    """Load a PDF and index its pages using PyMuPDF."""
    
    # 1. Load the PDF using PyMuPDF (fitz)
    loader = PyMuPDFLoader(str(file_path))
    
    # 2. Split into pages
    docs = loader.load()
    
    # 3. Index them using our core vector store logic
    return index_documents(docs)