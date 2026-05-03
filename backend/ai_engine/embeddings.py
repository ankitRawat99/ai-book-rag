import hashlib
import math

try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
except Exception:
    model = None


def _hash_embedding(text: str, dimensions: int = 384):
    vector = [0.0] * dimensions
    terms = [term.strip().lower() for term in text.replace("\n", " ").split() if term.strip()]

    for term in terms:
        digest = hashlib.sha256(term.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def get_embedding(text: str):
    if model is None:
        return _hash_embedding(text)

    return model.encode(text).tolist()
