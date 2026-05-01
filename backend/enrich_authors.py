import argparse
import time
from urllib.parse import quote

import requests

import models
from ai_engine.vector_store import add_book_embedding, build_book_document, clean_author
from database import SessionLocal

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
HEADERS = {
    "User-Agent": "ai-book-rag local learning project",
}


def _lookup_author(title: str) -> str:
    response = requests.get(
        f"{OPEN_LIBRARY_SEARCH_URL}?title={quote(title)}&limit=1",
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    docs = response.json().get("docs", [])

    if not docs:
        return "Unknown"

    author_names = docs[0].get("author_name") or []
    return ", ".join(author_names[:3]) if author_names else "Unknown"


def _sync_embedding(book):
    add_book_embedding(
        book.id,
        build_book_document(book),
        {
            "title": book.title,
            "author": clean_author(book.author),
            "rating": book.rating or 0,
            "url": book.url or "",
        },
    )


def enrich_authors(limit: int = 100, pause_seconds: float = 1.0):
    db = SessionLocal()
    updated_count = 0
    checked_count = 0

    try:
        books = (
            db.query(models.Book)
            .filter(models.Book.author == "Unknown")
            .limit(limit)
            .all()
        )

        for book in books:
            checked_count += 1
            author = clean_author(_lookup_author(book.title))

            if author != "Unknown":
                book.author = author
                updated_count += 1
                _sync_embedding(book)
                db.commit()

            time.sleep(pause_seconds)
    finally:
        db.close()

    print(f"Author enrichment checked {checked_count}. Updated {updated_count}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich Unknown authors via Open Library search")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--pause", type=float, default=1.0)
    args = parser.parse_args()

    enrich_authors(limit=args.limit, pause_seconds=args.pause)
