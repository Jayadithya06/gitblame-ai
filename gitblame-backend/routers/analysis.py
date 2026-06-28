import time
from fastapi import APIRouter
from services.vector_store import store_chunks, search_chunks
from services.llm_service import analyze_suspects
from pydantic import BaseModel

router = APIRouter()

class AnalysisRequest(BaseModel):
    chunks: list
    bug_description: str

@router.post("/analyze")
async def analyze(request: AnalysisRequest):
    start = time.time()

    store_chunks(request.chunks)
    print(f"Store chunks: {time.time() - start:.2f}s")

    t1 = time.time()
    search_results = search_chunks(request.bug_description)
    print(f"Vector search: {time.time() - t1:.2f}s")

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

    t2 = time.time()
    llm_analysis = await analyze_suspects(request.bug_description, suspects)
    print(f"LLM: {time.time() - t2:.2f}s")
    print(f"TOTAL: {time.time() - start:.2f}s")

    return llm_analysis