import chromadb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="diff_chunks")

def store_chunks_with_embeddings(chunks: list, embeddings: list):
    new_ids = []
    new_documents = []
    new_metadatas = []
    new_embeddings = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{chunk['sha']}_{i}"
        text = f"{chunk['message']} {chunk['filename']} {chunk['patch']}"

        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue

        new_ids.append(chunk_id)
        new_documents.append(text)
        new_metadatas.append({
            "sha": chunk["sha"],
            "message": chunk["message"],
            "filename": chunk["filename"]
        })
        new_embeddings.append(embedding)

    if new_ids:
        collection.add(
            documents=new_documents,
            embeddings=new_embeddings,
            metadatas=new_metadatas,
            ids=new_ids
        )
        print(f"Stored {len(new_ids)} new chunks")
    else:
        print(f"All chunks already stored")

    return {"stored": len(new_ids)}

def search_chunks_with_embedding(query_embedding: list, n_results: int = 3):
    count = collection.count()
    actual_n = min(n_results, count)
    if actual_n == 0:
        return {"metadatas": [[]], "documents": [[]], "distances": [[]]}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=actual_n
    )
    return results