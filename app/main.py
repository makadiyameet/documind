from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from app.ingest import retrieve
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, File
from app.ingest import chunk_text, embed_chunks, store_chunks
import json
import time
import json as json_module
from datetime import datetime

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_request(question, answer, duration, num_chunks, distance, prompt_tokens, completion_tokens):
    estimated_cost = (prompt_tokens * 0.00000010) + (completion_tokens * 0.00000010)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer_length": len(answer),
        "duration_seconds": round(duration, 2),
        "chunks_retrieved": num_chunks,
        "best_distance": distance,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "estimated_cost_usd": round(estimated_cost, 8),
    }
    with open("logs.jsonl", "a") as f:
        f.write(json_module.dumps(log_entry) + "\n")

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class Question(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/stats")
def get_stats():
    try:
        with open("logs.jsonl") as f:
            lines = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return {"total_requests": 0}

    if not lines:
        return {"total_requests": 0}

    total_requests = len(lines)
    avg_duration = sum(l.get("duration_seconds", 0) for l in lines) / total_requests
    total_cost = sum(l.get("estimated_cost_usd", 0) for l in lines)
    avg_distance = sum(l.get("best_distance", 0) for l in lines) / total_requests

    return {
        "total_requests": total_requests,
        "avg_duration_seconds": round(avg_duration, 2),
        "total_estimated_cost_usd": round(total_cost, 6),
        "avg_retrieval_distance": round(avg_distance, 3),
    }

@app.post("/ask")
def ask(question: Question):
    if not question.text.strip():
        return {"error": "Question cannot be empty"}

    start_time = time.time()

    chunks, distances = retrieve(question.text, top_k=2)
    if not chunks:
        return {"error": "No documents have been ingested yet"}

    if distances[0] > 1.5:
        return {"error": "This question appears to be outside the scope of the uploaded documents."}

    context = "\n".join(chunks)
    prompt = f"Answer the question using only this context:\n{context}\n\nQuestion: {question.text}"

    def generate():
        sources_json = json.dumps({"sources": chunks})
        yield sources_json + "\n<<<END_SOURCES>>>\n"

        stream = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        full_answer = ""
        prompt_tokens = 0
        completion_tokens = 0

        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                full_answer += token
                yield token
            if chunk.usage:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens

        duration = time.time() - start_time
        log_request(question.text, full_answer, duration, len(chunks), distances[0], prompt_tokens, completion_tokens)

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    chunks = chunk_text(text, chunk_size=20)
    vectors = embed_chunks(chunks)
    store_chunks(chunks, vectors)

    return {"status": "uploaded", "chunks_stored": len(chunks)}