import os

from transformers import pipeline

from ai_engine.vector_store import search_similar
from database import SessionLocal
from services.recommendation_service import suggest_books
from services.data_quality import build_key_points_list, build_summary_text, normalize_author

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
    if book.get("reason"):
        return book["reason"]

    if book["description"]:
        sentence = book["description"].split(".")[0].strip()
        if 45 <= len(sentence) <= 180:
            return sentence + "."
        return book["description"][:180].strip()

    return f"Strong semantic match for: {query}"


def _format_ranked_answer(query: str, books: list[dict]) -> str:
    selected_books = books[:3]
    lines = [f"Best grounded matches for '{query}':"]

    for index, book in enumerate(selected_books, start=1):
        rating = f" Rating: {float(book['rating']):.1f}/5." if book.get("rating") else ""
        genre = f" Genre: {book['genre']}." if book.get("genre") else ""
        lines.append(
            f"{index}. {book['title']} - {book['author']}.{genre}{rating} "
            f"Why it fits: {_reason_for(book, query)}"
        )

    return "\n".join(lines)


def _looks_like_bad_generation(answer: str) -> bool:
    bad_markers = ["Relevance distance", "Retrieved book records", "Book 1:"]
    return not answer or any(marker in answer for marker in bad_markers)


def _generate_llm_answer(query: str, context: str) -> str:
    prompt = f"""You are an expert book recommendation assistant.

User is looking for: {query}

Relevant Books Found:
{context}

Provide 2-3 book recommendations from above. For each:
- State the title and author
- Explain in 1-2 sentences why it matches their request
- Be enthusiastic but factual

Recommendations:"""

    response = _get_generator()(
        prompt,
        max_length=200,
        min_length=50,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
    )

    return response[0]["generated_text"].strip()


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


def _book_context(book) -> str:
    points = build_key_points_list(book)
    fields = [
        f"Title: {book.title}",
        f"Author: {normalize_author(book.author, book.title)}",
        f"Genre: {book.genre or 'General'}",
        f"Rating: {float(book.rating or 0):.1f}/5",
        f"Summary: {book.ai_summary or build_summary_text(book)}",
    ]

    if book.publish_year:
        fields.append(f"Published: {book.publish_year}")

    if points:
        fields.append("Key Points: " + " | ".join(points))

    return "\n".join(fields)


def _fallback_book_answer(book, question: str) -> str:
    question_lower = question.lower()
    summary = book.ai_summary or build_summary_text(book)
    points = build_key_points_list(book)
    author = normalize_author(book.author, book.title)

    # Question-specific logic
    if any(term in question_lower for term in ["summary", "about", "tell me", "what is"]):
        return summary

    if any(term in question_lower for term in ["lesson", "key", "point", "takeaway", "learn"]):
        if points:
            return "Key points: " + " | ".join(points[:3])
        return summary

    if any(term in question_lower for term in ["author", "who wrote", "writer", "creator"]):
        return f"{book.title} is written by {author}."

    if any(term in question_lower for term in ["rating", "review", "good", "recommend"]):
        rating = float(book.rating or 0)
        if rating >= 4.5:
            return f"{book.title} is highly rated at {rating:.1f}/5. Highly recommended by readers."
        elif rating >= 4.0:
            return f"{book.title} has a strong rating of {rating:.1f}/5. Well-received by readers."
        else:
            return f"{book.title} has a rating of {rating:.1f}/5."

    if any(term in question_lower for term in ["genre", "type", "category"]):
        return f"{book.title} is a {book.genre or 'General'} book. {summary}"

    if any(term in question_lower for term in ["year", "when", "publish"]):
        if book.publish_year:
            return f"{book.title} was published in {book.publish_year}."
        return "Publication year information is not available."

    return summary


def generate_book_answer(book, question: str) -> str:
    question = question.strip()
    if not question:
        return "Ask a question about the selected book."

    fallback_answer = _fallback_book_answer(book, question)

    if os.getenv("USE_LLM_ANSWER") != "1":
        return fallback_answer

    prompt = f"""Answer this question about a book using only the provided information.

Book: {book.title} by {normalize_author(book.author, book.title)}
Genre: {book.genre or 'General'}
Rating: {float(book.rating or 0):.1f}/5
Summary: {book.ai_summary or build_summary_text(book)}

Question: {question}

Answer (2-3 sentences, factual, helpful):"""

    answer = _get_generator()(
        prompt,
        max_length=120,
        min_length=20,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7,
    )[0]["generated_text"].strip()

    return fallback_answer if _looks_like_bad_generation(answer) else answer
