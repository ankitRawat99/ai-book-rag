import os
import re

from chromadb import PersistentClient

from ai_engine.embeddings import get_embedding

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

client = PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(name="books")

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

    parts = [
        f"Title: {book.title}",
        f"Author: {author}",
    ]

    if description and description.lower() != "scraped book":
        parts.append(f"Description: {description}")

    if rating is not None:
        parts.append(f"Rating: {rating}/5")

    return "\n".join(parts)


def add_book_embedding(book_id: int, text: str, metadata: dict | None = None):
    collection.upsert(
        documents=[text],
        embeddings=[get_embedding(text)],
        metadatas=[metadata or {}],
        ids=[str(book_id)],
    )


def search_similar(query: str, n_results: int = 10):
    query_embedding = get_embedding(query)

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
