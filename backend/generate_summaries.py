"""Generate AI summaries for all books in the database"""
import os
from transformers import pipeline
from database import SessionLocal
import models
from services.data_quality import build_summary_text, build_key_points_list, dump_key_points

# Set to use LLM for better summaries
os.environ["USE_LLM_ANSWER"] = "1"

_summarizer = None

def get_summarizer():
    global _summarizer
    if _summarizer is None:
        print("Loading AI model...")
        _summarizer = pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            model_kwargs={"local_files_only": True},
        )
    return _summarizer

def generate_ai_summary(book) -> str:
    """Generate a concise, meaningful AI summary for a book"""
    
    # Build context from book metadata
    context_parts = [
        f"Title: {book.title}",
        f"Author: {book.author}",
        f"Genre: {book.genre or 'General'}",
    ]
    
    if book.publish_year:
        context_parts.append(f"Published: {book.publish_year}")
    
    if book.description and len(book.description) > 50:
        context_parts.append(f"Description: {book.description[:300]}")
    
    context = "\n".join(context_parts)
    
    # Create a focused prompt for better summaries
    prompt = f"""Write a compelling 3-4 sentence summary for this book. Focus on what makes it unique and valuable to readers.

{context}

Summary (be specific, engaging, and informative):"""

    try:
        summarizer = get_summarizer()
        result = summarizer(
            prompt,
            max_length=150,
            min_length=40,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
        )
        
        summary = result[0]["generated_text"].strip()
        
        # Validate summary quality
        if len(summary) < 30 or summary.lower().startswith(("this is", "this book is")):
            # Fallback to template-based summary
            return build_summary_text(book)
        
        return summary
    except Exception as e:
        print(f"Error generating summary for '{book.title}': {e}")
        return build_summary_text(book)

def generate_all_summaries(limit=None):
    """Generate AI summaries for all books"""
    db = SessionLocal()
    
    try:
        query = db.query(models.Book)
        if limit:
            query = query.limit(limit)
        
        books = query.all()
        total = len(books)
        
        print(f"Generating summaries for {total} books...")
        
        for idx, book in enumerate(books, 1):
            print(f"[{idx}/{total}] Processing: {book.title}")
            
            # Generate AI summary
            book.ai_summary = generate_ai_summary(book)
            
            # Generate key points
            key_points = build_key_points_list(book)
            book.key_points = dump_key_points(key_points)
            
            # Commit every 10 books to avoid losing progress
            if idx % 10 == 0:
                db.commit()
                print(f"  ✓ Saved progress ({idx}/{total})")
        
        # Final commit
        db.commit()
        print(f"\n✓ Successfully generated summaries for {total} books!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate AI summaries for books")
    parser.add_argument("--limit", type=int, help="Limit number of books to process")
    args = parser.parse_args()
    
    generate_all_summaries(limit=args.limit)
