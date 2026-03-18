"""MiniLM embedding model"""
from sentence_transformers import SentenceTransformer
from typing import List, overload, Union
import numpy as np
from app.core.config import settings

_model = None


def get_embedding_model():
    """Get or create embedding model"""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text"""
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


@overload
def encode_texts(texts: str) -> List[float]: ...


@overload
def encode_texts(texts: List[str]) -> np.ndarray: ...


def encode_texts(texts: Union[str, List[str]]) -> Union[List[float], np.ndarray]:
    model = get_embedding_model()
    if isinstance(texts, str):
        return model.encode(texts).tolist()
    return model.encode(texts)


def generate_embeddings_batch(texts: List[str]) -> np.ndarray:
    """Generate embeddings for multiple texts"""
    model = get_embedding_model()
    embeddings = model.encode(texts)
    return embeddings
