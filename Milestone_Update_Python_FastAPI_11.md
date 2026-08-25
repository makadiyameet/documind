# Milestone 1: Python + FastAPI Foundations

**Status:** Done
**Started:**
**Completed:**

---

## Tasks

- [x] Python syntax refresh: functions, classes, virtual envs, pip
- [x] FastAPI basics: routes, request/response models (Pydantic), async endpoints
- [x] Build a throwaway "hello world" API with 2-3 endpoints, test with Postman or curl
- [x] Call the Anthropic/OpenAI API from Python — basic "send a prompt, get a response" call

---

## Done When

You can run a simple FastAPI server locally that takes a question, sends it to an LLM, and returns the answer.

---

## Notes / Progress Log

- Learned Python fundamentals (variables, functions, classes) via JS comparisons.
- Built FastAPI routes (`/`, `/health`), Pydantic models for request validation, and an async route.
- Attempted Anthropic API — hit a billing wall (no free credits without a card).
- Switched to Groq (free tier, no card required) as a stand-in LLM provider — `llama-3.3-70b-versatile`.
- Successfully called the LLM from Python and got a real response.

---

## Blockers / Questions

- Accidentally committed `.env` with a real API key before `.gitignore` caught it. GitHub push protection blocked the push.
  - Resolved: rotated the key, ran `git rm --cached .env`, scrubbed it from git history with `git filter-branch`, force-pushed successfully.

---
---

# Milestone 2: Core RAG Pipeline

**Status:** In Progress (~halfway)
**Started:**
**Completed:**

---

## Tasks

- [x] Document ingestion — load raw text from a file (`load_document` in `app/ingest.py`)
- [x] Chunking — split text into fixed-size word chunks (`chunk_text`)
- [x] Embeddings — convert chunks into vectors using `sentence-transformers` (`all-MiniLM-L6-v2`)
- [x] Vector storage — store chunks + embeddings in ChromaDB (`store_chunks`)
- [x] Retrieval — given a query, find top-matching chunks (`retrieve`)
- [x] Wire retrieval + generation into a real `/ask` FastAPI route
- [ ] Test end-to-end with a real (non-dummy) finance/compliance sample document
- [ ] Handle edge cases (empty query, no chunks stored yet, etc.)

---

## Done When

A user can POST a question to `/ask`, the app retrieves relevant chunks from a stored document, and returns an LLM-generated answer grounded in that context.

---

## Notes / Progress Log

- Built the full pipeline step by step in `app/ingest.py`: `load_document` → `chunk_text` → `embed_chunks` → `store_chunks` → `retrieve`.
- Used ChromaDB's `PersistentClient` for local, on-disk vector storage (`chroma_db/`, gitignored).
- Wired everything into `app/main.py`'s `/ask` route: retrieve top chunks → build a grounded prompt → send to Groq LLM → return answer.
- Verified retrieval correctly ranks the most semantically relevant chunk first, even with informal test text.
- Cleaned up `main.py` — removed leftover practice code (standalone functions/classes from the Python fundamentals step), keeping only the real FastAPI app.

---

## Blockers / Questions

- Port 8000 conflict when restarting uvicorn (`Address already in use`) — resolved via `lsof -ti:8000 | xargs kill -9`.
- Still using dummy/placeholder sample text — need to test with a real finance/compliance-style document before considering this milestone fully done.
