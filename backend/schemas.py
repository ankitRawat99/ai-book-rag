from pydantic import BaseModel, model_validator

from services.data_quality import clean_rating, normalize_author, normalize_image_url


class BookCreate(BaseModel):
    title: str
    author: str = "Unknown"
    description: str = "No description available"
    rating: float = 0.0
    url: str = ""
    image: str = ""
    publish_year: int | None = None
    genre: str = "General"


class BookResponse(BookCreate):
    id: int

    @model_validator(mode="after")
    def normalize_response(self):
        self.author = normalize_author(self.author, self.title)
        self.image = normalize_image_url(self.image, self.url, self.title)
        self.rating = clean_rating(self.rating, self.title, self.author)
        self.genre = self.genre or "General"
        return self

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


class BookDetail(BookResponse):
    summary: str
    ai_summary: str
    key_points: list[str]


class AskBookRequest(BaseModel):
    book_id: int
    question: str


class AskBookResponse(BaseModel):
    book_id: int
    question: str
    answer: str
