import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getBooks } from "../api.js";
import VerticalCarousel from "./VerticalCarousel.jsx";

export default function HeroSection() {
  const [carouselBooks, setCarouselBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    setIsLoading(true);
    getBooks({ limit: 20 })
      .then((books) => {
        setCarouselBooks(books);
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section className="relative overflow-hidden border-b border-slate-200/70 bg-white/55 transition-colors dark:border-white/10 dark:bg-[#121212]/70">
      <div className="relative mx-auto max-w-6xl px-5 py-12 sm:px-7 lg:px-8 lg:py-14">
        <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_520px] lg:gap-12">
          <div className="flex flex-col justify-center py-8">
            <p className="mb-5 w-fit rounded-full border border-teal-500/20 bg-teal-500/10 px-4 py-2 text-sm font-semibold text-teal-800 dark:text-teal-200">
              AI-powered reading discovery
            </p>
            <div className="space-y-5">
              <h1 className="max-w-4xl text-5xl font-black leading-[1.12] tracking-normal text-slate-950 dark:text-white sm:text-6xl lg:text-7xl">
                Discover your next
                <span className="block text-slate-600 dark:text-slate-300">favorite book</span>
              </h1>
            </div>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300 sm:text-xl">
              Explore a richer book catalog with grounded recommendations, concise summaries, and semantic search that understands what you want to read next.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <a
                href="/#books-grid"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-950 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-slate-950/10 transition hover:-translate-y-0.5 hover:shadow-xl dark:bg-white dark:text-slate-950"
              >
                Browse Books
              </a>
              <button
                onClick={() => navigate("/search")}
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-7 py-3.5 text-sm font-bold text-slate-900 shadow-sm transition hover:border-slate-400 dark:border-white/10 dark:bg-white/[0.06] dark:text-white dark:hover:border-white/25"
              >
                <Search className="h-5 w-5" />
                Search
              </button>
            </div>
          </div>

          <div className="hidden lg:block">
            {isLoading ? (
              <div className="h-full flex items-center justify-center">
                <div className="animate-pulse">
                  <div className="h-96 w-64 bg-gray-200 dark:bg-gray-800 rounded-3xl mb-4"></div>
                </div>
              </div>
            ) : (
              <VerticalCarousel books={carouselBooks} />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
