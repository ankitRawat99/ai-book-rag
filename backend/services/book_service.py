from sqlalchemy.orm import Session
import models
from ai_engine.vector_store import add_book_embedding

def get_all_books(db: Session):
    return db.query(models.Book).all()


def create_book(db: Session, book_data):
    new_book = models.Book(**book_data.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # 🔥 NEW: add embedding
    text = f"{new_book.title} by {new_book.author}"
    add_book_embedding(new_book.id, text)

    return new_book