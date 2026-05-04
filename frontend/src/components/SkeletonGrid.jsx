export default function SkeletonGrid({ count = 12 }) {
  return (
    <div className="grid grid-cols-3 gap-3 sm:gap-5 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="w-full">
          <div
            className="w-full rounded-md animate-pulse"
            style={{
              paddingBottom: "150%",
              background: "linear-gradient(135deg, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%)",
              backgroundSize: "200% 100%",
              animation: `pulse-book 1.6s ease-in-out ${index * 0.06}s infinite`,
            }}
          />
        </div>
      ))}
    </div>
  );
}

