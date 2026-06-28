import chromadb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="diff_chunks")

def store_chunks(chunks: list):
    new_ids = []
    new_documents = []
    new_metadatas = []

    for i, chunk in enumerate(chunks):
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

    if new_ids:
        collection.add(
            documents=new_documents,
            metadatas=new_metadatas,
            ids=new_ids
        )
        print(f"Stored {len(new_ids)} new chunks, skipped {len(chunks) - len(new_ids)} existing")
    else:
        print(f"All {len(chunks)} chunks already stored — skipping embedding entirely")

    return {"stored": len(new_ids)}

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