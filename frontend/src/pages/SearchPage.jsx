import { Loader2, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { searchBooks } from "../api.js";
import BookCard from "../components/BookCard.jsx";
import SearchBar from "../components/SearchBar.jsx";
import SkeletonGrid from "../components/SkeletonGrid.jsx";

export default function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [books, setBooks] = useState([]);
  const [meta, setMeta] = useState({ total: 0, hasMore: false });
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  async function loadResults(nextOffset = 0) {
    if (!query) {
      setBooks([]);
      return;
    }

    if (nextOffset === 0) {
      setIsLoading(true);
    } else {
      setIsLoadingMore(true);
    }

    try {
      const data = await searchBooks({ query, limit: 12, offset: nextOffset });
      setBooks((current) =>
        nextOffset === 0 ? data.suggestions : [...current, ...data.suggestions],
      );
      setMeta({ total: data.total, hasMore: data.has_more });
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }

  useEffect(() => {
    loadResults(0);
  }, [query]);

  return (
    <main className="min-h-screen bg-white dark:bg-[#1a1a1a] transition-colors">
      <section className="bg-gradient-to-b from-gray-50 to-white dark:from-[#0d0d0d] dark:to-[#1a1a1a] border-b border-gray-200 dark:border-gray-800">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:px-8 lg:px-10">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-gray-100 dark:bg-gray-800 px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
              <Search className="h-4 w-4" />
              AI-Powered Search
            </div>
            
            <h1 className="text-4xl font-black sm:text-5xl text-gray-900 dark:text-gray-100">
              Search with natural language
            </h1>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Try "books about habits", "suggest sci-fi books", or a specific title.
            </p>
            
            <div className="mt-8">
              <SearchBar initialValue={query} />
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-12 sm:px-8 lg:px-10">
        <div className="mb-8 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-black text-gray-900 dark:text-gray-100">Search Results</h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {query ? (
                isLoading ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Searching...
                  </span>
                ) : (
                  <>
                    Found <span className="font-bold text-gray-900 dark:text-gray-100">{meta.total}</span> relevant matches for "{query}"
                  </>
                )
              ) : (
                "Enter a query to begin"
              )}
            </p>
          </div>
          <Search className="hidden h-8 w-8 text-gray-300 dark:text-gray-600 sm:block" />
        </div>

        {isLoading ? (
          <SkeletonGrid count={12} />
        ) : books.length === 0 && query ? (
          <div className="rounded-2xl border-2 border-dashed border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] p-16 text-center">
            <Search className="mx-auto h-16 w-16 text-gray-300 dark:text-gray-600" />
            <h3 className="mt-4 text-xl font-bold text-gray-900 dark:text-gray-100">No books found</h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">Try a different search term or browse our collection</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-6 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
            {meta.hasMore ? (
              <div className="mt-12 flex justify-center">
                <button
                  onClick={() => loadResults(books.length)}
                  disabled={isLoadingMore}
                  className="inline-flex items-center gap-3 rounded-xl bg-gray-900 dark:bg-gray-100 px-8 py-4 text-sm font-bold text-white dark:text-gray-900 shadow-lg transition hover:shadow-xl disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {isLoadingMore ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    "Load More Results"
                  )}
                </button>
              </div>
            ) : null}
          </>
        )}
      </section>
    </main>
  );
}
