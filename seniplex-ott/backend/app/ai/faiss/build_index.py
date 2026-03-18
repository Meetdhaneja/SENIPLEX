import faiss
import numpy as np
from typing import Any, cast


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build a FAISS inner-product index for embeddings.

    Note: FAISS' Python runtime binding supports `index.add(x)`, but some type stubs
    model `add` with a different signature. We cast to `Any` to keep runtime-correct
    behavior while satisfying static type checking.
    """
    if embeddings.ndim != 2:
        raise ValueError("embeddings must be a 2D array of shape (n, d)")

    x = np.ascontiguousarray(embeddings, dtype=np.float32)
    dim = int(x.shape[1])

    index = faiss.IndexFlatIP(dim)
    cast(Any, index).add(x)
    return index


def save_index(index: faiss.Index, path: str) -> None:
    faiss.write_index(index, path)


def load_index(path: str) -> faiss.Index:
    return faiss.read_index(path)
