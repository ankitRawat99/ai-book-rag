"""Reset and rebuild the local catalog and vector index."""
import argparse
import shutil
from pathlib import Path


def _remove_existing(db_path: Path, chroma_path: Path):
    if db_path.exists():
        db_path.unlink()
        print("Deleted old books.db")

    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        print("Deleted old ChromaDB vector store")


def main():
    parser = argparse.ArgumentParser(description="Rebuild books.db and ChromaDB")
    parser.add_argument("--source", choices=["open-library", "books-to-scrape"], default="open-library")
    parser.add_argument("--limit-per-subject", type=int, default=250)
    parser.add_argument("--subjects", nargs="*", default=None)
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    args = parser.parse_args()

    print("=" * 60)
    print("AI Book RAG - Complete Database Setup")
    print("=" * 60)
    print()

    db_path = Path("books.db")
    chroma_path = Path("ai_engine/chroma_db")

    if db_path.exists() or chroma_path.exists():
        print("WARNING: Existing database detected.")
        print()
        print("This will:")
        print("  1. Delete the existing books.db")
        print("  2. Delete the ChromaDB vector store")
        print("  3. Re-ingest structured book metadata")
        print("  4. Generate summaries and key points")
        print("  5. Build vector embeddings for semantic search")
        print()

        if not args.yes:
            response = input("Continue? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("Setup cancelled.")
                return

        _remove_existing(db_path, chroma_path)

    print()
    print("Starting fresh setup...")
    print()

    from database import Base, engine
    import models

    Base.metadata.create_all(bind=engine)

    print("[1/3] Ingesting book catalog...")
    print()

    try:
        if args.source == "open-library":
            from seed_open_library import seed_open_library_books

            seed_open_library_books(
                subjects=args.subjects,
                limit_per_subject=args.limit_per_subject,
                rebuild_index=False,
            )
        else:
            from seed import seed_books

            seed_books(pages=50, include_details=True, rebuild_index=False)

        print("Books ingested successfully.")
    except Exception as exc:
        print(f"Error during ingestion: {exc}")
        return

    print()
    print("[2/3] Generating summaries and key points...")
    print()

    try:
        from generate_summaries import generate_all_summaries

        generate_all_summaries()
        print("Summaries generated successfully.")
    except Exception as exc:
        print(f"Error generating summaries: {exc}")
        print("You can run 'python generate_summaries.py' later to retry.")

    print()
    print("[2b/3] Rebuilding vector index...")
    print()

    try:
        from reindex import rebuild_index

        rebuild_index()
        print("Vector index rebuilt successfully.")
    except Exception as exc:
        print(f"Error rebuilding vector index: {exc}")
        return

    print()
    print("[3/3] Verifying setup...")
    print()

    from database import SessionLocal
    db = SessionLocal()
    try:
        book_count = db.query(models.Book).count()
        books_with_summaries = db.query(models.Book).filter(
            models.Book.ai_summary.isnot(None),
            models.Book.ai_summary != "",
        ).count()
        books_with_images = db.query(models.Book).filter(
            models.Book.image.isnot(None),
            models.Book.image != "",
        ).count()

        print(f"Total books: {book_count}")
        print(f"Books with summaries: {books_with_summaries}")
        print(f"Books with images: {books_with_images}")
    finally:
        db.close()

    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start backend: .\\run_backend.ps1")
    print("  2. Start frontend: cd frontend && .\\run_frontend.ps1")
    print("  3. Open http://127.0.0.1:5173")


if __name__ == "__main__":
    main()
