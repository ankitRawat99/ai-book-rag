import { ChevronLeft, ChevronRight, Star } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

export default function Carousel({ books }) {
  const featured = useMemo(() => books.slice(0, 8), [books]);
  const [index, setIndex] = useState(0);
  const fallbackImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="450"%3E%3Crect fill="%23475569" width="300" height="450"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" fill="%23cbd5e1" font-size="18"%3ENo Cover%3C/text%3E%3C/svg%3E';

  if (!featured.length) {
    return <div className="h-72 animate-pulse rounded-3xl bg-slate-200" />;
  }

  const current = featured[index % featured.length];

  return (
    <section className="relative overflow-hidden rounded-3xl bg-slate-950 text-white shadow-soft">
      <div className="absolute inset-0">
        <img 
          src={current.image || fallbackImage} 
          alt="" 
          className="h-full w-full object-cover opacity-25 blur-sm" 
          loading="eager"
          decoding="async"
          onError={(e) => {
            if (e.currentTarget.src !== fallbackImage) e.target.src = fallbackImage;
          }}
        />
      </div>
      <div className="relative grid gap-8 p-6 sm:p-8 lg:grid-cols-[260px_1fr] lg:p-10">
        <Link to={`/book/${current.id}`} className="group mx-auto block w-48 sm:w-56 lg:w-full">
          <img
            src={current.image || fallbackImage}
            alt={current.title}
            className="aspect-[2/3] w-full rounded-2xl object-cover shadow-2xl transition duration-300 group-hover:scale-105"
            loading="eager"
            decoding="async"
            onError={(e) => {
              if (e.currentTarget.src !== fallbackImage) e.target.src = fallbackImage;
            }}
          />
        </Link>
        <div className="flex flex-col justify-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-normal text-teal-200">
            Featured recommendation
          </p>
          <h1 className="max-w-3xl text-4xl font-black leading-tight sm:text-5xl">
            {current.title}
          </h1>
          <p className="mt-3 text-lg text-slate-200">{current.author}</p>
          <p className="line-clamp-3 mt-5 max-w-2xl text-slate-300">{current.description}</p>
          <div className="mt-6 flex flex-wrap items-center gap-3 text-sm">
            <span className="rounded-full bg-white/10 px-3 py-1.5">{current.genre}</span>
            <span className="inline-flex items-center gap-1 rounded-full bg-white/10 px-3 py-1.5">
              <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              {Number(current.rating || 0).toFixed(1)}
            </span>
            {current.publish_year ? (
              <span className="rounded-full bg-white/10 px-3 py-1.5">{current.publish_year}</span>
            ) : null}
          </div>
        </div>
      </div>
      <div className="absolute bottom-5 right-5 flex gap-2">
        <button
          className="grid h-10 w-10 place-items-center rounded-full bg-white/15 text-white backdrop-blur transition hover:bg-white/25"
          onClick={() => setIndex((value) => (value - 1 + featured.length) % featured.length)}
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <button
          className="grid h-10 w-10 place-items-center rounded-full bg-white/15 text-white backdrop-blur transition hover:bg-white/25"
          onClick={() => setIndex((value) => (value + 1) % featured.length)}
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </section>
  );
}
