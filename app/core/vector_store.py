import faiss
import numpy as np
import pickle
from pathlib import Path

INDEX_PATH = Path("data/vector_index.faiss")
META_PATH = Path("data/vector_meta.pkl")

def save_to_vector_store(embeddings: np.ndarray, chunks: list[str]):
    embeddings_np = np.array(embeddings).astype("float32")
    dimension = embeddings_np.shape[1]

    if INDEX_PATH.exists() and META_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        with open(META_PATH, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dimension)
        metadata = []

    index.add(embeddings_np)
    metadata.extend(chunks)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)

def load_vector_store():
    if not INDEX_PATH.exists() or not META_PATH.exists():
        return None, None

    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata