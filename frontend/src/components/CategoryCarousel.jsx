import { useEffect, useRef, useState } from "react";

export default function CategoryCarousel({ genres = [], selectedGenre = "", onSelect }) {
  const [isPaused, setIsPaused] = useState(false);
  const pauseTimer = useRef(null);
  const visibleGenres = genres.filter(Boolean);
  const trackGenres = [...visibleGenres, ...visibleGenres, ...visibleGenres];

  useEffect(() => {
    return () => {
      if (pauseTimer.current) {
        window.clearTimeout(pauseTimer.current);
      }
    };
  }, []);

  const handleSelect = (genre) => {
    onSelect(genre);
    setIsPaused(true);

    if (pauseTimer.current) {
      window.clearTimeout(pauseTimer.current);
    }

    pauseTimer.current = window.setTimeout(() => setIsPaused(false), 5000);
  };

  if (!visibleGenres.length) {
    return null;
  }

  return (
    <div className="relative overflow-hidden py-2">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-12 bg-gradient-to-r from-white to-transparent dark:from-[#121212]" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-12 bg-gradient-to-l from-white to-transparent dark:from-[#121212]" />
      <div
        className={`flex w-max gap-3 will-change-transform ${isPaused ? "pause-marquee" : "animate-category-marquee"}`}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
      >
        {trackGenres.map((genre, index) => (
          <button
            key={`${genre}-${index}`}
            type="button"
            onClick={() => handleSelect(genre)}
            className={`h-11 rounded-full border px-4 text-sm font-semibold transition ${
              selectedGenre === genre
                ? "border-slate-900 bg-slate-900 text-white shadow-sm dark:border-white dark:bg-white dark:text-slate-950"
                : "border-slate-200 bg-white text-slate-700 hover:border-slate-400 hover:text-slate-950 dark:border-white/10 dark:bg-white/[0.06] dark:text-slate-300 dark:hover:border-white/25 dark:hover:text-white"
            }`}
          >
            {genre}
          </button>
        ))}
      </div>
    </div>
  );
}
