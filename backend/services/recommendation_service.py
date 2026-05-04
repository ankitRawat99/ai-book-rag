from sqlalchemy import or_
from sqlalchemy.orm import Session

import models
from ai_engine.vector_store import clean_author, search_similar
from services.data_quality import clean_rating, normalize_author, normalize_image_url


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _split_terms(value: str) -> set[str]:
    return {term for term in _normalize(value).replace("-", " ").split() if len(term) > 2}


GENRE_INTENTS = {
    "Sci-Fi": {"space", "alien", "future", "futuristic", "robot", "technology", "science", "dystopian"},
    "Fantasy": {"magic", "dragon", "quest", "myth", "kingdom", "epic", "wizard"},
    "Mystery": {"mystery", "detective", "crime", "clue", "thriller", "suspense"},
    "Romance": {"love", "romance", "relationship", "heartbreak", "marriage"},
    "Business": {"startup", "business", "leadership", "management", "entrepreneur", "money"},
    "Self Help": {"habit", "productivity", "mindset", "self", "confidence", "growth"},
    "History": {"history", "war", "ancient", "empire", "historical"},
    "Biography": {"biography", "memoir", "life", "autobiography"},
    "Travel": {"travel", "journey", "adventure", "country", "world"},
    "Health": {"health", "fitness", "wellness", "nutrition"},
    "Philosophy": {"philosophy", "meaning", "ethics", "wisdom", "thought"},
}


def _intent_genres(query: str) -> set[str]:
    terms = _split_terms(query)
    return {
        genre
        for genre, keywords in GENRE_INTENTS.items()
        if terms & keywords
    }


def _reason(book: models.Book, match_type: str, query: str) -> str:
    description = (book.description or "").strip()
    genre = book.genre or "General"
    year = f", first published in {book.publish_year}" if book.publish_year else ""
    rating = clean_rating(book.rating, book.title, book.author)

    if match_type == "title":
        return f"Strong title or author match in {genre}{year}. Reader rating: {rating:.1f}/5."

    if match_type == "genre":
        return f"Good fit for readers asking for {genre}. Reader rating: {rating:.1f}/5."

    if description and description.lower() != "no description available":
        sentence = description.split(".")[0].strip()
        if 45 <= len(sentence) <= 220:
            return sentence + "."
        return description[:220].strip()

    return f"Relevant semantic match for '{query}' in {genre}. Reader rating: {rating:.1f}/5."


def _serialize_book(book: models.Book, score: float, match_type: str, query: str):
    author = normalize_author(clean_author(book.author), book.title)

    return {
        "id": book.id,
        "title": book.title,
        "author": author,
        "description": book.description,
        "rating": clean_rating(book.rating, book.title, author),
        "url": book.url,
        "image": normalize_image_url(book.image, book.url, book.title),
        "publish_year": book.publish_year,
        "genre": book.genre or "General",
        "score": round(score, 4),
        "match_type": match_type,
        "reason": _reason(book, match_type, query),
    }


def _text_score(book: models.Book, query: str) -> tuple[float, str]:
    title_norm = _normalize(book.title)
    query_norm = _normalize(query)
    author_norm = _normalize(book.author)
    genre_norm = _normalize(book.genre)
    haystack_terms = _split_terms(" ".join([
        book.title or "",
        book.author or "",
        book.genre or "",
        book.description or "",
    ]))
    title_author_terms = _split_terms(" ".join([book.title or "", book.author or ""]))
    query_terms = _split_terms(query)

    if title_norm == query_norm:
        return 1.0, "title"

    if query_norm and query_norm in title_norm:
        return 0.94, "title"

    if query_norm and query_norm in author_norm:
        return 0.9, "title"

    if query_terms:
        title_overlap = len(query_terms & title_author_terms) / len(query_terms)
        if title_overlap >= 1:
            return 0.96, "title"
        if title_overlap >= 0.5:
            return 0.88, "title"

    if query_norm and query_norm == genre_norm:
        return 0.86, "genre"

    if book.genre in _intent_genres(query):
        return 0.82, "genre"

    if not query_terms:
        return 0.0, "context"

    overlap = len(query_terms & haystack_terms) / len(query_terms)
    return min(0.84, 0.38 + overlap * 0.42), "context"


def _semantic_score(distance: float | None) -> float:
    if distance is None:
        return 0.5

    return max(0.0, min(1.0, 1.0 / (1.0 + distance)))


def _combined_score(base_score: float, book: models.Book) -> float:
    rating = clean_rating(book.rating, book.title, book.author)
    rating_bonus = max(0.0, (rating - 3.5) / 10)
    metadata_bonus = 0.0
    if book.publish_year:
        metadata_bonus += 0.015
    if book.image and not str(book.image).startswith("data:image"):
        metadata_bonus += 0.015
    if book.description and book.description.lower() != "no description available":
        metadata_bonus += 0.02

    return min(1.0, base_score + rating_bonus + metadata_bonus)


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
                models.Book.genre.ilike(f"%{query}%"),
            )
        )
        .limit(fetch_size)
        .all()
    )

    query_terms = _split_terms(query)
    if query_terms:
        token_filters = []
        for term in query_terms:
            like = f"%{term}%"
            token_filters.append(models.Book.title.ilike(like))
            token_filters.append(models.Book.author.ilike(like))

        for book in (
            db.query(models.Book)
            .filter(or_(*token_filters))
            .limit(fetch_size)
            .all()
        ):
            base_score, match_type = _text_score(book, query)
            suggestions_by_id[book.id] = _serialize_book(
                book,
                _combined_score(base_score, book),
                match_type,
                query,
            )

    intent_genres = _intent_genres(query)
    if intent_genres:
        for book in (
            db.query(models.Book)
            .filter(models.Book.genre.in_(intent_genres))
            .order_by(models.Book.rating.desc(), models.Book.title)
            .limit(fetch_size)
            .all()
        ):
            base_score, match_type = _text_score(book, query)
            suggestions_by_id[book.id] = _serialize_book(
                book,
                _combined_score(base_score, book),
                match_type,
                query,
            )

    for book in title_matches:
        base_score, match_type = _text_score(book, query)
        suggestions_by_id[book.id] = _serialize_book(
            book,
            _combined_score(base_score, book),
            match_type,
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
        combined_score = _combined_score(semantic_score, book)
        existing = suggestions_by_id.get(book.id)

        if existing and existing["score"] >= combined_score:
            existing["match_type"] = "title+context"
            continue

        suggestions_by_id[book.id] = _serialize_book(
            book,
            combined_score,
            "context",
            query,
        )

    query_terms = _split_terms(query)
    ranked_all = sorted(
        suggestions_by_id.values(),
        key=lambda item: (
            item["score"],
            query_terms.issubset(_split_terms(item["title"])),
            -len(_split_terms(item["title"]) - query_terms),
            item["rating"] or 0,
            -len(item["title"]),
        ),
        reverse=True,
    )

    ranked = []
    seen_books = set()
    for item in ranked_all:
        dedupe_key = (_normalize(item["title"]), _normalize(item["author"]))
        if dedupe_key in seen_books:
            continue
        seen_books.add(dedupe_key)
        ranked.append(item)

    page = ranked[offset : offset + limit]

    return {
        "query": query,
        "total": len(ranked),
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < len(ranked),
        "suggestions": page,
    }
