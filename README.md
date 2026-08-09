# Personal AI Assistant ("Digital Twin" Interactive Persona Agent)

An enterprise-grade, domain-bounded "Digital Twin" conversational agent engineered for portfolio website integration. The system acts as an interactive proxy for Vishal Kumar (Python & AI Developer), answering inquiries from recruiters, prospective clients, and collaborators in a natural, first-person voice (`"I"` / `"My"`).

Powered by **FastAPI**, **LangGraph**, **ChromaDB**, **BAAI/bge-base-en-v1.5** embeddings, and **React + Tailwind CSS**.

---

## Key Features

1. **First-Person Persona & Grounded RAG:** Speaks directly on behalf of Vishal Kumar without hallucinating unverified roles, dates, or companies.
2. **Multi-Collection Vector Store:** 12 isolated domain collections (`about_me`, `resume`, `projects`, `experience`, `skills`, `certificates`, `blogs`, `github`, `linkedin`, `faqs`, `services`, `contact_info`).
3. **LangGraph State Machine Architecture:** Intent classification, query rewriting, hybrid similarity/MMR retrieval, prompt formatting, validation, and SQLite thread checkpointer memory.
4. **Server-Sent Events (SSE) Streaming:** Real-time token-by-token streaming with vector source badges.
5. **Modern Glassmorphic React UI:** Sleek dark mode design system, starter question pills, character counter, export/clear thread history.

---

## Directory Structure

```
personal-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI chat stream & KB management endpoints
│   │   ├── core/            # Config, logger, security filters
│   │   ├── graph/           # LangGraph state machine DAG & prompts
│   │   ├── ingest/          # Multi-format doc parser (PDF/DOCX/TXT/MD)
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── seed/            # Portfolio seed data & auto-ingestion (--reset support)
│   │   └── vectorstore/     # ChromaDB & BAAI/bge-base-en-v1.5 embeddings
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Glassmorphic ChatWidget components
│   │   ├── context/         # Chat state provider
│   │   ├── hooks/           # useChatStream hook
│   │   └── styles/          # Tailwind glassmorphic theme
│   └── package.json
├── docker/                  # Dockerfile & docker-compose configurations
└── README.md
```

---

## Quickstart & Local Setup

### 1. Backend Setup (FastAPI + LangGraph)

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Reset and seed ChromaDB with clean knowledge base:
python -m app.seed.seed_ingest --reset

python app/main.py
```
Backend API server will run at `http://localhost:8000`.

### 2. Frontend Setup (React + Vite + Tailwind)

```bash
cd frontend
npm install
npm run dev
```
Frontend web application will run at `http://localhost:5173`.

---

## Verification & Testing

- **Health Check:** `GET http://localhost:8000/api/v1/health`
- **Suggestions:** `GET http://localhost:8000/api/v1/suggestions`
- **Collection Stats:** `GET http://localhost:8000/api/v1/kb/collections`
- **Chat Stream:** `POST http://localhost:8000/api/v1/chat/stream`
- **Pytest Suite:** `python -m pytest tests/test_portfolio_assistant.py`
