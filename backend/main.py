from fastapi import FastAPI
from database import engine, Base
import models
from routes import books

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(books.router)

@app.get("/")
def home():
    return {"message": "FastAPI is running 🚀"}