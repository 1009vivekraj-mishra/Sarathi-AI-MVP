"""backend/rag.py
RAG pipeline handling document loading, splitting, embedding, and vector store search.
"""
import os
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Local embedding model — no external API key required
HF_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
DOCS_DIR = os.path.join(DATA_DIR, "documents")
EXPERT_DIR = os.path.join(DATA_DIR, "expert")
VECTOR_DIR = os.path.abspath(os.path.join(DATA_DIR, "vectors"))

# Ensure directories exist
for d in [DOCS_DIR, EXPERT_DIR, VECTOR_DIR]:
    os.makedirs(d, exist_ok=True)


def get_embeddings():
    """Always use local sentence-transformers — no API key required."""
    return HuggingFaceEmbeddings(model_name=HF_EMBEDDING_MODEL)


embedding = get_embeddings()


def _load_documents() -> List:
    """Load all PDFs and TXT files from documents and expert directories."""
    docs = []
    for root_dir in [DOCS_DIR, EXPERT_DIR]:
        for filename in os.listdir(root_dir):
            path = os.path.join(root_dir, filename)
            if filename.lower().endswith(".pdf"):
                loader = PyPDFLoader(path)
            elif filename.lower().endswith(".txt"):
                loader = TextLoader(path, encoding="utf-8")
            else:
                continue
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = path
            docs.extend(loaded)
    return docs


def _get_vector_store():
    """Create or load the FAISS vector store from a persisted local index."""
    index_file = os.path.join(VECTOR_DIR, "index.faiss")
    if os.path.isfile(index_file):
        # allow_dangerous_deserialization required by current LangChain FAISS
        return FAISS.load_local(
            VECTOR_DIR, embedding, allow_dangerous_deserialization=True
        )

    # Build a new index from documents
    docs = _load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    if not chunks:
        # Return an empty in-memory store when no documents are present yet
        vs = FAISS.from_texts(["placeholder"], embedding)
        vs.save_local(VECTOR_DIR)
        return vs

    vs = FAISS.from_documents(chunks, embedding)
    vs.save_local(VECTOR_DIR)
    return vs


# Lazy-loaded global vector store
_vector_store = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = _get_vector_store()
    return _vector_store


def search(query: str, top_k: int = 4) -> List[Dict]:
    """Search the vector store for relevant chunks.

    Returns a list of dicts with ``content`` and ``source`` keys.
    """
    vs = get_vector_store()
    results = vs.similarity_search(query, k=top_k)
    return [
        {"content": doc.page_content, "source": doc.metadata.get("source", "unknown")}
        for doc in results
    ]
