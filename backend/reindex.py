import models
from ai_engine.vector_store import (
    add_book_embeddings,
    build_book_document,
    build_book_metadata,
    clean_author,
)
from database import SessionLocal


def rebuild_index():
    db = SessionLocal()
    indexed = 0
    seen = set()

    try:
        books = db.query(models.Book).all()

        batch = []
        for book in books:
            key = f"{book.title}-{book.author}"

            if key in seen:
                continue

            seen.add(key)

            book.author = clean_author(book.author)
            batch.append(
                (
                    book.id,
                    build_book_document(book),
                    build_book_metadata(book),
                )
            )
            indexed += 1

            if len(batch) >= 128:
                add_book_embeddings(batch)
                batch = []

        add_book_embeddings(batch)

        db.commit()
    finally:
        db.close()

    print(f"Indexed {indexed} books.")
    return indexed


if __name__ == "__main__":
    rebuild_index()
