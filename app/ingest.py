from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("documents")


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


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return model.encode(chunks).tolist()


def store_chunks(chunks: list[str], embeddings: list[list[float]]):
    ids = [str(i) for i in range(len(chunks))]
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )

def retrieve(query: str, top_k: int = 2) -> list[str]:
    query_vector = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=top_k
    )
    return results["documents"][0]


if __name__ == "__main__":
    text = load_document("data/sample.txt")
    chunks = chunk_text(text, chunk_size=20)
    vectors = embed_chunks(chunks)
    store_chunks(chunks, vectors)

    results = retrieve("what does this say about having a good day")
    for r in results:
        print(r)
        print("---")