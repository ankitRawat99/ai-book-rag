from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import schemas
from services import book_service
from ai_engine.vector_store import search_similar
from ai_engine.rag_pipeline import generate_answer


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/books", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    return book_service.get_all_books(db)


@router.post("/books", response_model=schemas.BookResponse)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, book)

@router.get("/search")
def search_books(query: str):
    results = search_similar(query)
    return results

@router.get("/ask")
def ask_ai(query: str):
    return {"answer": generate_answer(query)}