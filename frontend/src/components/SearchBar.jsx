import { Search } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getBookSuggestions } from "../api.js";

export default function SearchBar({ initialValue = "", compact = false, inputId = "book-search-input" }) {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const requestId = useRef(0);
  const navigate = useNavigate();

  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 3) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const currentRequest = ++requestId.current;
    const timer = window.setTimeout(() => {
      getBookSuggestions({ query: trimmed, limit: 6 })
        .then((data) => {
          if (currentRequest !== requestId.current) return;
          setSuggestions(data.suggestions || []);
          setIsOpen(true);
        })
        .catch(() => {
          if (currentRequest === requestId.current) {
            setSuggestions([]);
            setIsOpen(false);
          }
        });
    }, 180);

    return () => window.clearTimeout(timer);
  }, [query]);

  function handleSubmit(event) {
    event.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    }
  }

  function selectSuggestion(book) {
    setIsOpen(false);
    navigate(`/book/${book.id}`);
  }

  return (
    <div className="relative">
      <form
        onSubmit={handleSubmit}
        className={`flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 shadow-sm transition-all duration-300 focus-within:border-teal-500 focus-within:ring-4 focus-within:ring-teal-500/10 focus-within:shadow-lg hover:border-gray-300 dark:border-gray-700 dark:bg-[#1a1a1a] dark:focus-within:border-teal-300 ${
          compact ? "h-10" : "h-12"
        }`}
      >
        <Search className="h-4 w-4 text-gray-400 dark:text-gray-500" />
        <input
          id={inputId}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onFocus={() => query.trim().length >= 3 && setIsOpen(true)}
          className="w-full bg-transparent text-sm font-medium text-gray-900 outline-none placeholder:text-gray-400 dark:text-gray-100 dark:placeholder:text-gray-500"
          placeholder={compact ? "Search books..." : "Search for books, authors, genres..."}
        />
      </form>

      {isOpen && suggestions.length > 0 ? (
        <div className="absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl shadow-slate-900/5 dark:border-white/10 dark:bg-[#1a1a1a]">
          {suggestions.map((book) => (
            <button
              key={book.id}
              type="button"
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => selectSuggestion(book)}
              className="flex w-full items-center gap-4 px-4 py-3 text-left transition hover:bg-slate-50 dark:hover:bg-white/5"
            >
              <img src={book.image} alt="" className="h-14 w-10 rounded-md object-cover shadow-sm" />
              <span className="min-w-0">
                <span className="block truncate text-sm font-semibold text-slate-900 dark:text-white">{book.title}</span>
                <span className="block truncate text-xs text-slate-500 dark:text-slate-400 mt-0.5">{book.author}</span>
              </span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
