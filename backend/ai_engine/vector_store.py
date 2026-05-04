import json
import math
import os
import re
from pathlib import Path

from ai_engine.embeddings import get_embedding

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
FALLBACK_INDEX_PATH = Path(BASE_DIR) / "vector_index.json"

try:
    from chromadb import PersistentClient

    client = PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="books")
except Exception:
    client = None
    collection = None

PRICE_PATTERN = re.compile(r"\d")


def clean_author(author: str | None) -> str:
    if not author:
        return "Unknown"

    author = author.strip()
    if not author or (PRICE_PATTERN.search(author) and not re.search(r"[A-Za-z]", author)):
        return "Unknown"

    return author


def build_book_document(book) -> str:
    author = clean_author(getattr(book, "author", None))
    description = (getattr(book, "description", None) or "").strip()
    rating = getattr(book, "rating", None)
    genre = (getattr(book, "genre", None) or "General").strip()
    publish_year = getattr(book, "publish_year", None)
    summary = (getattr(book, "ai_summary", None) or "").strip()
    key_points = (getattr(book, "key_points", None) or "").strip()

    parts = [
        f"Title: {book.title}",
        f"Author: {author}",
        f"Genre: {genre}",
    ]

    if publish_year:
        parts.append(f"Publish Year: {publish_year}")

    if description and description.lower() != "scraped book":
        parts.append(f"Description: {description}")

    if summary:
        parts.append(f"Summary: {summary}")

    if key_points:
        parts.append(f"Key Points: {key_points}")

    if rating is not None:
        parts.append(f"Rating: {rating}/5")

    return "\n".join(parts)


def build_book_metadata(book) -> dict:
    return {
        "title": book.title or "",
        "author": clean_author(getattr(book, "author", None)),
        "rating": getattr(book, "rating", None) or 0,
        "url": getattr(book, "url", None) or "",
        "image": getattr(book, "image", None) or "",
        "publish_year": getattr(book, "publish_year", None) or 0,
        "genre": getattr(book, "genre", None) or "General",
    }


def _load_fallback_index():
    if not FALLBACK_INDEX_PATH.exists():
        return {}

    try:
        return json.loads(FALLBACK_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_fallback_index(index: dict):
    FALLBACK_INDEX_PATH.write_text(json.dumps(index), encoding="utf-8")


def _cosine_distance(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
    return 1.0 - (dot / (left_norm * right_norm))


def add_book_embedding(book_id: int, text: str, metadata: dict | None = None):
    embedding = get_embedding(text)

    if collection is not None:
        collection.upsert(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}],
            ids=[str(book_id)],
        )
        return

    index = _load_fallback_index()
    index[str(book_id)] = {
        "document": text,
        "embedding": embedding,
        "metadata": metadata or {},
    }
    _save_fallback_index(index)


def add_book_embeddings(items: list[tuple[int, str, dict]]):
    if not items:
        return

    ids = [str(book_id) for book_id, _, _ in items]
    documents = [text for _, text, _ in items]
    embeddings = [get_embedding(text) for text in documents]
    metadatas = [metadata or {} for _, _, metadata in items]

    if collection is not None:
        collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        return

    index = _load_fallback_index()
    for book_id, document, embedding, metadata in zip(ids, documents, embeddings, metadatas):
        index[book_id] = {
            "document": document,
            "embedding": embedding,
            "metadata": metadata,
        }
    _save_fallback_index(index)


def search_similar(query: str, n_results: int = 10):
    query_embedding = get_embedding(query)

    if collection is not None:
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    index = _load_fallback_index()
    ranked = sorted(
        (
            (
                book_id,
                item,
                _cosine_distance(query_embedding, item.get("embedding") or []),
            )
            for book_id, item in index.items()
        ),
        key=lambda row: row[2],
    )[:n_results]

    return {
        "ids": [[book_id for book_id, _, _ in ranked]],
        "documents": [[item.get("document", "") for _, item, _ in ranked]],
        "metadatas": [[item.get("metadata", {}) for _, item, _ in ranked]],
        "distances": [[distance for _, _, distance in ranked]],
    }
