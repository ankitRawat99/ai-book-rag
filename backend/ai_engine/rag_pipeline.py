from ai_engine.vector_store import search_similar

def generate_answer(query: str):
    # 🔍 Step 1: retrieve similar books
    results = search_similar(query)

    docs = results["documents"][0]

    # 🧠 Step 2: build context
    context = "\n".join(docs)

    # 🤖 Step 3: simple answer (LLM placeholder)
    answer = f"""
Based on your query, here are some relevant books:

{context}

These books can help you understand the topic better.
"""

    return answer