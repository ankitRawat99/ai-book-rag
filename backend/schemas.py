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