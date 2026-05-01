import os

from transformers import pipeline

from ai_engine.vector_store import search_similar
from database import SessionLocal
from services.recommendation_service import suggest_books

_generator = None


def _get_generator():
    global _generator

    if _generator is None:
        _generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            model_kwargs={"local_files_only": True},
        )

    return _generator


def _extract_field(document: str, field: str) -> str:
    prefix = f"{field}:"
    for line in document.splitlines():
        if line.startswith(prefix):
            return line.replace(prefix, "", 1).strip()

    return ""


def _get_ranked_books(results: dict) -> list[dict]:
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    books = []
    for index, document in enumerate(docs):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = distances[index] if index < len(distances) else None
        author = metadata.get("author") or _extract_field(document, "Author") or "Unknown"

        books.append(
            {
                "title": metadata.get("title") or _extract_field(document, "Title"),
                "author": author if author != "Unknown" else "author unavailable",
                "description": _extract_field(document, "Description"),
                "rating": metadata.get("rating") or _extract_field(document, "Rating"),
                "url": metadata.get("url") or "",
                "distance": distance,
            }
        )

    return books


def _format_context(results: dict) -> str:
    context_blocks = []

    for index, book in enumerate(_get_ranked_books(results), start=1):
        parts = [
            f"Book {index}",
            f"Title: {book['title']}",
            f"Author: {book['author']}",
        ]

        if book["description"]:
            parts.append(f"Description: {book['description']}")

        if book["rating"]:
            parts.append(f"Rating: {book['rating']}/5")

        context_blocks.append("\n".join(parts))

    return "\n\n".join(context_blocks)


def _reason_for(book: dict, query: str) -> str:
    if book["description"]:
        return book["description"][:180]

    return f"Strong semantic match for: {query}"


def _format_ranked_answer(query: str, books: list[dict]) -> str:
    selected_books = books[:3]
    lines = ["Here are the best matches I found:"]

    for index, book in enumerate(selected_books, start=1):
        rating = f" Rating: {book['rating']}/5." if book["rating"] else ""
        lines.append(
            f"{index}. {book['title']} - {book['author']}.{rating} "
            f"Why: {_reason_for(book, query)}"
        )

    return "\n".join(lines)


def _looks_like_bad_generation(answer: str) -> bool:
    bad_markers = ["Relevance distance", "Retrieved book records", "Book 1:"]
    return not answer or any(marker in answer for marker in bad_markers)


def _generate_llm_answer(query: str, context: str) -> str:
    prompt = f"""
You are a smart book recommendation assistant.

User query:
{query}

Retrieved book records:
{context}

Instructions:
- Recommend only the 2 or 3 strongest matches from the retrieved records.
- Use only facts from the retrieved records.
- Mention title and author. If author is Unknown, write "author unavailable".
- Add one short reason for each recommendation.
- Do not include prices, URLs, or internal distances.
- Do not invent details.

Answer:
"""

    response = _get_generator()(
        prompt,
        max_length=220,
        num_return_sequences=1,
        do_sample=False,
    )

    return response[0]["generated_text"].replace("\n\n", "\n").strip()


def generate_answer(query: str):
    db = SessionLocal()
    try:
        suggestion_result = suggest_books(db, query=query, limit=5, offset=0)
    finally:
        db.close()

    if not suggestion_result["suggestions"]:
        return "No books found. Please add books first."

    books = suggestion_result["suggestions"]
    fallback_answer = _format_ranked_answer(query, books)

    if os.getenv("USE_LLM_ANSWER") != "1":
        return fallback_answer

    results = search_similar(query, n_results=5)
    answer = _generate_llm_answer(query, _format_context(results))

    if _looks_like_bad_generation(answer):
        return fallback_answer

    return answer
