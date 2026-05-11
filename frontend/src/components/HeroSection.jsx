import { useEffect, useState } from "react";
import { getBooks } from "../api.js";
import VerticalCarousel from "./VerticalCarousel.jsx";

export default function HeroSection() {
  const [carouselBooks, setCarouselBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

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
      {/* Floating particle dots backdrop */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
        {[...Array(8)].map((_, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-teal-400/20 dark:bg-teal-400/10"
            style={{
              width: `${12 + i * 8}px`,
              height: `${12 + i * 8}px`,
              top: `${10 + (i * 11) % 80}%`,
              left: `${5 + (i * 17) % 90}%`,
              animation: `float-orb ${8 + i * 1.5}s ease-in-out infinite alternate`,
              animationDelay: `${i * 0.7}s`,
            }}
          />
        ))}
      </div>

      <div className="w-full px-5 sm:px-8 md:px-10 relative py-12 lg:py-16">
        <div className="grid items-center gap-8 lg:grid-cols-[minmax(0,1fr)_520px] lg:gap-6">
          <div className="flex flex-col justify-center py-8 section-enter">
            <p className="mb-5 w-fit rounded-full border border-teal-500/30 bg-teal-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-teal-700 dark:text-teal-300">
              AI-powered reading discovery
            </p>
            <div className="space-y-4">
              <h1 className="hero-shimmer max-w-3xl text-6xl font-black leading-[1.05] tracking-tight sm:text-7xl lg:text-8xl">
                Discover your next
                <span className="block">favorite book</span>
              </h1>
            </div>

            <p className="mt-5 max-w-xl text-base leading-7 text-slate-500 dark:text-slate-400">
              Explore a richer book catalog with AI-powered recommendations, concise summaries, and semantic search.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <a
                href="/#books-grid"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:-translate-y-1 hover:shadow-xl hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-gray-100"
              >
                Browse Books
              </a>
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
