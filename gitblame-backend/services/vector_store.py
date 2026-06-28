import chromadb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="diff_chunks")

def store_chunks(chunks: list):
    for i, chunk in enumerate(chunks):
        chunk_id = f"{chunk['sha']}_{i}"
        text = f"{chunk['message']} {chunk['filename']} {chunk['patch']}"
        
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue
            
        collection.add(
            documents=[text],
            metadatas=[{
                "sha": chunk["sha"],
                "message": chunk["message"],
                "filename": chunk["filename"]
            }],
            ids=[chunk_id]
        )
    return {"stored": len(chunks)}

def search_chunks(query_text: str, n_results: int = 3):
    count = collection.count()
    actual_n = min(n_results, count)
    if actual_n == 0:
        return {"metadatas": [[]], "documents": [[]], "distances": [[]]}
    
    results = collection.query(
        query_texts=[query_text],
        n_results=actual_n
    )
    return results