import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getBookCount, getBooks, getGenres } from "../api.js";
import BookCard from "../components/BookCard.jsx";
import CategoryCarousel from "../components/CategoryCarousel.jsx";
import HeroSection from "../components/HeroSection.jsx";
import SkeletonGrid from "../components/SkeletonGrid.jsx";
import SearchBar from "../components/SearchBar.jsx";
import { ChevronLeft, ChevronRight } from "lucide-react";

const preferredGenres = ["Sci-Fi", "Self Help", "Business", "Romance", "Fantasy"];
const BOOKS_PER_PAGE = 24;

export default function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedGenre = searchParams.get("genre") || "";
  const [books, setBooks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalBooks, setTotalBooks] = useState(0);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
  }, [selectedGenre]);

  useEffect(() => {
    setIsLoading(true);
    const offset = (page - 1) * BOOKS_PER_PAGE;
    Promise.all([
      getBooks({ genre: selectedGenre, limit: BOOKS_PER_PAGE, offset }),
      getGenres(),
      getBookCount({ genre: selectedGenre }),
    ])
      .then(([bookData, genreData, countData]) => {
        setBooks(bookData);
        setGenres(genreData);
        setTotalBooks(countData.count || 0);
        bookData.slice(0, 8).forEach(book => {
          const img = new Image();
          img.src = book.image;
        });
        if (page > 1) {
          document.getElementById("books-grid")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      })
      .finally(() => setIsLoading(false));
  }, [selectedGenre, page]);

  const categoryList = useMemo(() => {
    const merged = [...preferredGenres, ...genres];
    return [...new Set(merged)].slice(0, 12);
  }, [genres]);

  const totalPages = Math.max(1, Math.ceil(totalBooks / BOOKS_PER_PAGE));
  const pagination = useMemo(() => {
    const pages = new Set([1, totalPages, page - 1, page, page + 1]);
    return [...pages].filter((item) => item >= 1 && item <= totalPages).sort((a, b) => a - b);
  }, [page, totalPages]);

  return (
    <>
      <HeroSection />
      <main className="w-full px-4 sm:px-6 md:px-8 py-8 space-y-8" id="books-grid">

      <section className="section-enter hover-lift rounded-xl border border-slate-200/80 bg-white/80 p-5 shadow-sm backdrop-blur dark:border-white/10 dark:bg-[#0e1118]/80 sm:p-6" style={{ animationDelay: '0.05s' }}>
        <div className="mb-5 flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-1">Explore categories</p>
            <h2 className="text-xl font-black text-slate-900 dark:text-white">Genres</h2>
          </div>
          {selectedGenre ? (
            <button
              onClick={() => setSearchParams({})}
              className="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-xs font-semibold text-slate-600 shadow-sm transition hover:border-slate-300 hover:text-slate-900 dark:border-white/10 dark:bg-white/5 dark:text-slate-300 dark:hover:border-white/20 dark:hover:text-white"
            >
              ✕ Clear filter
            </button>
          ) : null}
        </div>
        <CategoryCarousel
          genres={categoryList}
          selectedGenre={selectedGenre}
          onSelect={(genre) => setSearchParams({ genre })}
        />
      </section>

      <section className="section-enter hover-lift relative z-20 rounded-xl border border-slate-200/80 bg-white/80 p-4 shadow-sm backdrop-blur dark:border-white/10 dark:bg-[#0e1118]/80" style={{ animationDelay: '0.12s' }}>
        <SearchBar />
      </section>

      {/* Books section: overflow must be visible for 3D perspective to work */}
      <section
        className="section-enter rounded-xl border border-slate-200/80 bg-white/80 p-5 shadow-sm backdrop-blur dark:border-white/10 dark:bg-[#0e1118]/80 sm:p-6"
        style={{ animationDelay: '0.2s', overflow: 'visible' }}
      >
        <div className="mb-5 flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-1">
              {selectedGenre || "Recommended"}
            </p>
            <h2 className="text-xl font-black text-slate-900 dark:text-white">Books Collection</h2>
          </div>
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500">
            Page {page} of {totalPages} &middot; {totalBooks} books
          </p>
        </div>

        {isLoading ? (
          <SkeletonGrid count={12} />
        ) : (
          <>
            {/* overflow:visible lets 3D book spines extend outside grid cells */}
            <div
              className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6"
              style={{ gap: '20px 16px', overflow: 'visible' }}
            >
              {books.map((book, index) => (
                <div
                  key={book.id}
                  style={{
                    animationDelay: `${0.035 * index}s`,
                    overflow: 'visible',
                  }}
                >
                  <BookCard book={book} />
                </div>
              ))}
            </div>
            
            {totalPages > 1 ? (
              <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  disabled={page === 1 || isLoading}
                  className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-sm font-bold text-slate-700 transition hover:border-slate-400 disabled:cursor-not-allowed disabled:opacity-45 dark:border-white/10 dark:bg-white/[0.06] dark:text-slate-300"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </button>

                {pagination.map((pageNumber, index) => {
                  const previous = pagination[index - 1];
                  const showGap = previous && pageNumber - previous > 1;
                  return (
                    <span key={pageNumber} className="inline-flex items-center gap-2">
                      {showGap ? <span className="px-1 text-slate-400">...</span> : null}
                      <button
                        type="button"
                        onClick={() => setPage(pageNumber)}
                        className={`h-10 min-w-10 rounded-lg px-3 text-sm font-black transition ${
                          page === pageNumber
                            ? "bg-slate-950 text-white shadow-md dark:bg-white dark:text-slate-950"
                            : "border border-slate-200 bg-white text-slate-700 hover:border-slate-400 dark:border-white/10 dark:bg-white/[0.06] dark:text-slate-300"
                        }`}
                      >
                        {pageNumber}
                      </button>
                    </span>
                  );
                })}

                <button
                  type="button"
                  onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
                  disabled={page === totalPages || isLoading}
                  className="inline-flex h-10 items-center gap-2 rounded-lg bg-slate-950 px-4 text-sm font-bold text-white shadow-sm transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-45 dark:bg-white dark:text-slate-950"
                >
                  Next Page
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            ) : null}
          </>
        )}
      </section>
    </main>
    </>
  );
}
