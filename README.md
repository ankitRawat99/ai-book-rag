# AI Book RAG

A modern book recommendation system with AI-powered search and semantic recommendations.

## Features

- 🎨 **Clean Minimal Design** - Ultra-minimal UI with neutral gray colors
- 🌓 **Light/Dark Mode** - Toggle theme via settings icon
- 🖼️ **High-Resolution Covers** - Sharp book images from Open Library
- 🤖 **AI Summaries** - Context-aware summaries for every book
- 🔍 **Semantic Search** - Natural language search with vector embeddings
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop
- ⚡ **Fast Performance** - Lazy loading and optimized animations

## Quick Start

### First Time Setup

1. **Setup Database** (required for first run):
   ```bash
   cd backend
   python setup_database.py
   ```
   This will scrape ~1000 books, fetch high-res images, generate AI summaries, and build the search index (~15-20 minutes).

2. **Start Backend**:
   ```bash
   .\run_backend.ps1
   ```

3. **Start Frontend** (new terminal):
   ```bash
   cd ..\frontend
   .\run_frontend.ps1
   ```

4. **Open Browser**: http://127.0.0.1:5173

### Development Mode

1. Start backend: `.\backend\run_backend.ps1`
2. Start frontend: `.\frontend\run_frontend.ps1`
3. Open http://127.0.0.1:5173

### Production Mode

1. Build frontend: `.\frontend\build_frontend.ps1`
2. Start backend: `.\backend\run_backend.ps1`
3. Open http://127.0.0.1:8000

## Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy
- **Database**: SQLite + ChromaDB (vector store)
- **AI**: HuggingFace (flan-t5-base + sentence-transformers)
- **Data**: books.toscrape.com + Open Library API

## Key Features

### Theme Toggle
- Settings icon in navbar opens theme menu
- Toggle between light and dark mode
- Preference saved in localStorage

### Hero Section
- Clean minimal design
- 2-column auto-scrolling carousel
- Smooth 60fps animations

### Search
- White background with black text (light mode)
- Dark background with white text (dark mode)
- Loading spinner during search
- Natural language queries

### Book Cards
- High-resolution cover images
- Hover effects (scale, shadow)
- Rating badges and genre tags
- Responsive grid layout

## Maintenance

### Regenerate AI Summaries
```bash
cd backend
python generate_summaries.py
```

### Add More Books
```bash
cd backend
python seed.py --pages 100 --with-details
python generate_summaries.py
```

### Reset Database
```bash
cd backend
del books.db
rmdir /s ai_engine\chroma_db
python setup_database.py
```

## Troubleshooting

**Issue**: Books have no images
- **Solution**: Run `python setup_database.py` to fetch high-res images

**Issue**: Summaries are generic
- **Solution**: Run `python generate_summaries.py` to regenerate

**Issue**: Ask AI not working
- **Solution**: Ensure ChromaDB is built (run `python reindex.py`)

**Issue**: Slow performance
- **Solution**: Reduce number of books or enable production build

## License

MIT