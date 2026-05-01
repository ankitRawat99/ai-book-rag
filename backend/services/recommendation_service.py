from sqlalchemy import or_
from sqlalchemy.orm import Session

import models
from ai_engine.vector_store import clean_author, search_similar


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _reason(book: models.Book, match_type: str, query: str) -> str:
    description = (book.description or "").strip()

    if match_type == "title":
        return "Title closely matches the search text."

    if description and description.lower() != "no description available":
        return description[:220]

    return f"Relevant match for: {query}"


def _serialize_book(book: models.Book, score: float, match_type: str, query: str):
    author = clean_author(book.author)

    return {
        "id": book.id,
        "title": book.title,
        "author": author if author != "Unknown" else "author unavailable",
        "description": book.description,
        "rating": book.rating,
        "url": book.url,
        "score": round(score, 4),
        "match_type": match_type,
        "reason": _reason(book, match_type, query),
    }


def _title_score(title: str, query: str) -> float:
    title_norm = _normalize(title)
    query_norm = _normalize(query)

    if title_norm == query_norm:
        return 1.0

    if query_norm in title_norm:
        return 0.92

    query_terms = set(query_norm.split())
    title_terms = set(title_norm.split())
    if not query_terms:
        return 0.0

    overlap = len(query_terms & title_terms) / len(query_terms)
    return min(0.88, 0.45 + overlap * 0.35)


def _semantic_score(distance: float | None) -> float:
    if distance is None:
        return 0.5

    return max(0.0, min(1.0, 1.0 / (1.0 + distance)))


def suggest_books(db: Session, query: str, limit: int = 10, offset: int = 0):
    query = query.strip()
    limit = max(1, min(limit, 50))
    offset = max(0, offset)
    fetch_size = limit + offset + 25
    suggestions_by_id = {}

    title_matches = (
        db.query(models.Book)
        .filter(
            or_(
                models.Book.title.ilike(f"%{query}%"),
                models.Book.author.ilike(f"%{query}%"),
            )
        )
        .limit(fetch_size)
        .all()
    )

    for book in title_matches:
        suggestions_by_id[book.id] = _serialize_book(
            book,
            _title_score(book.title, query),
            "title",
            query,
        )

    vector_results = search_similar(query, n_results=fetch_size)
    ids = vector_results.get("ids", [[]])[0]
    distances = vector_results.get("distances", [[]])[0]

    for index, book_id in enumerate(ids):
        book = db.query(models.Book).filter(models.Book.id == int(book_id)).first()
        if not book:
            continue

        semantic_score = _semantic_score(
            distances[index] if index < len(distances) else None
        )
        existing = suggestions_by_id.get(book.id)

        if existing and existing["score"] >= semantic_score:
            existing["match_type"] = "title+context"
            continue

        suggestions_by_id[book.id] = _serialize_book(
            book,
            semantic_score,
            "context",
            query,
        )

    ranked = sorted(
        suggestions_by_id.values(),
        key=lambda item: (item["score"], item["rating"] or 0),
        reverse=True,
    )

    page = ranked[offset : offset + limit]

    return {
        "query": query,
        "total": len(ranked),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < len(ranked),
        "suggestions": page,
    }
