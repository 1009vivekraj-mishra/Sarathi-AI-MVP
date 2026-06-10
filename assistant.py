"""backend/assistant.py
Utility to retrieve context from the vector store and generate a formatted answer.
"""
from typing import Tuple, List, Dict

from .rag import search
from .llm import call_llm

def get_answer_and_sources(query: str, top_k: int = 4) -> Tuple[str, List[str]]:
    """Execute the full Sarathi pipeline.

    1. Retrieve the top‑k relevant document chunks.
    2. Pass those chunks plus the user query to the LLM.
    3. Return the LLM answer and a list of source identifiers.
    """
    # 1. RAG retrieval
    retrieved = search(query, top_k=top_k)
    # 2. Build LLM response
    answer = call_llm(retrieved, query)
    # 3. Extract source citations (filenames) for UI display
    sources = [item.get("source", "") for item in retrieved]
    return answer, sources
