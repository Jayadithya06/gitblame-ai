import httpx
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HF_TOKEN = os.getenv("HF_TOKEN")
USE_LOCAL = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"

HF_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

async def embed_text(text: str):
    if USE_LOCAL:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": text}
            )
        data = response.json()
        return data["embedding"]
    else:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HF_URL,
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": text}
            )
        result = response.json()
        if isinstance(result, list):
            return result
        raise ValueError(f"Unexpected HuggingFace response: {result}")