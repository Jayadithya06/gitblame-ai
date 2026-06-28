# GitBlame AI

> Find the exact commit that broke your code — using AI.

GitBlame AI lets you describe a bug in plain English and automatically identifies the most likely guilty commit from your git history. It ranks suspects by confidence, explains why each commit is suspicious, and gives you both a rollback command and a proper fix suggestion.

---

## The Problem

Tech teams push hundreds of commits every day. When something breaks in production, finding the exact commit that caused it means reading through dozens of diffs manually — hoping something looks wrong. That takes hours.

GitBlame AI solves this in seconds.

---

## How It Works

```
You describe the bug in plain English
           ↓
GitHub API fetches all commits in your date range
           ↓
Each commit's diff is split by file (chunked)
           ↓
Every chunk is converted into a vector (embedding)
           ↓
Your bug description is embedded too
           ↓
Semantic search finds the most similar diff chunks
           ↓
LLM reasons over the top suspects
           ↓
You get ranked commits with confidence scores,
explanations, rollback commands, and fix suggestions
```

This is **RAG (Retrieval Augmented Generation)** applied to git history instead of documents.

---

## Features

- 🔍 **Semantic search** — finds relevant commits by meaning, not keywords
- 📊 **Confidence scores** — each suspect ranked by likelihood
- 💬 **Plain English explanations** — why each commit is suspicious
- 🔄 **Rollback commands** — one-click `git revert` ready to copy
- 🛠️ **Fix suggestions** — not just revert, but how to actually solve the root cause
- 🌗 **Dark / Light mode** — full responsive UI
- 🔐 **GitHub OAuth** — secure login, your credentials never touch the app

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite, React Router |
| Backend | FastAPI (Python) |
| Auth | GitHub OAuth (Authorization Code Flow) |
| Embeddings (local) | Ollama + nomic-embed-text |
| Embeddings (production) | HuggingFace Inference API (all-MiniLM-L6-v2) |
| Vector Database | ChromaDB |
| LLM (local) | Ollama + llama3.2 |
| LLM (production) | Groq — Llama 3.3 70B Versatile |
| Deployment | Render (backend + frontend) |

---

## Architecture

```
gitblame-ai/
├── gitblame-frontend/          # React + Vite
│   └── src/
│       ├── App.jsx             # Main app — all steps + state
│       ├── Callback.jsx        # OAuth callback handler
│       ├── App.css             # All styles
│       └── main.jsx            # React entry point
│
└── gitblame-backend/           # FastAPI
    ├── main.py                 # App setup + CORS + router wiring
    ├── routers/
    │   ├── auth.py             # GitHub OAuth routes
    │   ├── github.py           # Commit + diff fetching routes
    │   └── analysis.py        # Analysis endpoint
    └── services/
        ├── embedder.py         # Text → vector (Ollama / HuggingFace)
        ├── vector_store.py     # ChromaDB storage + search
        └── llm_service.py      # LLM reasoning (Ollama / Groq)
```

---

## How to Use

1. **Login** with your GitHub account
2. **Select** the repository you want to investigate
3. **Pick a date range** — narrow down when the bug was introduced
4. **Fetch commits** — see all commits in that window
5. **Describe the bug** — plain English, e.g. *"login stopped working after Tuesday's deploy"*
6. **Analyze** — AI searches the diffs and ranks the suspects

---

## Key Technical Concepts

### Why chunk diffs by file?

A commit touching 20 files produces one averaged embedding that loses all signal. File-level chunking preserves specificity — each file's diff becomes its own searchable vector.

### Why semantic search over keyword search?

Keyword search would miss *"token validation middleware"* when you search for *"login broke"*. Semantic search matches by meaning — they're the same concept even with completely different words.

### Why RAG?

The commit diffs are the knowledge base. Embeddings make them semantically searchable. Vector search retrieves the relevant ones. The LLM reasons over retrieved context. Classic RAG — just applied to git history.

---

## Deployment

The app is deployed on [Render](https://render.com).

In production:
- `USE_LOCAL_EMBEDDINGS=false` switches embeddings from Ollama → HuggingFace
- The LLM switches from local Ollama → Groq (Llama 3.3 70B Versatile)

**Live demo:** [your-render-url]

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GITHUB_CLIENT_ID` | GitHub OAuth App Client ID | ✅ |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App Client Secret | ✅ |
| `HF_TOKEN` | HuggingFace API token (production embeddings) | ✅ |
| `GROQ_API_KEY` | Groq API key (production LLM) | ✅ |
| `USE_LOCAL_EMBEDDINGS` | `true` for local, `false` for production | ✅ |
| `VITE_API_URL` | Backend URL (frontend env variable) | ✅ |

---

## Built By

**Jayadithya** — [@Jayadithya06](https://github.com/Jayadithya06)

---

*GitBlame AI — because `git blame` only tells you who. This tells you why.*
