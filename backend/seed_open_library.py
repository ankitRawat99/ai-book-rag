import argparse

import models
from ai_engine.vector_store import add_book_embedding, build_book_document, clean_author
from database import SessionLocal
from scraper.open_library_scraper import DEFAULT_SUBJECTS, scrape_open_library_books


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


def seed_open_library_books(
    subjects: list[str],
    limit_per_subject: int = 100,
    offset: int = 0,
    rebuild_index: bool = False,
):
    db = SessionLocal()
    created_count = 0
    updated_count = 0

    try:
        existing_by_url = {
            book.url: book for book in db.query(models.Book).all() if book.url
        }

        for book_data in scrape_open_library_books(
            subjects=subjects,
            limit_per_subject=limit_per_subject,
            offset=offset,
        ):
            existing_book = existing_by_url.get(book_data["url"])

            if existing_book:
                for field, value in book_data.items():
                    if field == "author":
                        value = clean_author(value)
                    setattr(existing_book, field, value)
                updated_count += 1
                continue

            book = models.Book(
                title=book_data["title"],
                author=clean_author(book_data["author"]),
                description=book_data["description"],
                rating=book_data["rating"],
                url=book_data["url"],
            )
            db.add(book)
            db.flush()
            existing_by_url[book.url] = book
            created_count += 1

            if rebuild_index:
                _sync_embedding(book)

        db.commit()
    finally:
        db.close()

    print(f"Open Library synced. Created: {created_count}. Updated: {updated_count}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed books from Open Library subjects")
    parser.add_argument("--limit-per-subject", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--subjects", nargs="*", default=DEFAULT_SUBJECTS)
    parser.add_argument("--rebuild-index", action="store_true")
    args = parser.parse_args()

    seed_open_library_books(
        subjects=args.subjects,
        limit_per_subject=args.limit_per_subject,
        offset=args.offset,
        rebuild_index=args.rebuild_index,
    )
