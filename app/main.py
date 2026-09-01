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


load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class Question(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask(question: Question):
    if not question.text.strip():
        return {"error": "Question cannot be empty"}

    chunks, distances = retrieve(question.text, top_k=2)
    if not chunks:
        return {"error": "No documents have been ingested yet"}

    if distances[0] > 1.5:
        return {"error": "This question appears to be outside the scope of the uploaded documents."}

    # chunks = retrieve(question.text, top_k=2)
    # if not chunks:
    #     return {"error": "No documents have been ingested yet"}

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
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")

    chunks = chunk_text(text, chunk_size=200)
    vectors = embed_chunks(chunks)
    store_chunks(chunks, vectors)

    return {"status": "uploaded", "chunks_stored": len(chunks)}