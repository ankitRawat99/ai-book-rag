import { Link } from "react-router-dom";
import { Star } from "lucide-react";
import { useEffect, useState } from "react";

export default function VerticalCarousel({ books = [] }) {
  const [scrollPosition, setScrollPosition] = useState(0);

  const displayBooks = [...books, ...books, ...books];
  const cardHeight = 180;
  const maxScroll = books.length * cardHeight;
  
  const column1 = displayBooks.filter((_, i) => i % 2 === 0);
  const column2 = displayBooks.filter((_, i) => i % 2 === 1);

  useEffect(() => {
    const interval = setInterval(() => {
      setScrollPosition((prev) => {
        const newPos = prev + 0.5;
        return newPos >= maxScroll ? 0 : newPos;
      });
    }, 20);

    return () => clearInterval(interval);
  }, [books.length]);

  if (!books.length) {
    return <div className="h-[600px] animate-pulse bg-gray-200 dark:bg-gray-800 rounded-3xl" />;
  }

  const fallbackImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="450"%3E%3Crect fill="%23e5e7eb" width="300" height="450"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" fill="%236b7280" font-size="18" font-weight="700"%3ENo Cover%3C/text%3E%3C/svg%3E';

  const renderBookCard = (book, index, columnKey) => (
    <Link
      key={`${columnKey}-${book.id}-${index}`}
      to={`/book/${book.id}`}
      className="group relative block mb-4 rounded-2xl overflow-hidden bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-all duration-300 hover:scale-[1.03] hover:shadow-2xl cursor-pointer"
      style={{ transform: 'translateZ(0)' }}
    >
      <div className="relative aspect-[2/3] overflow-hidden">
        <img
          src={book.image || fallbackImage}
          alt={book.title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          loading="lazy"
          onError={(e) => {
            if (e.currentTarget.src !== fallbackImage) {
              e.currentTarget.src = fallbackImage;
            }
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-300"></div>
        
        <div className="absolute top-2 right-2 flex items-center gap-1 bg-gray-900 dark:bg-gray-100 rounded-full px-2 py-1 shadow-lg">
          <Star className="h-3 w-3 fill-gray-100 dark:fill-gray-900 text-gray-100 dark:text-gray-900" />
          <span className="text-xs font-bold text-gray-100 dark:text-gray-900">{Number(book.rating || 0).toFixed(1)}</span>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
          <h3 className="font-bold text-sm line-clamp-2 mb-1 group-hover:text-gray-300 transition-colors duration-300">
            {book.title}
          </h3>
          <p className="text-xs text-gray-300 line-clamp-1 mb-2">
            {book.author === "Unknown" || book.author === "Unknown author"
              ? "Author unavailable"
              : book.author}
          </p>
          <span className="inline-block text-xs bg-gray-800/80 backdrop-blur-sm px-2 py-0.5 rounded-full text-white font-semibold">
            {book.genre || "General"}
          </span>
        </div>
      </div>
    </Link>
  );

  return (
    <div className="relative w-full h-[600px] overflow-hidden rounded-3xl">
      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-white dark:from-[#1a1a1a] to-transparent z-20 pointer-events-none"></div>
      <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-white dark:from-[#1a1a1a] to-transparent z-20 pointer-events-none"></div>

      <div className="flex gap-4 h-full">
        <div className="flex-1 overflow-hidden">
          <div
            className="will-change-transform"
            style={{
              transform: `translateY(-${scrollPosition}px)`,
              transition: 'transform 0.02s linear',
            }}
          >
            {column1.map((book, index) => 
              renderBookCard(book, index, 'col1')
            )}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <div
            className="will-change-transform"
            style={{
              transform: `translateY(-${maxScroll - scrollPosition + 90}px)`,
              transition: 'transform 0.02s linear',
            }}
          >
            {column2.map((book, index) => 
              renderBookCard(book, index, 'col2')
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
