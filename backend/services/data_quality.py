import hashlib
import json
import re
from html import escape
from urllib.parse import quote, quote_plus, urljoin
from urllib.request import Request, urlopen

UNKNOWN_AUTHOR_VALUES = {"", "unknown", "author unavailable", "n/a", "none"}
BAD_DESCRIPTION_VALUES = {"", "scraped book", "no description available"}
LOW_QUALITY_SUMMARY_MARKERS = (
    "compelling ",
    "notable contribution",
    "perfect for readers interested",
    "quality content",
    "this book explores general themes",
)

KNOWN_BOOK_INSIGHTS = {
    "atomic habits": [
        "shows how tiny behavior changes compound into large results over time",
        "argues that environment design often beats willpower",
        "centers habit change on identity: become the kind of person who does the action",
    ],
    "pride and prejudice": [
        "follows Elizabeth Bennet as she judges status, manners, and character in Regency England",
        "uses romance to examine pride, class pressure, family ambition, and first impressions",
        "contrasts social performance with the slower work of understanding people clearly",
    ],
    "alice's adventures in wonderland": [
        "sends Alice through a dreamlike world where logic, language, and authority keep shifting",
        "turns childhood curiosity into encounters with absurd rules and comic disorder",
        "uses fantasy to question how adults make meaning, manners, and power feel arbitrary",
    ],
    "a christmas carol": [
        "follows Ebenezer Scrooge as three spirits force him to confront greed, memory, and mortality",
        "argues that generosity and social responsibility can remake a life",
        "connects personal redemption with compassion for poverty and family hardship",
    ],
    "the great gatsby": [
        "tracks Jay Gatsby's reinvention and obsession with Daisy Buchanan",
        "shows how wealth, longing, and performance distort the American dream",
        "contrasts glittering parties with loneliness, carelessness, and moral emptiness",
    ],
    "to kill a mockingbird": [
        "uses Scout Finch's childhood view to reveal racism and injustice in a Southern town",
        "centers Atticus Finch's defense of Tom Robinson as a lesson in conscience under pressure",
        "connects empathy with the difficulty of doing what is right in public",
    ],
    "1984": [
        "imagines a surveillance state that controls language, memory, and private thought",
        "follows Winston Smith's attempt to preserve truth and desire under totalitarian power",
        "warns that political control becomes absolute when reality itself can be rewritten",
    ],
}

GENRE_INSIGHTS = {
    "Sci-Fi": [
        "explores how imagined futures expose present-day questions about power, technology, and human choice",
        "uses speculative settings to test what people value when society changes",
    ],
    "Self Help": [
        "focuses on practical behavior change rather than abstract motivation",
        "turns personal growth into repeatable actions readers can apply",
    ],
    "Business": [
        "connects decisions, leadership, and execution to real organizational outcomes",
        "offers frameworks for thinking about work, markets, and management",
    ],
    "Romance": [
        "builds emotional tension through character choices, trust, and vulnerability",
        "uses relationships to explore identity, timing, and personal change",
    ],
    "Fantasy": [
        "uses invented worlds to make conflict, loyalty, and transformation feel larger than ordinary life",
        "leans on worldbuilding and quests to test character under pressure",
    ],
    "History": [
        "places people and events in context so causes and consequences are easier to understand",
        "shows how political, cultural, and personal forces shape the past",
    ],
    "Biography": [
        "examines a life through choices, setbacks, influence, and legacy",
        "helps readers understand the person behind the public record",
    ],
    "Mystery": [
        "builds suspense through clues, withheld information, and shifting suspicion",
        "rewards close attention to motive, evidence, and character behavior",
    ],
}


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


def is_low_quality_summary(summary: str | None) -> bool:
    value = (summary or "").strip().lower()
    return not value or any(marker in value for marker in LOW_QUALITY_SUMMARY_MARKERS)


def _usable_description(description: str | None) -> str:
    value = (description or "").strip()
    if not value or value.lower() in BAD_DESCRIPTION_VALUES:
        return ""

    lower = value.lower()
    if lower.startswith("open library subject:") and len(value) < 120:
        return ""

    return value


def _first_sentences(text: str, limit: int = 2) -> list[str]:
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
    return sentences[:limit]


def build_summary_text(book) -> str:
    description = _usable_description(getattr(book, "description", None))
    title = getattr(book, "title", "This book")
    author = normalize_author(getattr(book, "author", None), title)
    genre = getattr(book, "genre", None) or "General"
    
    known = KNOWN_BOOK_INSIGHTS.get((title or "").strip().lower())
    if known:
        return " ".join([
            f"{title} by {author} {known[0]}.",
            f"It {known[1]}.",
            f"Key idea: {known[2]}.",
        ])

    if description:
        sentences = _first_sentences(description, limit=3)
        if sentences:
            return " ".join(sentences)[:650].strip()
    
    publish_year = getattr(book, "publish_year", None)
    insights = GENRE_INSIGHTS.get(genre, [
        f"focuses on core {genre.lower()} ideas through its subject and structure",
        "gives readers a concise path into the book's themes and context",
    ])
    year = f" First published in {publish_year}," if publish_year else ""
    return (
        f"{year} {title} by {author} is best approached as a {genre.lower()} book that {insights[0]}. "
        f"It {insights[1]}. "
        "The available catalog data is limited, so this summary stays grounded in metadata rather than inventing plot details."
    ).strip()


def build_key_points_list(book) -> list[str]:
    title = getattr(book, "title", "This book")
    genre = getattr(book, "genre", None) or "General"
    author = normalize_author(getattr(book, "author", None), title)
    publish_year = getattr(book, "publish_year", None)
    rating = getattr(book, "rating", None)
    description = _usable_description(getattr(book, "description", None))
    
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
    
    known = KNOWN_BOOK_INSIGHTS.get((title or "").strip().lower())
    if known:
        points.extend(known)
        return points[:5]

    if description:
        for sentence in _first_sentences(description, limit=2):
            if 20 <= len(sentence) <= 180:
                points.append(sentence.rstrip("."))
    
    # Genre-specific insights
    if genre in GENRE_INSIGHTS and len(points) < 5:
        points.extend(GENRE_INSIGHTS[genre])
    
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
