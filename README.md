# AI Book RAG

A minimal, modern book recommendation system featuring AI-powered search and semantic summaries.

---

## 🚀 Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy
- **AI & Storage:** SQLite, ChromaDB, HuggingFace (Flan-T5 + Sentence Transformers)
- **Data Sources:** Open Library API, Books.toscrape.com

## ✨ Features

- **Intelligent Search:** Natural language semantic search using vector embeddings.
- **AI Summaries:** Context-aware, dynamically generated book summaries.
- **Modern UI/UX:** Responsive, clean design with light/dark mode and high-res cover imagery.

## 🛠️ Quick Start

### 1. Initial Setup
Generates the database, fetches high-res images, creates AI summaries, and builds the search index (takes ~15-20 mins).

```bash
cd backend
python setup_database.py
```

### 2. Run Servers

**Development:**
```bash
# Terminal 1: Backend
.\backend\run_backend.ps1

# Terminal 2: Frontend
.\frontend\run_frontend.ps1
```
*UI accessible at `http://127.0.0.1:5173`*

**Production:**
```bash
.\frontend\build_frontend.ps1
.\backend\run_backend.ps1
```
*UI accessible at `http://127.0.0.1:8000`*

## 🔧 Maintenance

| Task | Command (run from `backend/` dir) |
|---|---|
| **Regenerate AI Summaries** | `python generate_summaries.py` |
| **Add More Books** | `python seed.py --pages 100 --with-details`<br>`python generate_summaries.py` |
| **Fix "Ask AI" / Rebuild Index** | `python reindex.py` |
| **Hard Reset Database** | `del books.db`<br>`rmdir /s ai_engine\chroma_db`<br>`python setup_database.py` |

## 📄 License
MIT