import argparse

import models
from ai_engine.vector_store import add_book_embedding, build_book_document, clean_author
from database import SessionLocal
from scraper.book_scraper import scrape_books


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


def seed_books(pages: int = 50, include_details: bool = False, rebuild_index: bool = True):
    db = SessionLocal()
    created_count = 0
    updated_count = 0

    try:
        existing_by_url = {
            book.url: book for book in db.query(models.Book).all() if book.url
        }

        for book_data in scrape_books(pages=pages, include_details=include_details):
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
            created_count += 1

        db.commit()

        if rebuild_index:
            for book in db.query(models.Book).all():
                _sync_embedding(book)
    finally:
        db.close()

    print(f"Books synced. Created: {created_count}. Updated: {updated_count}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed books from books.toscrape.com")
    parser.add_argument("--pages", type=int, default=50)
    parser.add_argument("--with-details", action="store_true")
    parser.add_argument("--skip-index", action="store_true")
    args = parser.parse_args()

    seed_books(
        pages=args.pages,
        include_details=args.with_details,
        rebuild_index=not args.skip_index,
    )
