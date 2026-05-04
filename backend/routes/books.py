from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import schemas
from ai_engine.rag_pipeline import generate_answer, generate_book_answer
from database import SessionLocal
from services import book_service
from services.recommendation_service import suggest_books

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/books", response_model=list[schemas.BookResponse])
def get_books(
    genre: str | None = None,
    limit: int = Query(default=80, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return book_service.get_all_books(db, genre=genre, limit=limit, offset=offset)


@router.get("/books/count")
def get_book_count(genre: str | None = None, db: Session = Depends(get_db)):
    return {"count": book_service.get_book_count(db, genre=genre)}


@router.get("/book/{book_id}", response_model=schemas.BookDetail)
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = book_service.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    data = schemas.BookResponse.model_validate(book).model_dump()
    summary = book_service.build_ai_summary(book)
    return {
        **data,
        "summary": summary,
        "ai_summary": summary,
        "key_points": book_service.build_key_points(book),
    }


@router.get("/genres", response_model=list[str])
def get_genres(db: Session = Depends(get_db)):
    return book_service.get_genres(db)


@router.post("/books", response_model=schemas.BookResponse)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, book)


@router.get("/search", response_model=schemas.BookSuggestionResponse)
def search_books(
    query: str,
    limit: int = Query(default=12, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return suggest_books(db, query=query, limit=limit, offset=offset)


@router.get("/suggestions", response_model=schemas.BookSuggestionResponse)
def get_book_suggestions(
    query: str,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return suggest_books(db, query=query, limit=limit, offset=offset)


@router.get("/ask")
def ask_ai(query: str):
    return {"answer": generate_answer(query)}


@router.post("/ask-book", response_model=schemas.AskBookResponse)
def ask_book(payload: schemas.AskBookRequest, db: Session = Depends(get_db)):
    book = book_service.get_book_by_id(db, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return {
        "book_id": book.id,
        "question": payload.question,
        "answer": generate_book_answer(book, payload.question),
    }
