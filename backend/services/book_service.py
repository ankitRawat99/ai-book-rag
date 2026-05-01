from sqlalchemy.orm import Session

import models
from ai_engine.vector_store import add_book_embedding, build_book_document, clean_author


def get_all_books(db: Session):
    return db.query(models.Book).all()


def get_book_count(db: Session):
    return db.query(models.Book).count()


def find_book_by_url(db: Session, url: str):
    return db.query(models.Book).filter(models.Book.url == url).first()


def create_book(db: Session, book_data):
    payload = book_data.dict()
    payload["author"] = clean_author(payload.get("author"))

    new_book = models.Book(**payload)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    add_book_embedding(
        new_book.id,
        build_book_document(new_book),
        {
            "title": new_book.title,
            "author": clean_author(new_book.author),
            "rating": new_book.rating or 0,
            "url": new_book.url or "",
        },
    )

    return new_book


def upsert_book(db: Session, book_data):
    existing_book = find_book_by_url(db, book_data.url)

    if not existing_book:
        return create_book(db, book_data), True

    payload = book_data.dict()
    payload["author"] = clean_author(payload.get("author"))

    changed = False
    for field, value in payload.items():
        if getattr(existing_book, field) != value:
            setattr(existing_book, field, value)
            changed = True

    if changed:
        db.commit()
        db.refresh(existing_book)

    add_book_embedding(
        existing_book.id,
        build_book_document(existing_book),
        {
            "title": existing_book.title,
            "author": clean_author(existing_book.author),
            "rating": existing_book.rating or 0,
            "url": existing_book.url or "",
        },
    )

    return existing_book, False
