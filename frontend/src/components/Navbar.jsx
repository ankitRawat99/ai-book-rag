import { BookOpen, Settings, Filter } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getGenres } from "../api.js";
import { useTheme } from "../context/ThemeContext.jsx";

export default function Navbar() {
  const [genres, setGenres] = useState([]);
  const [hasScrolled, setHasScrolled] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showGenres, setShowGenres] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    getGenres().then(setGenres).catch(() => setGenres([]));
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setHasScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-40 transition-all duration-300 ${
        hasScrolled
          ? "border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-lg shadow-sm"
          : "border-b border-gray-200/40 dark:border-gray-700/40 bg-white/50 dark:bg-[#1a1a1a]/50 backdrop-blur-sm"
      }`}
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3 sm:px-8 lg:px-10">
        <Link
          to="/"
          className="flex shrink-0 items-center gap-2.5 font-black text-gray-900 dark:text-gray-100 hover:opacity-80 transition-opacity"
        >
          <span className="grid h-10 w-10 place-items-center rounded-lg bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 shadow-lg hover:shadow-xl transition-shadow">
            <BookOpen className="h-5 w-5" />
          </span>
          <span className="hidden text-lg sm:inline">
            Librarian RAG
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <div className="relative">
            <button
              onClick={() => {
                setShowGenres(!showGenres);
                setShowSettings(false);
              }}
              className="h-11 px-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] flex items-center gap-2 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <Filter className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:inline">Genres</span>
            </button>
            
            {showGenres && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowGenres(false)}
                />
                <div className="absolute right-0 mt-2 w-56 max-h-96 overflow-y-auto rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] shadow-lg z-50">
                  <div className="p-2">
                    <Link
                      to="/"
                      onClick={() => setShowGenres(false)}
                      className="block px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
                    >
                      All Genres
                    </Link>
                    {genres.map((genre) => (
                      <Link
                        key={genre}
                        to={`/?genre=${encodeURIComponent(genre)}`}
                        onClick={() => setShowGenres(false)}
                        className="block px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
                      >
                        {genre}
                      </Link>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="relative">
            <button
              onClick={() => {
                setShowSettings(!showSettings);
                setShowGenres(false);
              }}
              className="h-11 w-11 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] flex items-center justify-center shadow-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <Settings className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            </button>
            
            {showSettings && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowSettings(false)}
                />
                <div className="absolute right-0 mt-2 w-48 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] shadow-lg z-50">
                  <div className="p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Theme</span>
                      <button
                        onClick={toggleTheme}
                        className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-600 focus:ring-offset-2 dark:focus:ring-offset-[#1a1a1a] bg-gray-200 dark:bg-gray-700"
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white dark:bg-gray-900 transition-transform ${
                            theme === "dark" ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      {theme === "light" ? "Light" : "Dark"} mode
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
