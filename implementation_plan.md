# Sarathi AI – Workforce Intelligence Assistant

## Goal Description

Build a production‑quality MVP web application that acts as a context‑aware workforce intelligence assistant for industrial environments. It must allow employees to query SOPs, machine manuals, and expert knowledge, retrieve grounded answers via a RAG pipeline, track skill exposure, and suggest concise learning items. The UI should be a single‑screen, dark‑theme, minimal interface with one primary input box and at most a few secondary actions.

## User Review Required

> [!IMPORTANT]
> The implementation includes several components that require user decisions before proceeding:
> - **Vector store choice**: FAISS (local) vs. ChromaDB (local). Both satisfy requirements; choose based on preference.
> - **LLM provider**: OpenAI API key (or compatible model) is needed for generation. Ensure you have an API key and acceptable usage limits.
> - **Deployment target**: For local testing, Streamlit run is sufficient. For production, consider Dockerizing the app.

## Open Questions

> [!WARNING]
> - Do you have existing SOP / expert documents ready for initial upload, or should we include sample PDFs?
> - Preferred storage for user profiles: SQLite file vs. JSON file?
> - Do you want authentication (e.g., simple username entry) or open access?

## Proposed Changes

---
### Project Structure

#### [NEW] [project_root](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI)
- `frontend/`
  - `app.py` – Streamlit entry point.
  - `styles.css` – Dark theme CSS.
- `backend/`
  - `rag.py` – Document loading, splitting, embedding, vector store.
  - `llm.py` – Wrapper for OpenAI / compatible LLM.
  - `skill_tracker.py` – SQLite DB and update logic.
  - `suggestion.py` – Learning suggestion engine.
  - `api.py` – FastAPI layer (optional, but kept minimal for future scaling).
- `data/`
  - `documents/` – Uploaded PDFs / txt.
  - `expert/` – Expert notes uploads.
  - `vectors/` – FAISS / Chroma index files.
  - `users.db` – SQLite DB for skill tracking.
- `requirements.txt`
- `README.md`

---
### Core Modules Implementation

#### [NEW] [backend/rag.py](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI/backend/rag.py)
- Functions to load PDFs/text via `langchain.document_loaders`.
- Use `RecursiveCharacterTextSplitter` with chunk size ~500 tokens.
- Generate embeddings via `OpenAIEmbeddings` (or `HuggingFaceEmbeddings`).
- Store vectors in FAISS (`FAISS.from_documents`) or ChromaDB based on chosen option.
- `search(query, top_k=4)` returns relevant chunks with source metadata.

#### [NEW] [backend/llm.py](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI/backend/llm.py)
- Wrapper `call_llm(prompt)` that sends system prompt describing response style (concise, includes source, optional tip).
- Handles API key configuration via environment variable `OPENAI_API_KEY`.

#### [NEW] [backend/skill_tracker.py](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI/backend/skill_tracker.py)
- SQLite schema: `users(id INTEGER PRIMARY KEY, name TEXT, skill TEXT, exposure INTEGER)`.
- Functions: `get_or_create_user(name)`, `update_skill(user_id, skill_category)`, `get_skill_profile(user_id)`.
- Simple skill categorisation based on keyword matching of retrieved chunks.

#### [NEW] [backend/suggestion.py](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI/backend/suggestion.py)
- After generating answer, call `suggest_learning(skill_category)` returning:
  1. One SOP snippet title (from source metadata) or
  2. One short tip (pre‑defined dictionary) or
  3. Next skill recommendation.
- Limit to max two items.

#### [NEW] [frontend/app.py](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI/frontend/app.py)
- Streamlit UI with dark theme CSS.
- Single text input box labeled “Ask Sarathi about your work or SOP…”.
- Sidebar or collapsible area for two secondary actions:
  - “Upload Document” (PDF/TXT) – stores in `data/documents`.
  - “Upload Expert Note” – stores in `data/expert` with tag selection.
- On submit:
  1. Call `rag.search`.
  2. Build prompt with retrieved context and send to LLM.
  3. Parse LLM response, display answer, source citations, optional tip.
  4. Update skill tracker.
  5. Show learning suggestions.

#### [NEW] [requirements.txt](file:///C:/Users/Vivek%20Raj/.gemini/antigravity/brain/2011541a-1893-44b0-b7ed-876694bbd320/SarathiAI/requirements.txt)
```
streamlit
openai
langchain
faiss-cpu   # or chromadb
pypdf
python-dotenv
```

---
### Verification Plan

**Automated Tests**
- Unit tests for `rag.search` returning expected number of chunks.
- Mock LLM call to verify prompt construction and response parsing.
- SQLite operations unit tests for skill tracking.

**Manual Verification**
- Run `streamlit run frontend/app.py`.
- Upload a sample SOP PDF, ask a query, verify answer is grounded and sources shown.
- Submit several queries of differing skill categories, check skill exposure counter increments in `users.db`.
- Verify learning suggestions appear (max two items).
- Test expert note upload and ensure it is searchable.

---
### Timeline (optional)
- Day 1: Scaffold repo, set up Streamlit UI, CSS styling.
- Day 2: Implement RAG pipeline, document upload flows.
- Day 3: Add expert note handling, skill tracker, suggestion engine.
- Day 4: Integrate all pieces, polish UI, write README.
- Day 5: Testing, bug fixes, final verification.

---
**End of Plan**

Please review the above details, answer the open questions, and approve to proceed with implementation.
