from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_document(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# if __name__ == "__main__":
#     text = load_document("data/sample.txt")
#     chunks = chunk_text(text, chunk_size=20)
#     for c in chunks:
#         print(c)
#         print("---")

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return model.encode(chunks).tolist()


if __name__ == "__main__":
    text = load_document("data/sample.txt")
    chunks = chunk_text(text, chunk_size=20)
    vectors = embed_chunks(chunks)
    print(len(vectors), "vectors")
    print(len(vectors[0]), "dimensions each")
    print(vectors[0][:5], "... (first 5 numbers)")