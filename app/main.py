from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from app.ingest import retrieve
from fastapi.responses import StreamingResponse

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

    chunks = retrieve(question.text, top_k=2)
    if not chunks:
        return {"error": "No documents have been ingested yet"}

    context = "\n".join(chunks)
    prompt = f"Answer the question using only this context:\n{context}\n\nQuestion: {question.text}"

    def generate():
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