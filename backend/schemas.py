from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    description: str
    rating: float
    url: str


class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True


class BookSuggestion(BookResponse):
    score: float
    match_type: str
    reason: str


class BookSuggestionResponse(BaseModel):
    query: str
    total: int
    limit: int
    offset: int
    has_more: bool
    suggestions: list[BookSuggestion]
