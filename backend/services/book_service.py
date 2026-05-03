from sqlalchemy.orm import Session

import models
from ai_engine.vector_store import (
    add_book_embedding,
    build_book_document,
    build_book_metadata,
    clean_author,
)
from services.data_quality import (
    build_key_points_list,
    build_summary_text,
    clean_rating,
    dump_key_points,
    fetch_open_library_metadata,
    load_key_points,
    normalize_author,
    normalize_image_url,
)


def get_all_books(db: Session, genre: str | None = None, limit: int = 80, offset: int = 0):
    query = db.query(models.Book)

    if genre:
        query = query.filter(models.Book.genre.ilike(genre))

    return query.order_by(models.Book.rating.desc(), models.Book.title).offset(offset).limit(limit).all()


def get_book_count(db: Session):
    return db.query(models.Book).count()


def find_book_by_url(db: Session, url: str):
    return db.query(models.Book).filter(models.Book.url == url).first()


def get_book_by_id(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        ensure_book_quality(db, book)
    return book


def get_genres(db: Session):
    rows = db.query(models.Book.genre).filter(models.Book.genre.isnot(None)).distinct().all()
    return sorted(row[0] for row in rows if row[0])


def ensure_book_quality(db: Session, book: models.Book):
    changed = False
    current_author = normalize_author(book.author, book.title)

    should_enrich = (
        current_author == "Unknown author"
        or not book.image
        or str(book.image).startswith("data:image")
        or not book.publish_year
    )
    metadata = fetch_open_library_metadata(book.title or "", book.author) if should_enrich else {}

    enriched_author = normalize_author(metadata.get("author") or current_author, book.title)
    if book.author != enriched_author:
        book.author = enriched_author
        changed = True

    next_image = normalize_image_url(metadata.get("image") or book.image, book.url, book.title)
    if book.image != next_image:
        book.image = next_image
        changed = True

    if metadata.get("publish_year") and not book.publish_year:
        book.publish_year = metadata["publish_year"]
        changed = True

    next_rating = clean_rating(book.rating, book.title, book.author)
    if book.rating != next_rating:
        book.rating = next_rating
        changed = True

    if not book.ai_summary:
        book.ai_summary = build_summary_text(book)
        changed = True

    if not load_key_points(book.key_points):
        book.key_points = dump_key_points(build_key_points_list(book))
        changed = True

    if changed:
        db.commit()
        db.refresh(book)

    return book


def build_ai_summary(book):
    return book.ai_summary or build_summary_text(book)


def build_key_points(book):
    return load_key_points(book.key_points) or build_key_points_list(book)


def create_book(db: Session, book_data):
    payload = book_data.dict()
    payload["author"] = normalize_author(clean_author(payload.get("author")), payload.get("title"))
    payload["image"] = normalize_image_url(payload.get("image"), payload.get("url"), payload.get("title"))
    payload["rating"] = clean_rating(payload.get("rating"), payload.get("title"), payload.get("author"))

    new_book = models.Book(**payload)
    db.add(new_book)
    db.flush()
    new_book.ai_summary = build_summary_text(new_book)
    new_book.key_points = dump_key_points(build_key_points_list(new_book))
    db.commit()
    db.refresh(new_book)

    add_book_embedding(
        new_book.id,
        build_book_document(new_book),
        build_book_metadata(new_book),
    )

    return new_book


def upsert_book(db: Session, book_data):
    existing_book = find_book_by_url(db, book_data.url)

    if not existing_book:
        return create_book(db, book_data), True

    payload = book_data.dict()
    payload["author"] = normalize_author(clean_author(payload.get("author")), payload.get("title"))
    payload["image"] = normalize_image_url(payload.get("image"), payload.get("url"), payload.get("title"))
    payload["rating"] = clean_rating(payload.get("rating"), payload.get("title"), payload.get("author"))

    changed = False
    for field, value in payload.items():
        if getattr(existing_book, field) != value:
            setattr(existing_book, field, value)
            changed = True

    if changed:
        existing_book.ai_summary = build_summary_text(existing_book)
        existing_book.key_points = dump_key_points(build_key_points_list(existing_book))
        db.commit()
        db.refresh(existing_book)

    add_book_embedding(
        existing_book.id,
        build_book_document(existing_book),
        build_book_metadata(existing_book),
    )

    return existing_book, False
