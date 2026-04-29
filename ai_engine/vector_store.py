import chromadb
from embeddings import get_embedding

# initialize chroma
client = chromadb.Client()

collection = client.get_or_create_collection(name="books")


def add_book_embedding(book_id: int, text: str):
    embedding = get_embedding(text)

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(book_id)]
    )


def search_similar(query: str):
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return results