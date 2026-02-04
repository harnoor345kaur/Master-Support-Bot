from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
from google import genai
import os
from dotenv import load_dotenv

from rag.store import load_index
from llm.gemini_llm import GeminiLLM
from fastapi.middleware.cors import CORSMiddleware

from fastapi import HTTPException

load_dotenv()

app = FastAPI(title="Master Support Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """
You are a helpful AI Support Engineer for a SaaS product.

Rules:
- Answer ONLY using the provided context.
- If the answer is not present in context, say: "I don't have that information in the documentation yet."
- Keep answers short, actionable, and professional.

Formatting rules (IMPORTANT):
- If steps are needed, ALWAYS return them as bullet points using "- "
- Add a short friendly opening line (1 sentence max)
- Do NOT use "*" for bullets.
- End with: "Let me know if you want help with anything else 😊"
"""



class AskRequest(BaseModel):
    question: str
    password: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float


def embed_query(client, text: str) -> np.ndarray:
    result = client.models.embed_content(
        model="text-embedding-004",
        contents=text
    )
    embedding = result.embeddings[0].values
    return np.array(embedding, dtype=np.float32)


@app.post("/ask", response_model=AskResponse)
def ask_bot(req: AskRequest):
    demo_password = os.getenv("DEMO_PASSWORD")

    # If DEMO_PASSWORD is set, API becomes password-protected
    if demo_password:
        if not req.password or req.password != demo_password:
            raise HTTPException(status_code=401, detail="Invalid demo password")

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found")
    client = genai.Client(api_key=api_key)

    index, chunks = load_index()

    qvec = embed_query(client, req.question).reshape(1, -1)

    k = 4  # top chunks
    distances, indices = index.search(qvec, k)

    retrieved_chunks = [chunks[i] for i in indices[0] if i != -1]

    # Simple confidence from distance
    # Smaller distance = better match
    # We’ll convert to 0-1 score (rough)
    avg_dist = float(np.mean(distances[0]))
    confidence = max(0.0, min(1.0, 1.0 / (1.0 + avg_dist)))

    llm = GeminiLLM(model_name="models/gemini-flash-latest")
    answer = llm.generate_with_context(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=req.question,
        context_chunks=retrieved_chunks,
    )

    # For v1, sources are the raw chunks (later we’ll store doc titles/urls)
    sources = retrieved_chunks[:2]

    return AskResponse(answer=answer, sources=sources, confidence=confidence)
