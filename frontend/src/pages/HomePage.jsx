import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getBooks, getGenres } from "../api.js";
import BookCard from "../components/BookCard.jsx";
import CategoryCarousel from "../components/CategoryCarousel.jsx";
import HeroSection from "../components/HeroSection.jsx";
import SkeletonGrid from "../components/SkeletonGrid.jsx";
import { Loader2 } from "lucide-react";

const preferredGenres = ["Sci-Fi", "Self Help", "Business", "Romance", "Fantasy"];
const BOOKS_PER_PAGE = 16;

export default function HomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedGenre = searchParams.get("genre") || "";
  const [books, setBooks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    setIsLoading(true);
    setOffset(0);
    setHasMore(true);
    Promise.all([
      getBooks({ genre: selectedGenre, limit: BOOKS_PER_PAGE, offset: 0 }),
      getGenres(),
    ])
      .then(([bookData, genreData]) => {
        setBooks(bookData);
        setGenres(genreData);
        setHasMore(bookData.length === BOOKS_PER_PAGE);
        bookData.slice(0, 8).forEach(book => {
          const img = new Image();
          img.src = book.image;
        });
      })
      .finally(() => setIsLoading(false));
  }, [selectedGenre]);

  const loadMore = async () => {
    setIsLoadingMore(true);
    const nextOffset = offset + BOOKS_PER_PAGE;
    try {
      const moreBooks = await getBooks({ genre: selectedGenre, limit: BOOKS_PER_PAGE, offset: nextOffset });
      setBooks(prev => [...prev, ...moreBooks]);
      setOffset(nextOffset);
      setHasMore(moreBooks.length === BOOKS_PER_PAGE);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const categoryList = useMemo(() => {
    const merged = [...preferredGenres, ...genres];
    return [...new Set(merged)].slice(0, 12);
  }, [genres]);

  return (
    <>
      <HeroSection />
      <main className="mx-auto max-w-6xl px-5 py-6 sm:px-7 lg:px-8" id="books-grid">

      <section className="rounded-2xl border border-slate-200/80 bg-white/80 p-5 shadow-sm backdrop-blur dark:border-white/10 dark:bg-[#121212]/80 sm:p-6">
        <div className="mb-5 flex items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Explore categories
            </p>
            <h2 className="mt-1 text-2xl font-black text-slate-950 dark:text-white">Genres</h2>
          </div>
          {selectedGenre ? (
            <button
              onClick={() => setSearchParams({})}
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-400 hover:text-slate-950 dark:border-white/10 dark:bg-white/[0.06] dark:text-slate-300 dark:hover:border-white/25 dark:hover:text-white"
            >
              Clear filter
            </button>
          ) : null}
        </div>
        <CategoryCarousel
          genres={categoryList}
          selectedGenre={selectedGenre}
          onSelect={(genre) => setSearchParams({ genre })}
        />
      </section>

      <section className="mt-6 rounded-2xl border border-slate-200/80 bg-white/80 p-5 shadow-sm backdrop-blur dark:border-white/10 dark:bg-[#121212]/80 sm:p-6">
        <div className="mb-5">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            {selectedGenre || "Recommended"}
          </p>
          <h2 className="mt-1 text-2xl font-black text-slate-950 dark:text-white">Books Collection</h2>
        </div>

        {isLoading ? (
          <SkeletonGrid count={8} />
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
            
            {hasMore && (
              <div className="mt-8 flex justify-center">
                <button
                  onClick={loadMore}
                  disabled={isLoadingMore}
                  className="inline-flex items-center gap-3 rounded-lg bg-slate-950 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-slate-950/10 transition hover:-translate-y-0.5 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-70 dark:bg-white dark:text-slate-950"
                >
                  {isLoadingMore ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    "Load More Books"
                  )}
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </main>
    </>
  );
}
