import { Star } from "lucide-react";
import { Link } from "react-router-dom";

function coverFallback(title = "Book") {
  const label = encodeURIComponent(title.substring(0, 25));
  return `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="600"%3E%3Crect fill="%23e5e7eb" width="400" height="600"/%3E%3Ctext x="50%25" y="47%25" text-anchor="middle" fill="%236b7280" font-size="22" font-weight="700"%3E${label}%3C/text%3E%3Ctext x="50%25" y="56%25" text-anchor="middle" fill="%239ca3af" font-size="14"%3ENo Cover%3C/text%3E%3C/svg%3E`;
}

export default function BookCard({ book }) {
  const fallbackImage = coverFallback(book.title);

  return (
    <Link
      to={`/book/${book.id}`}
      className="group relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-xl dark:border-white/10 dark:bg-white/[0.06] dark:hover:border-white/25"
    >
      <div className="relative aspect-[2/3] overflow-hidden bg-gray-100 dark:bg-gray-800 flex-shrink-0">
        <img
          src={book.image || fallbackImage}
          alt={book.title}
          className="h-full w-full object-cover transition duration-500 group-hover:scale-110"
          loading="lazy"
          decoding="async"
          onError={(e) => {
            if (e.currentTarget.src === fallbackImage) return;
            e.target.src = fallbackImage;
          }}
        />
        
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/0 to-black/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        <div className="absolute top-3 right-3 flex items-center gap-1.5 rounded-full bg-gray-900 dark:bg-gray-100 backdrop-blur-md px-2.5 py-1.5 shadow-lg">
          <Star className="h-3.5 w-3.5 fill-gray-100 dark:fill-gray-900 text-gray-100 dark:text-gray-900" />
          <span className="text-xs font-bold text-gray-100 dark:text-gray-900">{Number(book.rating || 0).toFixed(1)}</span>
        </div>

        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-900 dark:bg-gray-100 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left" />
      </div>
      
      <div className="flex flex-grow flex-col justify-between space-y-3 p-4">
        <div className="flex items-center justify-between gap-2">
          <span className="inline-block rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-700 dark:border-white/10 dark:bg-white/[0.06] dark:text-slate-300">
            {book.genre || "General"}
          </span>
        </div>
        
        <h3 className="line-clamp-2 text-base font-black leading-snug text-slate-950 transition group-hover:text-slate-700 dark:text-white dark:group-hover:text-slate-300">
          {book.title}
        </h3>
        
        <p className="line-clamp-1 text-sm font-semibold text-slate-500 transition group-hover:text-slate-700 dark:text-slate-400 dark:group-hover:text-slate-300">
          {book.author === "Unknown" || book.author === "Unknown author" ? "Author unavailable" : book.author}
        </p>

        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 mt-auto pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs font-semibold text-gray-600 dark:text-gray-400">Click to view →</p>
        </div>
      </div>
    </Link>
  );
}
