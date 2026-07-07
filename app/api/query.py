import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.embedding import get_embeddings
from app.core.vector_store import load_vector_store
from app.core.generator import generate_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@router.post("/query")
async def query_documents(request: QueryRequest):
    index, metadata = load_vector_store()

    if index is None or metadata is None:
        raise HTTPException(status_code=404, detail="No documents indexed yet. Upload a document first.")

    query_embedding = get_embeddings([request.query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, request.top_k)

    chunks = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx != -1 and idx < len(metadata):
            chunks.append(metadata[idx])

    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")

    answer = generate_answer(request.query, chunks)

    return {
        "query": request.query,
        "answer": answer,
        "sources": chunks
    }