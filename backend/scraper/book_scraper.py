from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
SITE_URL = "https://books.toscrape.com/catalogue/"

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
    description_heading = detail_soup.select_one("#product_description")
    if not description_heading:
        return ""

    description = description_heading.find_next_sibling("p")
    return description.get_text(strip=True) if description else ""


def scrape_books(pages=5, include_details=True):
    books = []

    for page in range(1, pages + 1):
        url = BASE_URL.format(page)
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup.select(".product_pod"):
            title = item.h3.a["title"]
            link = item.h3.a["href"]
            rating = _extract_rating(item)
            book_url = urljoin(SITE_URL, link)

            description = ""
            if include_details:
                detail_res = requests.get(book_url, timeout=20)
                detail_res.raise_for_status()
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                description = _extract_description(detail_soup)

            books.append(
                {
                    "title": title,
                    "author": "Unknown",
                    "description": description or "No description available",
                    "rating": rating,
                    "url": book_url,
                }
            )

    return books
