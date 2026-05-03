import { ArrowLeft, ExternalLink, Star } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getBook } from "../api.js";

export default function BookDetailsPage() {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const fallbackImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="450"%3E%3Crect fill="%23e5e7eb" width="300" height="450"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" fill="%236b7280" font-size="18"%3ENo Cover Available%3C/text%3E%3C/svg%3E';

  useEffect(() => {
    setIsLoading(true);
    getBook(id)
      .then(setBook)
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-white dark:bg-[#1a1a1a]">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="h-[600px] animate-pulse rounded-3xl bg-gray-200 dark:bg-gray-800" />
        </div>
      </main>
    );
  }

  if (!book) {
    return (
      <main className="min-h-screen bg-white dark:bg-[#1a1a1a]">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="rounded-2xl border-2 border-dashed border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] p-16 text-center">
            <p className="text-xl font-bold text-gray-600 dark:text-gray-400">Book not found.</p>
            <Link
              to="/"
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-gray-900 dark:bg-gray-100 px-6 py-3 text-sm font-bold text-white dark:text-gray-900 transition hover:opacity-90"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white dark:bg-[#1a1a1a] transition-colors">
      <div className="relative bg-gray-50 dark:bg-[#0d0d0d] pb-32 border-b border-gray-200 dark:border-gray-800">
        <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm font-bold text-gray-600 dark:text-gray-400 transition hover:text-gray-900 dark:hover:text-gray-100"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to books
          </Link>
        </div>
      </div>

      <div className="relative mx-auto max-w-7xl px-4 -mt-24 pb-16 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-[380px_1fr]">
          <div className="mx-auto w-full max-w-sm">
            <div className="sticky top-24">
              <div className="overflow-hidden rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-700">
                <img
                  src={book.image || fallbackImage}
                  alt={book.title}
                  className="aspect-[2/3] w-full object-cover"
                  loading="eager"
                  decoding="async"
                  onError={(e) => {
                    e.target.src = fallbackImage;
                  }}
                />
              </div>
              
              {book.url && (
                <a
                  href={book.url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-gray-900 dark:bg-gray-100 px-6 py-4 text-sm font-bold text-white dark:text-gray-900 transition hover:opacity-90"
                >
                  View Source
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}
            </div>
          </div>

          <div className="space-y-8">
            <div className="rounded-3xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] p-8 shadow-lg">
              <div className="mb-6 flex flex-wrap gap-3">
                <span className="inline-flex items-center gap-1.5 rounded-xl bg-gray-100 dark:bg-gray-800 px-4 py-2 text-sm font-bold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
                  {book.genre}
                </span>
                {book.publish_year && (
                  <span className="rounded-xl bg-gray-100 dark:bg-gray-800 px-4 py-2 text-sm font-bold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
                    {book.publish_year}
                  </span>
                )}
                <span className="inline-flex items-center gap-1.5 rounded-xl bg-gray-100 dark:bg-gray-800 px-4 py-2 text-sm font-bold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
                  <Star className="h-4 w-4 fill-gray-700 dark:fill-gray-300 text-gray-700 dark:text-gray-300" />
                  {Number(book.rating || 0).toFixed(1)}
                </span>
              </div>
              
              <h1 className="text-4xl font-black leading-tight text-gray-900 dark:text-gray-100 lg:text-5xl">
                {book.title}
              </h1>
              <p className="mt-4 text-xl font-semibold text-gray-600 dark:text-gray-400">{book.author}</p>
            </div>

            <div className="rounded-3xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] p-8 shadow-lg">
              <div className="mb-4 flex items-center gap-2">
                <div className="rounded-lg bg-gray-900 dark:bg-gray-100 p-2">
                  <svg className="h-5 w-5 text-white dark:text-gray-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-black text-gray-900 dark:text-gray-100">AI-Generated Summary</h2>
              </div>
              <p className="leading-relaxed text-gray-700 dark:text-gray-300">{book.ai_summary}</p>
            </div>

            <div className="rounded-3xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a1a] p-8 shadow-lg">
              <h2 className="mb-6 text-2xl font-black text-gray-900 dark:text-gray-100">Key Points</h2>
              <div className="grid gap-4">
                {book.key_points.map((point, index) => (
                  <div
                    key={point}
                    className="flex items-start gap-4 rounded-2xl bg-gray-50 dark:bg-gray-800/50 p-5 transition hover:shadow-md border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-900 dark:bg-gray-100 text-sm font-bold text-white dark:text-gray-900">
                      {index + 1}
                    </div>
                    <p className="pt-1 text-gray-700 dark:text-gray-300">{point}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
