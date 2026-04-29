from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

router = APIRouter()

# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# GET all books
@router.get("/books", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()


# POST new book
@router.post("/books", response_model=schemas.BookResponse)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book