from urllib.parse import quote

import requests
from services.data_quality import clean_rating, normalize_author, normalize_image_url

OPEN_LIBRARY_BASE_URL = "https://openlibrary.org"
DEFAULT_SUBJECTS = [
    "fiction",
    "science_fiction",
    "fantasy",
    "history",
    "biography",
    "business",
    "psychology",
    "self_help",
    "science",
    "travel",
    "mystery",
    "romance",
    "philosophy",
    "technology",
    "health",
]

GENRE_LABELS = {
    "fiction": "Fiction",
    "science_fiction": "Sci-Fi",
    "fantasy": "Fantasy",
    "history": "History",
    "biography": "Biography",
    "business": "Business",
    "psychology": "Psychology",
    "self_help": "Self Help",
    "science": "Science",
    "travel": "Travel",
    "mystery": "Mystery",
    "romance": "Romance",
    "philosophy": "Philosophy",
    "technology": "Technology",
    "health": "Health",
}

HEADERS = {
    "User-Agent": "ai-book-rag local learning project",
}


def _format_author(work: dict) -> str:
    authors = work.get("authors") or []
    names = [author.get("name") for author in authors if author.get("name")]
    return normalize_author(", ".join(names[:3]), work.get("title"))


def _format_description(work: dict, subject: str) -> str:
    first_publish_year = work.get("first_publish_year")
    subject_label = subject.replace("_", " ")
    pieces = [f"Open Library subject: {subject_label}."]

    if first_publish_year:
        pieces.append(f"First published in {first_publish_year}.")

    return " ".join(pieces)


def _format_url(work: dict) -> str:
    key = work.get("key")
    return f"{OPEN_LIBRARY_BASE_URL}{key}" if key else OPEN_LIBRARY_BASE_URL


def _format_image(work: dict) -> str:
    cover_id = work.get("cover_id")
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    return normalize_image_url("", title=work.get("title"))


def scrape_open_library_books(
    subjects: list[str] | None = None,
    limit_per_subject: int = 100,
    offset: int = 0,
):
    books = []
    subjects = subjects or DEFAULT_SUBJECTS

    for subject in subjects:
        url = (
            f"{OPEN_LIBRARY_BASE_URL}/subjects/{quote(subject)}.json"
            f"?limit={limit_per_subject}&offset={offset}"
        )
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        data = response.json()
        for work in data.get("works", []):
            title = work.get("title")
            if not title:
                continue

            books.append(
                {
                    "title": title,
                    "author": _format_author(work),
                    "description": _format_description(work, subject),
                    "rating": clean_rating(0.0, title, _format_author(work)),
                    "url": _format_url(work),
                    "image": _format_image(work),
                    "publish_year": work.get("first_publish_year"),
                    "genre": GENRE_LABELS.get(subject, subject.replace("_", " ").title()),
                }
            )

    return books
