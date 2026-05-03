export const API_BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

export function getBooks({ genre = "", limit = 40, offset = 0 } = {}) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (genre) {
    params.set("genre", genre);
  }

  return request(`/books?${params.toString()}`);
}

export function getBook(id) {
  return request(`/book/${id}`);
}

export function getGenres() {
  return request("/genres");
}

export function searchBooks({ query, limit = 12, offset = 0 }) {
  const params = new URLSearchParams({
    query,
    limit: String(limit),
    offset: String(offset),
  });

  return request(`/search?${params.toString()}`);
}

export function askBook({ bookId, question }) {
  return request("/ask-book", {
    method: "POST",
    body: JSON.stringify({ book_id: Number(bookId), question }),
  });
}
