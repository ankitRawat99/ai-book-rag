import hashlib
import json
import re
from html import escape
from urllib.parse import quote, quote_plus, urljoin
from urllib.request import Request, urlopen

UNKNOWN_AUTHOR_VALUES = {"", "unknown", "author unavailable", "n/a", "none"}
BAD_DESCRIPTION_VALUES = {"", "scraped book", "no description available"}


def fallback_cover(title: str | None = None) -> str:
    label = escape((title or "Book Cover")[:34])
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='320' height='480'>"
        f"<rect fill='#e2e8f0' width='320' height='480'/>"
        f"<text x='50%' y='47%' text-anchor='middle' fill='#334155' "
        f"font-size='22' font-weight='700'>{label}</text>"
        f"<text x='50%' y='56%' text-anchor='middle' fill='#64758b' "
        f"font-size='14'>No Cover</text></svg>"
    )
    return f"data:image/svg+xml,{quote(svg)}"


def normalize_author(author: str | None, title: str | None = None) -> str:
    value = (author or "").strip()
    if value.lower() in UNKNOWN_AUTHOR_VALUES:
        return "Unknown author"

    parts = []
    for part in re.split(r",|;|\band\b", value):
        cleaned = part.strip()
        if cleaned and cleaned not in parts:
            parts.append(cleaned)

    return ", ".join(parts[:3]) if parts else "Author unavailable"


def normalize_image_url(image: str | None, source_url: str | None = None, title: str | None = None) -> str:
    value = (image or "").strip()
    if not value:
        return fallback_cover(title)

    if value.startswith("data:image"):
        return value

    if value.startswith("//"):
        return f"https:{value}"

    if value.startswith(("http://", "https://")):
        return value

    if source_url:
        return urljoin(source_url, value)

    return fallback_cover(title)


def estimate_rating(title: str | None, author: str | None = None) -> float:
    seed = f"{title or ''}|{author or ''}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return round(3.5 + bucket, 1)


def clean_rating(rating: float | int | None, title: str | None, author: str | None = None) -> float:
    try:
        value = float(rating or 0)
    except (TypeError, ValueError):
        value = 0.0

    if value <= 0:
        return estimate_rating(title, author)

    return round(max(1.0, min(value, 5.0)), 1)


def build_summary_text(book) -> str:
    description = (getattr(book, "description", None) or "").strip()
    
    # If we have a good description, use it
    if description and description.lower() not in BAD_DESCRIPTION_VALUES:
        # Limit length and ensure quality
        summary = description[:500].strip()
        if len(summary) > 100:  # Only use if substantial
            return summary
    
    # Generate meaningful summary from metadata
    title = getattr(book, "title", "This book")
    author = normalize_author(getattr(book, "author", None), title)
    genre = getattr(book, "genre", None) or "General"
    publish_year = getattr(book, "publish_year", None)
    rating = getattr(book, "rating", None)
    
    # Create a more engaging summary
    summary_parts = []
    
    # Main hook
    if publish_year:
        summary_parts.append(f"Published in {publish_year}, {title} by {author} is a compelling {genre.lower()} work.")
    else:
        summary_parts.append(f"{title} by {author} is a notable contribution to {genre.lower()} literature.")
    
    # Add quality indicator
    if rating and rating >= 4.0:
        summary_parts.append(f"Highly regarded by readers with a {rating:.1f}/5 rating,")
    elif rating and rating >= 3.5:
        summary_parts.append(f"Well-received with a {rating:.1f}/5 rating,")
    
    # Add genre context
    genre_context = {
        "Sci-Fi": "this work explores imaginative futures and technological possibilities.",
        "Self Help": "this book offers practical insights and actionable strategies.",
        "Business": "this book provides valuable business wisdom and entrepreneurial insights.",
        "Romance": "this story delves into compelling relationships and emotional connections.",
        "Fantasy": "this epic tale creates immersive worlds and memorable adventures.",
        "History": "this work brings historical events and figures to life.",
        "Biography": "this narrative reveals the life and achievements of remarkable individuals.",
        "Science": "this book explores scientific concepts and natural phenomena.",
        "Mystery": "this story weaves together clues and suspenseful revelations.",
        "Travel": "this work captures cultures and destinations around the globe.",
    }
    
    context = genre_context.get(genre, f"this book explores {genre.lower()} themes in depth.")
    summary_parts.append(context)
    
    # Add audience
    summary_parts.append(f"Perfect for readers interested in {genre.lower()} and seeking engaging, quality content.")
    
    return " ".join(summary_parts)


