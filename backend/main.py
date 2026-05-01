from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routes import books

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
    ],
    allow_origin_regex=r"http://.*:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)


@app.get("/")
def home():
    return {"message": "FastAPI is running"}
