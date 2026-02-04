import os
import numpy as np
import faiss
from dotenv import load_dotenv

from google import genai
from rag.chunking import simple_chunk_text
from rag.store import save_index

load_dotenv()

# THIS IS THE DOC FILE TO BE REPLACED - HERE
DATA_FILE = "data/docs.txt"


def get_embedding(client: genai.Client, text: str) -> np.ndarray:
    """
    Generate embedding vector using Gemini embedding model.
    """
    result = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )

    # result.embeddings is a list, take the first embedding
    embedding = result.embeddings[0].values
    return np.array(embedding, dtype=np.float32)


def ingest_docs():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env")

    # Create Gemini client
    client = genai.Client(api_key=api_key)

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"{DATA_FILE} not found")

    # Read complete docs text
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # Split into chunks
    chunks = simple_chunk_text(text, chunk_size=800, overlap=120)

    # Create embedding vectors for all chunks
    vectors = []
    for c in chunks:
        vec = get_embedding(client, c)
        vectors.append(vec)

    vectors = np.vstack(vectors)
    dim = vectors.shape[1]

    # Build FAISS index and add vectors
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save index + chunks
    save_index(index, chunks, vectors)

    print(f"Ingestion complete: {len(chunks)} chunks indexed.")


if __name__ == "__main__":
    ingest_docs()
