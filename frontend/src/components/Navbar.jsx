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
      <nav className="w-full px-4 sm:px-6 md:px-8 flex items-center justify-between gap-4 py-3">
        <Link
          to="/"
          className="flex shrink-0 items-center gap-2.5 font-black text-gray-900 dark:text-gray-100 hover:opacity-80 transition-opacity"
        >
          <img 
            src="/ibook-logo.svg" 
            alt="IBooK Logo" 
            className="h-10 w-10 hover:scale-105 transition-transform drop-shadow-sm" 
          />
          <span className="hidden text-lg sm:inline">
            IBooK
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-6 mr-4">
            <Link to="/" className="text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-colors">
              Home
            </Link>
            <Link to="/#books-grid" className="text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-colors">
              Books
            </Link>
            <Link to="/" className="text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-colors">
              Authors
            </Link>
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
