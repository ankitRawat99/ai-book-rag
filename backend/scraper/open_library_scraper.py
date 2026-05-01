from urllib.parse import quote

import requests

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

HEADERS = {
    "User-Agent": "ai-book-rag local learning project",
}


def _format_author(work: dict) -> str:
    authors = work.get("authors") or []
    names = [author.get("name") for author in authors if author.get("name")]
    return ", ".join(names[:3]) if names else "Unknown"


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
                    "rating": 0.0,
                    "url": _format_url(work),
                }
            )

    return books
