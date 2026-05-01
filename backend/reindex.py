from database import SessionLocal
import models
from ai_engine.vector_store import add_book_embedding, build_book_document, clean_author

db = SessionLocal()

books = db.query(models.Book).all()
seen = set()

for book in books:
    key = f"{book.title}-{book.author}"

    if key in seen:
        continue

    seen.add(key)

    book.author = clean_author(book.author)
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

db.commit()
db.close()
