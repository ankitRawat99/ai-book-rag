from sqlalchemy import Column, Float, Integer, String, Text
from database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    rating = Column(Float)
    url = Column(String)
    image = Column(String)
    publish_year = Column(Integer)
    genre = Column(String)
    ai_summary = Column(Text)
    key_points = Column(Text)
