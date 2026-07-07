import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(texts: list[str]) -> np.ndarray:
    return model.encode(texts, convert_to_numpy=True)