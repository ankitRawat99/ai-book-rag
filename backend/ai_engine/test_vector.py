from backend.ai_engine.vector_store import add_book_embedding, search_similar

# add sample
add_book_embedding(1, "Atomic Habits by James Clear")
add_book_embedding(2, "Deep Work by Cal Newport")

# search
results = search_similar("books about productivity")

print(results)