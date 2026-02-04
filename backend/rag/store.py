import os
import faiss
import numpy as np
from typing import List, Tuple

INDEX_DIR = "index"
INDEX_FILE = os.path.join(INDEX_DIR, "docs.index")
CHUNKS_FILE = os.path.join(INDEX_DIR, "chunks.npy")


def ensure_index_dir():
    os.makedirs(INDEX_DIR, exist_ok=True)


def save_index(index: faiss.IndexFlatL2, chunks: List[str], vectors: np.ndarray):
    ensure_index_dir()
    faiss.write_index(index, INDEX_FILE)
    np.save(CHUNKS_FILE, np.array(chunks, dtype=object))


def load_index() -> Tuple[faiss.IndexFlatL2, List[str]]:
    if not os.path.exists(INDEX_FILE) or not os.path.exists(CHUNKS_FILE):
        raise FileNotFoundError("Index not found. Run ingest first.")

    index = faiss.read_index(INDEX_FILE)
    chunks = np.load(CHUNKS_FILE, allow_pickle=True).tolist()
    return index, chunks
