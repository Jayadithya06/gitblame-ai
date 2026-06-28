import time
from fastapi import APIRouter
from services.vector_store import store_chunks_with_embeddings, search_chunks_with_embedding
from services.embedder import embed_text
from services.llm_service import analyze_suspects
from pydantic import BaseModel
import asyncio

router = APIRouter()

class AnalysisRequest(BaseModel):
    chunks: list
    bug_description: str

@router.post("/analyze")
async def analyze(request: AnalysisRequest):
    start = time.time()

    # Embed all chunks
    texts = [
        f"{chunk['message']} {chunk['filename']} {chunk['patch']}"
        for chunk in request.chunks
    ]
    embeddings = []
    for text in texts:
        emb = await embed_text(text)
        embeddings.append(emb)
    print(f"Embeddings: {time.time() - start:.2f}s")

    t1 = time.time()
    store_chunks_with_embeddings(request.chunks, embeddings)
    print(f"Store chunks: {time.time() - t1:.2f}s")

    t2 = time.time()
    query_embedding = await embed_text(request.bug_description)
    search_results = search_chunks_with_embedding(query_embedding)
    print(f"Vector search: {time.time() - t2:.2f}s")

    suspects = []
    metadatas = search_results.get("metadatas", [[]])[0]
    documents = search_results.get("documents", [[]])[0]
    distances = search_results.get("distances", [[]])[0]

    for i, metadata in enumerate(metadatas):
        suspects.append({
            "metadata": metadata,
            "document": documents[i],
            "distance": distances[i]
        })

    t3 = time.time()
    llm_analysis = await analyze_suspects(request.bug_description, suspects)
    print(f"LLM: {time.time() - t3:.2f}s")
    print(f"TOTAL: {time.time() - start:.2f}s")

    return llm_analysis