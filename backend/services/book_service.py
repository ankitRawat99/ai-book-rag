from sqlalchemy.orm import Session
import models


def get_all_books(db: Session):
    return db.query(models.Book).all()


def create_book(db: Session, book_data):
    new_book = models.Book(**book_data.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book