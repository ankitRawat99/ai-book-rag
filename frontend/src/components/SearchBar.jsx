import { Search } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SearchBar({ initialValue = "", compact = false }) {
  const [query, setQuery] = useState(initialValue);
  const navigate = useNavigate();

  function handleSubmit(event) {
    event.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] px-4 shadow-sm transition-all duration-300 focus-within:border-gray-400 dark:focus-within:border-gray-500 focus-within:ring-4 focus-within:ring-gray-100 dark:focus-within:ring-gray-800 focus-within:shadow-lg hover:border-gray-300 dark:hover:border-gray-600 ${
        compact ? "h-10" : "h-12"
      }`}
    >
      <Search className="h-4 w-4 text-gray-400 dark:text-gray-500" />
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        className="w-full bg-transparent text-sm outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500 font-medium text-gray-900 dark:text-gray-100"
        placeholder={compact ? "Search books..." : "Search for books, authors, genres..."}
      />
    </form>
  );
}
