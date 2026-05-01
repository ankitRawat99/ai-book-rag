from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import schemas
from services import book_service
from services.recommendation_service import suggest_books
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


@router.get("/books/count")
def get_book_count(db: Session = Depends(get_db)):
    return {"count": book_service.get_book_count(db)}


@router.post("/books", response_model=schemas.BookResponse)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, book)

@router.get("/search")
def search_books(query: str):
    results = search_similar(query)
    return results


@router.get("/suggestions", response_model=schemas.BookSuggestionResponse)
def get_book_suggestions(
    query: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return suggest_books(db, query=query, limit=limit, offset=offset)

@router.get("/ask")
def ask_ai(query: str):
    return {"answer": generate_answer(query)}
