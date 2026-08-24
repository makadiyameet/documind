from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from app.ingest import retrieve

load_dotenv()
app = FastAPI()
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

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response.choices[0].message.content}