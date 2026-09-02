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
- Switched to Groq (free tier, no card required) as a stand-in LLM provider.
- Successfully called the LLM from Python and got a real response.

---

## Blockers / Questions

- Accidentally committed `.env` with a real API key before `.gitignore` caught it. GitHub push protection blocked the push.
  - Resolved: rotated the key, ran `git rm --cached .env`, scrubbed it from git history with `git filter-branch`, force-pushed successfully.

---
---

# Milestone 2: Core RAG Pipeline

**Status:** Done
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
- [x] Test end-to-end with a real (non-dummy) finance/compliance sample document
- [x] Handle edge cases (empty query, no chunks stored yet, etc.)

---

## Done When

A user can POST a question to `/ask`, the app retrieves relevant chunks from a stored document, and returns an LLM-generated answer grounded in that context.

**✅ Confirmed working** — tested with real compliance-style sample text (transaction reporting rules) and got a correctly grounded answer citing the exact policy section.

---

## Notes / Progress Log

- Built the full pipeline step by step in `app/ingest.py`: `load_document` → `chunk_text` → `embed_chunks` → `store_chunks` → `retrieve`.
- Used ChromaDB's `PersistentClient` for local, on-disk vector storage (`chroma_db/`, gitignored).
- Wired everything into `app/main.py`'s `/ask` route: retrieve top chunks → build a grounded prompt → send to Groq LLM → return answer.
- Verified retrieval correctly ranks the most semantically relevant chunk first, even with informal test text.
- Cleaned up `main.py` — removed leftover practice code (standalone functions/classes from the Python fundamentals step), keeping only the real FastAPI app.
- Replaced dummy sample text with realistic finance/compliance content (transaction reporting policy) and re-ran ingestion.
- Added edge case handling to `/ask`: empty/whitespace-only questions return a clear error instead of hitting the LLM; empty retrieval results (no documents ingested) also return a clear error instead of crashing.

---

## Blockers / Questions

- Port 8000 conflict when restarting uvicorn (`Address already in use`) — resolved via `lsof -ti:8000 | xargs kill -9`.
- Groq deprecated `llama-3.3-70b-versatile` (404 `model_not_found`) — switched to `openai/gpt-oss-20b`, confirmed working.

---
---

# Milestone 3: React Frontend Polish

**Status:** Done
**Started:**
**Completed:**

---

## Tasks

- [x] Scaffold React app with Vite (`documind-frontend/`)
- [x] Connect frontend to FastAPI backend (basic fetch to `/ask`)
- [x] Chat bubble UI (user/bot messages, styled with CSS)
- [x] CORS middleware added to FastAPI backend
- [x] Streaming responses — backend `StreamingResponse` + generator, frontend `ReadableStream` reader
- [x] Document upload — `/upload` route with `python-multipart`, frontend file input + `FormData`
- [x] Citations — backend sends source chunks as JSON before a delimiter, then streams the answer; frontend parses and displays both

---

## Done When

A user can upload a document, ask a question in a chat-style UI, see the answer stream in progressively, and see which source chunks the answer was grounded in.

**✅ Confirmed working** — uploaded a real compliance document through the UI, asked questions, got streamed answers with correct source citations displayed underneath.

---

## Notes / Progress Log

- Scaffolded frontend with `npm create vite@latest documind-frontend -- --template react`.
- Hit a Node/rolldown native binding error on scaffold — resolved by upgrading Node to `22.12.0` via `nvm`.
- Built basic fetch-based Q&A UI first, then upgraded to full chat bubble UI with message history (`useState` array of `{role, text}`).
- Hit CORS `405 Method Not Allowed` on preflight `OPTIONS` requests — resolved by adding `CORSMiddleware` to FastAPI with `allow_origins=["http://localhost:5173"]`.
- Implemented streaming: backend uses a Python generator (`yield`) wrapped in `StreamingResponse`; frontend reads the response body via `res.body.getReader()` + `TextDecoder`, appending tokens to the last message as they arrive.
- Implemented file upload: backend `/upload` route using `UploadFile`/`File` (required installing `python-multipart`); frontend uses `FormData` + file input, no manual `Content-Type` header needed.
- Implemented citations: backend sends `{"sources": [...]}` JSON followed by a `<<<END_SOURCES>>>` delimiter, then streams the answer text after it. Frontend buffers incoming chunks, detects the delimiter, parses sources out, then appends the remainder as answer text.
- Debugged a subtle JS closure bug: reused a shared `buffer` variable inside a `setMessages` functional updater, then reset it (`buffer = ""`) before React's state update actually ran — meaning every update appended an empty string and the answer text never showed (only citations rendered). Fixed by capturing the current buffer into a separate constant before resetting it, so the closure captured the correct value.
- Merged `documind-frontend/` into the main `documind` repo as a nested folder, so the whole project lives in one git history.

---

## Blockers / Questions

- npm optional-dependencies bug on scaffold (`Cannot find native binding`, related to npm/cli#4828) — resolved via clean reinstall + Node upgrade to 22.12.0.
- Groq deprecated `llama-3.3-70b-versatile` again surfaced here during testing — already on `openai/gpt-oss-20b`, no change needed.

---
---

# Milestone 4: Evaluation + Guardrails

**Status:** Done
**Started:**
**Completed:**

---

## Tasks

- [x] Build a small test set of real questions + expected answers (`eval/test_set.json`)
- [x] Build an eval script that runs the test set against the live `/ask` endpoint (`eval/run_eval.py`)
- [x] Automated scoring — fuzzy key-term overlap matching instead of exact string match
- [x] Guardrails — reject questions outside the uploaded document's scope using retrieval distance threshold

---

## Done When

Running the eval script gives a pass/fail score across all test questions, and the bot correctly refuses to answer questions unrelated to the uploaded documents instead of hallucinating an answer.

**✅ Confirmed working** — 4/4 test questions passed with fuzzy scoring; off-topic question ("what is the capital of France?") correctly rejected with a scope error, while all real compliance questions still passed after adding the guardrail.

---

## Notes / Progress Log

- Built `eval/test_set.json` — 4 question/expected-answer pairs based on the real compliance sample document content.
- Built `eval/run_eval.py` using the `requests` library to call the live `/ask` endpoint and compare actual vs expected answers.
- First scoring approach (exact substring match) failed all 4 cases — LLM paraphrasing meant expected text never appeared verbatim in actual answers, even when factually correct.
- Improved to fuzzy scoring: split both expected and actual answers into word sets, check what percentage of expected words appear in the actual answer (`threshold=0.6`).
- Hit a second scoring bug: hyphenation mismatch ("anti-money laundering" vs "anti‑money‑laundering") caused a false fail even though wording was correct — fixed by normalizing hyphens/punctuation before splitting into words.
- Reached 4/4 passing after normalization fix.
- Added guardrails: updated `retrieve()` in `app/ingest.py` to also return ChromaDB distance scores, not just chunks. In `/ask`, if the best (closest) match's distance exceeds `1.5`, the route returns a scope-rejection error instead of generating an answer.
- Verified the guardrail doesn't cause false rejections — re-ran the eval script after adding it, all 4 real questions still passed.

---

## Blockers / Questions

- None outstanding. Distance threshold (`1.5`) is a rough starting value tuned against a small test set — may need adjustment as more/varied documents are tested later.

---

**Milestone 4 fully complete. Ready to start Milestone 5: Monitoring + Cost Tracking.**
