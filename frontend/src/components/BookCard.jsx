import { useState } from "react";
import { Link } from "react-router-dom";

/* ─── deterministic spine colour per book title ─────────── */
const SPINE_COLORS = [
  { top: "#1a237e", bot: "#283593" }, // deep indigo
  { top: "#004d40", bot: "#00695c" }, // deep teal
  { top: "#b71c1c", bot: "#c62828" }, // deep red
  { top: "#4a148c", bot: "#6a1b9a" }, // deep purple
  { top: "#e65100", bot: "#ef6c00" }, // deep orange
  { top: "#1b5e20", bot: "#2e7d32" }, // deep green
  { top: "#263238", bot: "#37474f" }, // deep slate
  { top: "#880e4f", bot: "#ad1457" }, // deep pink
];

function spineFor(title = "") {
  return SPINE_COLORS[title.charCodeAt(0) % SPINE_COLORS.length];
}

function fallbackSrc(title = "") {
  const s = spineFor(title);
  const label = encodeURIComponent(title.slice(0, 22));
  const bg = s.top.replace("#", "%23");
  const hi = s.bot.replace("#", "%23");
  return (
    `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450'%3E` +
    `%3Crect fill='${bg}' width='300' height='450'/%3E` +
    `%3Crect fill='${hi}' x='12' y='12' width='276' height='426' rx='4'/%3E` +
    `%3Ctext x='50%25' y='42%25' text-anchor='middle' fill='%23ffffffcc' font-size='18' font-weight='800' font-family='Georgia,serif'%3E${label}%3C/text%3E` +
    `%3Ctext x='50%25' y='56%25' text-anchor='middle' fill='%23ffffff66' font-size='12' font-family='Georgia,serif'%3ENo Cover%3C/text%3E` +
    `%3C/svg%3E`
  );
}

const D = 26; // spine/page depth in px

