from typing import List


def simple_chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """
    Simple chunking by character length.
    Good enough for v1.
    """
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap  # overlap for context continuity
        if start < 0:
            start = 0

    return chunks
