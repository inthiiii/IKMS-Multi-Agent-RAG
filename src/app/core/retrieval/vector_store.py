# src/app/core/retrieval/vector_store.py

import os
from pathlib import Path
from typing import List, Any

# Switched to PyMuPDFLoader for better reliability
from langchain_community.document_loaders import PyMuPDFLoader 
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

def get_vector_store() -> PineconeVectorStore:
    """Get the Pinecone vector store instance."""
    
    # Use the cheaper embedding model
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    index_name = os.getenv("PINECONE_INDEX_NAME", "knowledge-index")

    # Connect to existing index
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )
    
    return vector_store

def get_retriever(k: int = 5) -> Any:
    """Get a retriever interface from the vector store."""
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

def retrieve(query: str, k: int = 8) -> List[Document]:
    """Retrieve relevant documents for a query string.
    
    Args:
        query: The search text.
        k: The number of documents to return (default 4).
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    return retriever.invoke(query)

def index_documents(documents: List[Document]) -> int:
    """Index a list of documents into Pinecone."""
    vector_store = get_vector_store()
    ids = vector_store.add_documents(documents)
    return len(ids)

def index_pdf_file(file_path: Path) -> int:
    """Load a PDF and index its pages."""
    
    # 1. Use PyMuPDFLoader (As a solution against 'bbox' errors)
    loader = PyMuPDFLoader(str(file_path))
    
    # 2. Load pages
    docs = loader.load()
    
    # 3. Index them
    return index_documents(docs)