export default function BookCard({ book }) {
  const [hovered, setHovered] = useState(false);
  const { top, bot } = spineFor(book.title);
  const fallback = fallbackSrc(book.title);
  const author =
    !book.author || book.author === "Unknown" || book.author === "Unknown author"
      ? null
      : book.author;

  return (
    <Link
      to={`/book/${book.id}`}
      className="block select-none"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      /* perspective on the outer wrapper */
      style={{ perspective: "700px", perspectiveOrigin: "50% 40%" }}
    >
      {/* ── aspect-ratio shell ────────────────────── */}
      <div style={{ position: "relative", paddingBottom: "154%" }}>

        {/* ── 3-D book (rotates as one unit) ───────── */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            transformStyle: "preserve-3d",
            transform: hovered
              ? `rotateY(-28deg) translateY(-8px)`
              : `rotateY(0deg)  translateY(0px)`,
            transition:
              "transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94), filter 0.4s ease",
            filter: hovered
              ? "drop-shadow(14px 22px 36px rgba(0,0,0,0.55)) drop-shadow(2px 4px 8px rgba(0,0,0,0.25))"
              : "drop-shadow(4px 8px 18px rgba(0,0,0,0.28))",
          }}
        >

          {/* ══ FRONT COVER ═══════════════════════════ */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              /* push forward so spine/pages can fold behind */
              transform: `translateZ(${D / 2}px)`,
              borderRadius: "1px 4px 4px 1px",
              overflow: "hidden",
              /* inner left sheen mimicking the binding groove */
              boxShadow: "inset 6px 0 12px rgba(0,0,0,0.22)",
            }}
          >
            {/* cover image */}
            <img
              src={book.image || fallback}
              alt={book.title}
              loading="lazy"
              decoding="async"
              onError={(e) => {
                if (e.currentTarget.src === fallback) return;
                e.target.src = fallback;
              }}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                display: "block",
                transition: "transform 0.5s ease",
                transform: hovered ? "scale(1.04)" : "scale(1)",
              }}
            />

            {/* dark vignette on hover */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.24) 42%, transparent 68%)",
                opacity: hovered ? 1 : 0,
                transition: "opacity 0.35s ease",
              }}
            />

            {/* ★ rating badge — always visible */}
            <div
              style={{
                position: "absolute",
                top: 7,
                right: 7,
                display: "flex",
                alignItems: "center",
                gap: 3,
                background: "rgba(0,0,0,0.68)",
                backdropFilter: "blur(6px)",
                borderRadius: 999,
                padding: "3px 7px",
                fontSize: 10,
                fontWeight: 700,
                color: "#fff",
                letterSpacing: 0,
                pointerEvents: "none",
              }}
            >
              <span style={{ color: "#fbbf24" }}>★</span>
              {Number(book.rating || 0).toFixed(1)}
            </div>

            {/* info block — slides up on hover */}
            <div
              style={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                padding: "10px 10px 12px",
                opacity: hovered ? 1 : 0,
                transform: hovered ? "translateY(0)" : "translateY(6px)",
                transition: "opacity 0.3s ease, transform 0.3s ease",
                pointerEvents: "none",
              }}
            >
              <p
                style={{
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: "rgba(255,255,255,0.55)",
                  margin: "0 0 3px",
                }}
              >
                {book.genre || "General"}
              </p>
              <p
                style={{
                  fontSize: 11,
                  fontWeight: 800,
                  color: "#fff",
                  margin: "0 0 2px",
                  lineHeight: 1.3,
                  textShadow: "0 1px 4px rgba(0,0,0,0.7)",
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                {book.title}
              </p>
              {author && (
                <p
                  style={{
                    fontSize: 9,
                    color: "rgba(255,255,255,0.5)",
                    margin: 0,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {author}
                </p>
              )}
            </div>
          </div>
          {/* ══ END FRONT COVER ════════════════════════ */}

          {/* ══ SPINE — left face ══════════════════════
              positioned at left:0 (right edge = left boundary of book)
              rotateY(-90°) around that right edge folds it backward
              giving a real left-edge face.
          */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: D,
              height: "100%",
              transformOrigin: "right center",
              transform: `rotateY(-90deg) translateZ(${D / 2}px)`,
              background: `linear-gradient(160deg, ${top} 0%, ${bot} 100%)`,
              borderRadius: "4px 0 0 4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              overflow: "hidden",
              boxShadow:
                "inset -4px 0 10px rgba(0,0,0,0.35), inset 2px 0 5px rgba(255,255,255,0.06)",
            }}
          >
            <span
              style={{
                writingMode: "vertical-rl",
                transform: "rotate(180deg)",
                fontSize: 8,
                fontWeight: 700,
                letterSpacing: "0.07em",
                color: "rgba(255,255,255,0.82)",
                padding: "8px 2px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                maxHeight: "88%",
              }}
            >
              {book.title}
            </span>
          </div>
          {/* ══ END SPINE ══════════════════════════════ */}

          {/* ══ PAGES — right face ═════════════════════
              positioned at right:0 (left edge = right boundary of book)
              rotateY(+90°) around that left edge folds it backward.
          */}
          <div
            style={{
              position: "absolute",
              top: "2%",
              right: 0,
              width: D,
              height: "96%",
              transformOrigin: "left center",
              transform: `rotateY(90deg) translateZ(${D / 2}px)`,
              borderRadius: "0 3px 3px 0",
              background:
                "repeating-linear-gradient(to bottom, #f5f0e8 0px, #f5f0e8 1px, #ede4d3 2px, #ede4d3 3px, #f2eade 3px, #f2eade 5px)",
              boxShadow:
                "inset -3px 0 6px rgba(0,0,0,0.08), inset 1px 0 3px rgba(0,0,0,0.05)",
            }}
          />
          {/* ══ END PAGES ══════════════════════════════ */}

        </div>
        {/* end .book-3d */}
      </div>
      {/* end aspect-ratio shell */}
    </Link>
  );
}
