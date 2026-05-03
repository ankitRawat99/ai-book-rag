from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from services.data_quality import (
    clean_rating,
    fetch_open_library_metadata,
    normalize_author,
    normalize_image_url,
)

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
SITE_URL = "https://books.toscrape.com/catalogue/"
GENRES = ["Sci-Fi", "Self Help", "Business", "Romance", "Fantasy"]

RATING_MAP = {
    "One": 1.0,
    "Two": 2.0,
    "Three": 3.0,
    "Four": 4.0,
    "Five": 5.0,
}


def _extract_rating(item):
    rating_tag = item.select_one(".star-rating")
    if not rating_tag:
        return 0.0

    for class_name in rating_tag.get("class", []):
        if class_name in RATING_MAP:
            return RATING_MAP[class_name]

    return 0.0


def _extract_description(detail_soup):
    """Extract book description with fallback strategies"""
    # Try product description first
    description_heading = detail_soup.select_one("#product_description")
    if description_heading:
        description = description_heading.find_next_sibling("p")
        if description:
            text = description.get_text(strip=True)
            if len(text) > 50:  # Ensure substantial content
                return text
    
    # Fallback: try any paragraph in product description area
    product_desc = detail_soup.select(".product_page p")
    for p in product_desc:
        text = p.get_text(strip=True)
        if len(text) > 50 and "product description" not in text.lower():
            return text
    
    return ""


def scrape_books(pages=5, include_details=True):
    books = []

    for page in range(1, pages + 1):
        url = BASE_URL.format(page)
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            continue
            
        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup.select(".product_pod"):
            title = item.h3.a["title"]
            link = item.h3.a["href"]
            rating = _extract_rating(item)
            book_url = urljoin(SITE_URL, link)
            
            # Extract and normalize image URL
            image_tag = item.select_one("img")
            image = urljoin(SITE_URL, image_tag["src"]) if image_tag else ""
            
            genre = GENRES[(len(books) + page) % len(GENRES)]

            description = ""
            if include_details:
                try:
                    detail_res = requests.get(book_url, timeout=20)
                    detail_res.raise_for_status()
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    description = _extract_description(detail_soup)
                except requests.RequestException:
                    pass  # Continue without description

            # Fetch Open Library metadata for better author and high-res image
            metadata = fetch_open_library_metadata(title)
            author = normalize_author(metadata.get("author"), title)
            
            # Prefer Open Library high-res image, fallback to scraped image
            final_image = metadata.get("image") or image
            final_image = normalize_image_url(final_image, book_url, title)

            books.append(
                {
                    "title": title,
                    "author": author,
                    "description": description or "No description available",
                    "rating": clean_rating(rating, title, author),
                    "url": book_url,
                    "image": final_image,
                    "publish_year": metadata.get("publish_year"),
                    "genre": genre,
                }
            )

    return books