def build_key_points_list(book) -> list[str]:
    title = getattr(book, "title", "This book")
    genre = getattr(book, "genre", None) or "General"
    author = normalize_author(getattr(book, "author", None), title)
    publish_year = getattr(book, "publish_year", None)
    rating = getattr(book, "rating", None)
    description = (getattr(book, "description", None) or "").strip()
    
    points = []
    
    # Author info
    if author != "Unknown author" and author != "Author unavailable":
        points.append(f"Written by {author}")
    
    # Genre classification
    points.append(f"Genre: {genre}")
    
    # Publication info
    if publish_year:
        points.append(f"Published: {publish_year}")
    
    # Rating/Quality
    if rating:
        rating_float = float(rating)
        if rating_float >= 4.5:
            points.append(f"Highly Rated: {rating_float:.1f}/5 - Exceptional quality")
        elif rating_float >= 4.0:
            points.append(f"Well Received: {rating_float:.1f}/5 - Strong reader approval")
        elif rating_float >= 3.5:
            points.append(f"Good Rating: {rating_float:.1f}/5 - Worth reading")
        else:
            points.append(f"Rating: {rating_float:.1f}/5")
    
    # Key insight from description if available
    if description and description.lower() not in BAD_DESCRIPTION_VALUES:
        # Extract first meaningful sentence
        sentences = [s.strip() for s in description.split('.') if s.strip()]
        if sentences:
            first_sentence = sentences[0]
            if len(first_sentence) > 20 and len(first_sentence) < 150:
                points.append(f"Summary: {first_sentence}")
    
    # Genre-specific insights
    genre_insights = {
        "Sci-Fi": "Explores futuristic themes and imaginative worlds",
        "Self Help": "Offers practical strategies for personal growth",
        "Business": "Provides entrepreneurial wisdom and business insights",
        "Romance": "Features compelling emotional and relational narratives",
        "Fantasy": "Contains rich worldbuilding and epic storytelling",
        "History": "Documents historical events and periods",
        "Biography": "Chronicles a remarkable life or achievement",
        "Science": "Explains scientific concepts and discoveries",
        "Mystery": "Delivers suspenseful, plot-driven narrative",
        "Travel": "Captures global cultures and destinations",
    }
    
    if genre in genre_insights and len(points) < 5:
        points.append(genre_insights[genre])
    
    return points[:5]


def load_key_points(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        points = json.loads(value)
    except json.JSONDecodeError:
        return []

    return [str(point) for point in points if str(point).strip()]


def dump_key_points(points: list[str]) -> str:
    return json.dumps(points, ensure_ascii=True)


def fetch_open_library_metadata(title: str, author: str | None = None) -> dict:
    query = quote_plus(f"{title} {author or ''}".strip())
    request = Request(
        f"https://openlibrary.org/search.json?q={query}&limit=3",
        headers={"User-Agent": "ai-book-rag metadata enrichment"},
    )

    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}

    docs = payload.get("docs") or []
    if not docs:
        return {}

    # Try to find best match
    doc = docs[0]
    for d in docs:
        # Prefer exact title match
        if d.get("title", "").lower() == title.lower():
            doc = d
            break
    
    cover_id = doc.get("cover_i")
    metadata = {
        "author": ", ".join((doc.get("author_name") or [])[:3]),
        "publish_year": doc.get("first_publish_year"),
    }
    
    # Fetch high-resolution cover image
    if cover_id:
        # Use -L suffix for large (high-res) images
        metadata["image"] = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    
    return {key: value for key, value in metadata.items() if value}
