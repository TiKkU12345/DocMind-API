from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.query import router as query_router

app = FastAPI(
    title = "DocMind API",
    description = "RAG-based AI Knowledge Assistant",
    version = "0.1.0"
)

app.include_router(upload_router)
app.include_router(query_router)

@app.get("/health")
def health_check():
    return {"status": "ok",
             "message": "DocMind backend running"}
