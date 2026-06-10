"""backend/llm.py
Wrapper for Grok (xAI) LLM calls.
xAI exposes an OpenAI-compatible REST API, so the openai SDK is used
with a custom base_url pointing at api.x.ai.
"""
import os
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv()
print("GROQ =", os.getenv("GROQ_API_KEY"))

from openai import OpenAI
import os

_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
print("USING GROQ:", os.getenv("GROQ_API_KEY")[:10] if os.getenv("GROQ_API_KEY") else "NO KEY")
print("BASE URL: https://api.groq.com/openai/v1")
_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are Sarathi, a workforce intelligence assistant for industrial environments. "
    "Provide concise, accurate answers grounded strictly in the provided context. "
    "Cite the source document at the end of your answer. "
    "If relevant, add one short practical learning tip."
)


def call_llm(context_chunks: List[Dict[str, str]], user_query: str) -> str:
    """Send retrieved context + user query to Grok and return the answer.

    Args:
        context_chunks: List of dicts with ``content`` and ``source``.
        user_query: The employee's question.
    Returns:
        Formatted answer string.
    """
    context_text = "\n\n".join(
        [f"Source: {c['source']}\n{c['content']}" for c in context_chunks]
    )
    user_prompt = (
        f"Context snippets (for grounding):\n{context_text}\n\n"
        f"Question: {user_query}\n\n"
        "Provide a concise answer, cite the source(s) used, and optionally add a short learning tip."
    )
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
