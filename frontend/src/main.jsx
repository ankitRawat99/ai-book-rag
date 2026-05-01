import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BookOpen,
  Bot,
  ExternalLink,
  Library,
  Loader2,
  Search,
  Send,
  Star,
} from "lucide-react";
import "./styles.css";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

function getRatingLabel(rating) {
  const numericRating = Number(rating || 0);
  return Number.isFinite(numericRating) ? numericRating.toFixed(1) : "0.0";
}

function App() {
  const [books, setBooks] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [suggestionMeta, setSuggestionMeta] = useState({
    total: 0,
    limit: 10,
    offset: 0,
    hasMore: false,
  });
  const [apiStatus, setApiStatus] = useState("checking");
  const [bookError, setBookError] = useState("");
  const [isLoadingBooks, setIsLoadingBooks] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [askQuery, setAskQuery] = useState("recommend books about travel and adventure");
  const [answer, setAnswer] = useState("");
  const [askError, setAskError] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    async function loadBooks() {
      try {
        const response = await fetch(`${API_BASE}/books`);
        if (!response.ok) {
          throw new Error("Unable to load books");
        }
        const data = await response.json();
        setBooks(data);
        setApiStatus("connected");
      } catch (error) {
        setBookError(error.message);
        setApiStatus("offline");
      } finally {
        setIsLoadingBooks(false);
      }
    }

    loadBooks();
  }, []);

  const filteredBooks = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return books;
    }

    return books.filter((book) => {
      return `${book.title} ${book.author} ${book.description}`
        .toLowerCase()
        .includes(query);
    });
  }, [books, searchQuery]);

  const topRatedCount = useMemo(() => {
    return books.filter((book) => Number(book.rating) >= 4).length;
  }, [books]);

  async function loadSuggestions(query, nextOffset = 0) {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setSuggestions([]);
      setSuggestionMeta({
        total: 0,
        limit: 10,
        offset: 0,
        hasMore: false,
      });
      return;
    }

    if (nextOffset === 0) {
      setIsLoadingBooks(true);
    } else {
      setIsLoadingMore(true);
    }
    setBookError("");

    try {
      const params = new URLSearchParams({
        query: trimmedQuery,
        limit: "10",
        offset: String(nextOffset),
      });
      const response = await fetch(`${API_BASE}/suggestions?${params.toString()}`);
      if (!response.ok) {
        throw new Error("Unable to fetch suggestions");
      }
      const data = await response.json();
      setSuggestions((current) =>
        nextOffset === 0 ? data.suggestions : [...current, ...data.suggestions],
      );
      setSuggestionMeta({
        total: data.total,
        limit: data.limit,
        offset: data.offset,
        hasMore: data.has_more,
      });
      setApiStatus("connected");
    } catch (error) {
      setBookError(error.message);
      setApiStatus("offline");
    } finally {
      setIsLoadingBooks(false);
      setIsLoadingMore(false);
    }
  }

  useEffect(() => {
    const handle = window.setTimeout(() => {
      loadSuggestions(searchQuery, 0);
    }, 350);

    return () => window.clearTimeout(handle);
  }, [searchQuery]);

  async function handleAsk(event) {
    event.preventDefault();

    const query = askQuery.trim();
    if (!query) {
      return;
    }

    setIsAsking(true);
    setAskError("");
    setAnswer("");

    try {
      const params = new URLSearchParams({ query });
      const response = await fetch(`${API_BASE}/ask?${params.toString()}`);
      if (!response.ok) {
        throw new Error("Unable to generate an answer");
      }
      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      setAskError(error.message);
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI Book RAG</p>
          <h1>Book Recommendation Assistant</h1>
        </div>
        <div className={`api-status ${apiStatus === "offline" ? "offline" : ""}`}>
          <span />
          {apiStatus === "connected"
            ? "FastAPI connected"
            : apiStatus === "offline"
              ? "FastAPI offline"
              : "Checking API"}
        </div>
      </header>

      <section className="stats-grid" aria-label="Library summary">
        <div className="stat">
          <Library size={22} />
          <div>
            <span>{books.length}</span>
            <p>Total books</p>
          </div>
        </div>
        <div className="stat">
          <Star size={22} />
          <div>
            <span>{topRatedCount}</span>
            <p>Rated 4+</p>
          </div>
        </div>
        <div className="stat">
          <Bot size={22} />
          <div>
            <span>{answer ? "Ready" : "Ask"}</span>
            <p>RAG assistant</p>
          </div>
        </div>
      </section>

      <section className="workspace">
        <div className="assistant-panel">
          <div className="panel-heading">
            <Bot size={22} />
            <div>
              <h2>Ask for recommendations</h2>
              <p>Searches the vector index and returns ranked book choices.</p>
            </div>
          </div>

          <form className="ask-form" onSubmit={handleAsk}>
            <textarea
              value={askQuery}
              onChange={(event) => setAskQuery(event.target.value)}
              rows={4}
              placeholder="Ask for books about productivity, psychology, travel..."
            />
            <button type="submit" disabled={isAsking}>
              {isAsking ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
              {isAsking ? "Thinking" : "Ask"}
            </button>
          </form>

          {askError && <div className="error">{askError}</div>}
          {answer && (
            <div className="answer">
              {answer.split("\n").map((line) => (
                <p key={line}>{line}</p>
              ))}
            </div>
          )}
        </div>

        <div className="library-panel">
          <div className="panel-heading library-heading">
            <div>
              <h2>Library</h2>
              <p>
                {searchQuery.trim()
                  ? `${suggestionMeta.total} relevant matches`
                  : `${filteredBooks.length} visible books`}
              </p>
            </div>
            <div className="search-box">
              <Search size={18} />
              <input
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Filter books"
              />
            </div>
          </div>

          {bookError && <div className="error">{bookError}</div>}
          {isLoadingBooks ? (
            <div className="loading">
              <Loader2 className="spin" size={20} />
              Loading library
            </div>
          ) : (
            <div className="book-list">
              {(searchQuery.trim() ? suggestions : filteredBooks.slice(0, 80)).map((book) => (
                <article className="book-card" key={book.id}>
                  <div className="book-icon">
                    <BookOpen size={20} />
                  </div>
                  <div className="book-content">
                    <h3>{book.title}</h3>
                    <div className="book-meta">
                      <span>{book.author === "Unknown" ? "Author unavailable" : book.author}</span>
                      <span>{getRatingLabel(book.rating)} / 5</span>
                      {book.match_type && <span>{book.match_type}</span>}
                    </div>
                    <p>{book.reason || book.description}</p>
                  </div>
                  {book.url && (
                    <a className="icon-link" href={book.url} target="_blank" rel="noreferrer">
                      <ExternalLink size={18} />
                    </a>
                  )}
                </article>
              ))}
              {searchQuery.trim() && suggestionMeta.hasMore && (
                <button
                  className="load-more"
                  type="button"
                  disabled={isLoadingMore}
                  onClick={() => loadSuggestions(searchQuery, suggestions.length)}
                >
                  {isLoadingMore ? <Loader2 className="spin" size={18} /> : <Search size={18} />}
                  More suggestions
                </button>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
