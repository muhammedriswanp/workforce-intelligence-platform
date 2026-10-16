# Workforce Intelligence Platform

An internal tool that suggests **who on your team should do which task** — and explains why.

Type a task in plain words. The AI checks everyone's skills, free time, and workload, then ranks the best matches. A manager always makes the final decision.

## Features

- **Employee profiles** — skills, experience, weekly capacity
- **Projects & tasks** — with AI breakdown of a project into tasks
- **AI recommendations** — best candidates with scores and reasons
- **Policy-aware** — reads your company policies before suggesting
- **AI Chat** — ask "Who is free this week?" and get live answers
- **Safety guard** — blocks unsafe requests (passwords, secrets, other people's data)
- **Two roles** — Managers can change things, Employees view their own work

## Tech Stack

| Layer | Tool |
| --- | --- |
| Backend | Python 3.11, FastAPI |
| Frontend | Streamlit |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| AI | Groq, LangGraph, RAG (Pinecone) |
| Safety | Guardrails AI |
| Auth | JWT + Argon2 |
| Package mgmt | uv |
| Tests / CI | pytest + GitHub Actions |

---

## Setup

### Option A — Docker Compose (recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/), PostgreSQL running on port `5432`, and a `.env` file (see [Environment Variables](#environment-variables)).

```bash
docker compose up --build -d     # start everything
docker compose logs -f           # watch logs (Ctrl+C to stop)
docker compose down              # stop
```

Check it works:

```bash
curl http://localhost:8000/health   # → {"status": "healthy"}
```

Then open **http://localhost:8501**

### Option B — Manual (for development)

**Prerequisites:** git, Python 3.11, [uv](https://docs.astral.sh/uv/), PostgreSQL, a [Groq API key](https://console.groq.com/), optionally a [Pinecone](https://www.pinecone.io/) account.

```bash
# 1. Clone
git clone https://github.com/muhammedriswanp/workforce-intelligence-platform.git
cd workforce-intelligence-platform

# 2. Create .env file (see below)

# 3. Install dependencies
uv sync

# 4. Create database (once)
#    In psql: CREATE DATABASE workforce_intelligence;

# 5. Create tables
uv run alembic upgrade head

# 6. (Optional) Load company policies into the knowledge base
uv run python -m app.rag.ingest

# 7. Start backend — terminal 1
uv run uvicorn main:app --reload

# 8. Start website — terminal 2
uv run streamlit run streamlit_app/home.py
```

Open **http://localhost:8501** and sign up.

| Service | URL |
| --- | --- |
| Website | http://localhost:8501 |
| API | http://127.0.0.1:8000 |
| API docs | http://127.0.0.1:8000/docs |

---

## Environment Variables

Create a `.env` file in the project root (never commit it):

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/workforce_intelligence
JWT_SECRET_KEY=<random-secret>
GROQ_API_KEY=gsk_...
```

Generate a secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

| Variable | Needed | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | **Yes** | Database connection string |
| `DATABASE_URL_DOCKER` | For Compose | Same, but uses `host.docker.internal` |
| `JWT_SECRET_KEY` | **Yes** | Keeps login sessions secure |
| `GROQ_API_KEY` | **Yes** | AI features (task analysis, chat, safety) |
| `PINECONE_API_KEY` / `PINECONE_INDEX_NAME` | Optional | Company policy knowledge base |
| `LANGCHAIN_TRACING_V2=true` + LangSmith keys | Optional | AI tracing in LangSmith |

---

## Usage

**First-time setup (Manager):** add skills → create employee profiles → assign skills → create a project → break it into tasks → run AI recommendation → approve the best candidate.

**Day to day:** Dashboard shows workload and over-utilisation warnings. Tasks page runs AI matching. AI Chat answers questions from live data.

**Employees:** sign in to see their own profile, workload, and assignments (read-only elsewhere).

**AI safety messages:**
- *normal answer* → allowed
- *Request blocked* → unsafe (passwords, secrets, others' data) — rephrase
- *Request needs review* → risky/unclear — handle via normal approval flow

---

## Testing & Evaluation

```bash
uv run pytest                    # run all tests
python -m evals.run_retrieval_eval   # RAG quality (Recall@3, MRR)
```

CI runs automatically on every push/PR to `main` via GitHub Actions.

---

## Project Structure

```
├── main.py                  # Backend entry point
├── app/
│   ├── auth/                # Login, roles, permissions
│   ├── employees/           # Profiles, skills, workload
│   ├── projects/            # Projects + AI breakdown
│   ├── tasks/               # Tasks, matching scores
│   ├── assignments/         # Approve / reject work
│   ├── agent/               # 8-step AI recommendation workflow
│   ├── rag/                 # Policy knowledge base
│   └── chat/                # AI chat + safety guard
├── streamlit_app/           # Website (pages/ has all screens)
├── evals/                   # RAG evaluation suite
├── tests/                   # Automated tests
└── infra/terraform/         # Infrastructure as code
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Sign-in fails | Backend not running? Check `curl http://localhost:8000/health` |
| Safety check always fails | Check `GROQ_API_KEY` and internet connection |
| AI returns nothing | Ensure employees have skills; re-run `uv run python -m app.rag.ingest` |
| AI code changes not showing | Restart both Streamlit and uvicorn |
| Migration errors | Confirm PostgreSQL is running, then `uv run alembic upgrade head` |
| Docker keeps restarting | `docker compose logs` — usually bad `DATABASE_URL` or missing `.env` |
