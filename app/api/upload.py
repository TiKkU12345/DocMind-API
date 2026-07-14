from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from pypdf import PdfReader
from app.services.text_splitter import split_text
from app.core.embedding import get_embeddings
from app.core.vector_store import save_to_vector_store

router = APIRouter()

UPLOAD_DIR = Path("data/raw_docs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed")

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        text = file_path.read_text(encoding="utf-8")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in the document")

    chunks = split_text(text)
    embeddings = get_embeddings(chunks)
    save_to_vector_store(embeddings, chunks)

    return {
        "filename": file.filename,
        "chunks_created": len(chunks),
        "status": "indexed"
    }