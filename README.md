# Workforce Intelligence Platform

AI-powered workforce management platform that helps managers **match the right employee to the right task** using skill-based candidate scoring, workload/availability intelligence, RAG-guided policy awareness, and conversational AI.

The platform combines a **FastAPI** backend (REST + an agentic LangGraph recommendation workflow) with a **Streamlit** frontend and an **AI chat assistant** that can query live platform data and run the recommendation workflow through MCP.

---

## Table of Contents

- [What is this project?](#what-is-this-project)
- [Core features](#core-features)
- [How it works](#how-it-works)
  - [System architecture](#system-architecture)
  - [The 8-node LangGraph recommendation workflow](#the-8-node-langgraph-recommendation-workflow)
  - [Candidate scoring formula](#candidate-scoring-formula)
  - [Data model](#data-model)
- [Project structure](#project-structure)
- [Tech stack](#tech-stack)
- [Getting started (new developer setup)](#getting-started-new-developer-setup)
  - [Prerequisites](#prerequisites)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Configure environment variables](#2-configure-environment-variables)
  - [3. Install dependencies with uv](#3-install-dependencies-with-uv)
  - [4. Create the database](#4-create-the-database)
  - [5. Run database migrations](#5-run-database-migrations)
  - [6. (Optional) Seed the Pinecone knowledge base](#6-optional-seed-the-pinecone-knowledge-base)
  - [7. Start the API server](#7-start-the-api-server)
  - [8. Start the Streamlit frontend](#8-start-the-streamlit-frontend)
- [Docker deployment](#docker-deployment)
- [User manual](#user-manual)
  - [Roles](#roles)
  - [Creating an account](#creating-an-account)
  - [Manager walkthrough](#manager-walkthrough)
  - [Employee walkthrough](#employee-walkthrough)
  - [AI Chat assistant](#ai-chat-assistant)
- [API reference](#api-reference)
- [Environment variables](#environment-variables)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Roadmap ideas](#roadmap-ideas)

---

## What is this project?

**Workforce Intelligence Platform** is an internal tool for engineering teams that:

- Stores **users, employees, skills, projects, tasks, and assignments** in PostgreSQL.
- Computes each employee's **workload** and **availability** from live assignment data.
- Uses an **LLM (Groq)** to analyse a free-text task and extract the target role, required skills, and complexity.
- Runs an **8-node LangGraph agent** that finds, matches, scores, and ranks the best candidates.
- Grounds recommendations in **company policies** retrieved from a Pinecone vector store (RAG).
- Provides a **chat assistant** so managers can query data and generate recommendations in natural language.

## Core features

| Feature | Description |
| --- | --- |
| 🔐 **Role-based auth** | JWT login/register; `manager` and `employee` roles gate API + UI access. |
| 🧑‍💼 **Employee profiles** | Designation, experience, weekly capacity, workload, and skill tags. |
| 🗂️ **Projects & tasks** | Project creation, task creation, task dependencies, status tracking. |
| 📊 **Workload intelligence** | Per-employee allocated hours, workload %, availability, and utilisation alerts. |
| 🧠 **AI task analysis** | LLM extracts role, required skills, and complexity from job descriptions. |
| 🤖 **Candidate recommendation agent** | LangGraph pipeline ranks employees for a task with human-readable explanations. |
| 📜 **RAG policy grounding** | Retrieves relevant assignment/role/project policies from Pinecone to justify recommendations. |
| 💬 **AI chat assistant** | MCP-exposed API tools + LLM agent; managers can talk to their data. |
| 🪄 **Project decomposition** | LLM splits a project description into up to 10 concrete task proposals. |

## How it works

### System architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Streamlit UI (port 8501)                │
│  home · Dashboard · Projects · Tasks · Employees · Skills   │
│  Assignments · AI Chat                                      │
└──────────────────────────────────────┬───────────────────────┘
                                       │ HTTP + JWT (requests)
┌──────────────────────────────────────▼───────────────────────┐
│              FastAPI backend (port 8000, main.py)           │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐ │
│  │ /auth  │ │/skills │ │/employees│ │/projects│ │ /agent     │ │
│  └────────┘ └────────┘ └────────┘ └──┬─────┘ │ (LangGraph) │ │
│        /tasks   /assignments        │       └──────┬───────┘ │
│        /ai (LLM analysis)           │              │         │
│  ┌──────────────────────────────────┼──────────────┼───────┐ │
│  │        app/services matching     │       agent nodes     │ │
│  └──────────────────────────────────┼──────────────┼───────┘ │
└─────────────┬───────────────────────┼──────────────┼─────────┘
              │ SQLAlchemy            │ Groq LLM      │ Pinecone
        ┌─────▼──────┐         ┌──────▼──────┐        ┌▼──────────────┐
        │ PostgreSQL │         │   Groq API  │        │  Vector DB    │
        │  (Alembic) │         │   ChatGroq  │        │ (policies/RAG)│
        └────────────┘         └─────────────┘        └───────────────┘
```

### The 8-node LangGraph recommendation workflow

`POST /agent/recommendations` runs the compiled graph defined in `app/agent/graph.py`.

| # | Node | What it does | Writes to state |
| --- | --- | --- | --- |
| 1 | `task_analyzer` | LLM extracts role, skills, complexity from `task_description` | `target_role`, `required_skills`, `complexity` |
| 2 | `candidate_finder` | Loads every employee profile | `candidate_pool` |
| 3 | `skill_matcher` | Overlaps required skills with each employee's skills | `matched_skills`, `missing_skills`, `skill_score` |
| 4 | `availability_checker` | Remaining hours = capacity − workload | `available_hours`, `availability_ratio` |
| 5 | `workload_checker` | Composite score (see formula) | `scored_candidates` |
| 6 | `rag_retrieval` | Queries Pinecone for relevant policies | `policy_context` |
| 7 | `candidate_ranking` | Sorts by score, keeps top 3 | `scored_candidates` (top 3) |
| 8 | `recommendation` | LLM writes grounded 1–2 sentence explanations | `final_recommendations` |

### Candidate scoring formula

The agent uses a **deterministic composite score** in `workload_checker_node`:

```
match_score = (skill_score × 0.60) + (availability_ratio × 0.40)
```

A second scoring path (`/tasks/{id}/candidates`, `app/services/matching.py`) weights four factors:

```
final_score = skill_score×0.40 + availability_score×0.25 + workload_score×0.20 + experience_score×0.15
```

Skill proficiency maps to points: **Beginner = 50**, **Intermediate = 75**, **Advanced = 100**.

### Data model

```
users ──────────► employees ──► employee_skills ──► skills
  │                  │  ▲
  │                  │  │ (assigned to)
  │                  ▼  │
  └─► projects ──► tasks ──► assignments (task_id, employee_id, hours)
                       │
                       └──► task_dependencies
```

- **users** — `name`, `email`, `password_hash`, `role` (`manager` / `employee`)
- **employees** — `user_id`, `designation`, `experience_years`, `weekly_capacity`, `current_workload`
- **skills** — `name` (unique)
- **employee_skills** — `employee_id`, `skill_id`, `proficiency_level`
- **projects** — `title`, `description`, `status` (`planning`, `in_progress`, `completed`)
- **tasks** — `project_id`, `title`, `description`, `estimated_hours`, `status` (`todo`, `in_progress`, `completed`)
- **task_dependencies** — `task_id`, `prerequisite_task_id`
- **assignments** — `task_id`, `employee_id`, `allocated_hours`, `status` (`active`, `completed`, `cancelled`)

## Project structure

```
workforce-intelligence-platform/
├── main.py                     # FastAPI app; includes all routers
├── pyproject.toml              # uv project metadata + dependencies
├── uv.lock                     # Locked dependency set (reproducible installs)
├── alembic.ini                 # Alembic config
├── alembic/                    # Database migration scripts
│   └── versions/
├── Dockerfile                  # Container image (uv-based, python:3.11-slim)
├── .dockerignore
├── app/
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models/                 # SQLAlchemy ORM models
│   ├── auth/                   # Register/login, JWT, role dependencies
│   ├── skills/                 # Skill catalogue CRUD
│   ├── employees/              # Employee CRUD, skills, workload, availability
│   ├── projects/               # Projects CRUD + LLM task decomposition + approval
│   ├── tasks/                  # Tasks CRUD, dependencies, candidate scoring
│   ├── assignments/            # Assignment create/approve/reject + capacity checks
│   ├── ai/                     # Groq LLM: task analysis, candidate evaluation, reasoning
│   ├── agent/                  # LangGraph state, nodes, graph, /agent/recommendations
│   ├── rag/                    # Pinecone vector store, retriever, knowledge ingestion
│   ├── chat/                   # MCP-backed AI chat assistant + terminal bot
│   └── services/               # matching.py, task_decomposer.py, assignment_service.py
├── streamlit_app/
│   ├── home.py                 # Login/register and landing
│   ├── api_client.py           # HTTP client for the backend
│   ├── ui.py                   # Shared CSS components (cards, KPIs, badges)
│   └── pages/                  # Dashboard, My Workspace, Projects, Tasks, Employees,
│                               # Skills, Assignments, AI Chat, View Tasks
└── .streamlit/config.toml      # Streamlit theme + headless config
```

## Tech stack

- **Language / runtime:** Python 3.11
- **API framework:** FastAPI + Uvicorn
- **Package manager:** uv (locked via `uv.lock`)
- **Database / ORM:** PostgreSQL + SQLAlchemy 2.0 + Alembic migrations
- **LLM provider:** Groq (`langchain-groq` / `ChatGroq`)
- **Agent framework:** LangGraph
- **Vector search / RAG:** Pinecone (`langchain-pinecone`) + FastEmbed (`BAAI/bge-small-en-v1.5`)
- **Tool bridge / MCP:** FastMCP (`FastMCP.from_fastapi`)
- **Frontend:** Streamlit
- **Auth:** JWT (PyJWT) + Argon2 password hashing (`pwdlib`)
- **Observability (optional):** LangSmith

## Getting started (new developer setup)

### Prerequisites

- **git**
- **Python 3.11** (the repo pins `.python-version` to `3.11`)
- **[uv](https://docs.astral.sh/uv/)** (fast Python package & environment manager)
- **PostgreSQL** running locally (or a remote DB URL)
- **Pinecone** account + index (only needed for the RAG features / recommendations)
- **Groq** API key (for all LLM/AI features)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/workforce-intelligence-platform.git
cd workforce-intelligence-platform
```

### 2. Configure environment variables

Create a `.env` file in the project root (`.env` is git-ignored). At a minimum you need:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/workforce_intelligence
JWT_SECRET_KEY=generate-a-random-secret
GROQ_API_KEY=gsk_...
```

Optional, for RAG / observability:

```bash
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=workforce-policies
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=workforce-intelligence-platform
```

> Generate a secure `JWT_SECRET_KEY` with:
> `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 3. Install dependencies with uv

```bash
uv sync          # creates a `.venv` and installs everything in uv.lock
```

> On Windows, activate the environment with:
> `.\\.venv\\Scripts\\Activate.ps1`

### 4. Create the database

```sql
CREATE DATABASE workforce_intelligence;
```

Make sure the user/password in `DATABASE_URL` can connect to it.

### 5. Run database migrations

```bash
uv run alembic upgrade head
```

This applies the migrations in `alembic/versions/` and creates all tables.

### 6. (Optional) Seed the Pinecone knowledge base

If you want RAG-grounded recommendations, index the policy files in `app/rag/knowledge/`:

```bash
uv run python -m app.rag.ingest
```

This pushes `assignment_policies.txt`, `role_guidelines.txt`, and `project_standards.txt` as embeddings into your Pinecone index.

### 7. Start the API server

```bash
uv run uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.

- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

### 8. Start the Streamlit frontend

In a second terminal:

```bash
uv run streamlit run streamlit_app/home.py
```

Open **http://localhost:8501** and log in (or create an account).

---

## Docker deployment

The included `Dockerfile` builds the app with uv and runs the API with uvicorn.

```bash
docker build -t workforce-api:latest .
```

Run it, forwarding your `.env` and pointing `DATABASE_URL` at the host's PostgreSQL
(use `host.docker.internal` on Docker Desktop for Windows/Mac):

```bash
docker run -d --name workforce-api -p 8000:8000 --env-file .env \
  -e DATABASE_URL="postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/workforce_intelligence" \
  workforce-api:latest
```

> Note: the container only serves the API. The Streamlit UI is designed to run on the host
> and talk to `http://127.0.0.1:8000` (see `streamlit_app/api_client.py`), so update
> `API_BASE_URL` there if your API is hosted remotely.

## User manual

### Roles

| Role | Access |
| --- | --- |
| **manager** | Everything: create projects/tasks/employees/skills, run recommendations, approve assignments, AI chat. |
| **employee** | Read-only: own workspace, workload/availability, assigned work, view projects/tasks. |

### Creating an account

1. Open the Streamlit app at **http://localhost:8501**.
2. Choose **Create an account**, fill in your name/email/password, pick `employee` or `manager`, and submit.
3. Sign in; the dashboard loads.

### Manager walkthrough

1. **Add employees** → `Employees` page → create a profile (linked to a registered user), then assign skills with proficiency levels.
2. **Add skills** → `Skills` page → build the skill catalogue (used for matching).
3. **Create projects** → `Projects` page → add a project title + description.
4. **Decompose a project** (optional) → on the project, ask the LLM to break it into up to 10 tasks, then approve all or individually.
5. **Add tasks** → `Tasks` page → give a title, description, and estimated hours.
6. **Match candidates** → on a task, view candidate scoring (`/tasks/{id}/candidates`) or use the **AI Chat** to run the recommendation workflow.
7. **Create assignments** → `Assignments` page → assign hours. Capacity is enforced on approve (`/assignments/approve`).
8. **Monitor** → `Dashboard` shows workload by employee, project pipeline, utilisation alerts, and an employee utilisation table.

### Employee walkthrough

1. `home` shows your **My workspace**: allocated hours, capacity, workload %, and your skills.
2. `My Workspace` page shows details + your assignments.
3. `View Tasks` lets you browse projects and their tasks read-only.

### AI Chat assistant

The **AI Chat** page (`7_AI_Chat.py`) wires the FastAPI app into an MCP server via
`FastMCP.from_fastapi` and lets an LLM agent call a (managers can see all) subset of tools:

- who’s available, workload, skills (`/employees`, `/skills`)
- projects, tasks, dependencies, assignments
- `POST /agent/recommendations` — run the full recommendation workflow
- create / approve / reject assignments

Example questions you can ask:

- *"Who is free this week?"*
- *"Recommend employees for: build a Python FastAPI auth module."* (runs the LangGraph agent)
- *"Assign Sarah to the API task with 20 hours."*
- *"What projects are in progress?"*

> The agent never finalises work on its own — assignment approvals/policy checks are enforced
> on the backend, so recommendations are advisory (human-in-the-loop).

## API reference

> All endpoints below (except `/auth/*`) require a `Authorization: Bearer <token>` header.
> Manager-only endpoints return `403` for employees.

| Method | Endpoint | Description | Who |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Create user (`name`, `email`, `password`, `role`) | open |
| `POST` | `/auth/login` | OAuth2 form login (`username`=email) → JWT | open |
| `GET` | `/auth/me` | Current user claims | auth user |
| `GET` | `/auth/users` | List users | manager |
| `GET` | `/auth/manager-only` | Manager dashboard check | manager |
| `POST/GET` | `/skills/` | Create / list skills | create=manager |
| `POST` | `/employees/` | Create employee profile | manager |
| `GET` | `/employees/` | List employees | auth user |
| `GET` | `/employees/{id}` | One employee | auth user |
| `POST` | `/employees/{id}/skills` | Assign skill with proficiency | manager |
| `GET` | `/employees/{id}/skills` | Employee skills | auth user |
| `GET` | `/employees/{id}/workload` | Allocated hours, %, status | auth user |
| `GET` | `/employees/{id}/availability` | Available hours, capacity % | auth user |
| `POST/GET` | `/projects/` | Create / list projects | create=manager |
| `GET` | `/projects/{id}` | One project | auth user |
| `POST` | `/projects/{id}/decompose` | LLM → up to 10 task proposals | manager |
| `POST` | `/projects/{id}/tasks/approve-proposal` | Save one proposed task | manager |
| `POST` | `/projects/{id}/tasks/approve-all` | Save batch of proposed tasks | manager |
| `POST` | `/tasks/` | Create task | manager |
| `GET` | `/tasks/project/{project_id}` | List tasks for a project | auth user |
| `GET` | `/tasks/{id}` | One task | auth user |
| `POST` | `/tasks/{id}/dependencies` | Add prerequisite dependency | manager |
| `GET` | `/tasks/{id}/dependencies` | List dependencies | auth user |
| `GET` | `/tasks/{id}/candidates` | Deterministic weighted candidate scores | manager |
| `POST` | `/tasks/{id}/agent-recommendations` | Run the LangGraph workflow for an existing task | manager |
| `POST` | `/assignments/` | Create assignment (adds workload) | manager |
| `GET` | `/assignments/` | List assignments | auth user |
| `GET` | `/assignments/employee/{employee_id}` | Assignments for an employee | auth user |
| `POST` | `/assignments/approve` | Capacity-checked approval → `active` | manager |
| `POST` | `/assignments/reject` | Record rejection reason | manager |
| `POST` | `/ai/analyze-task` | LLM: role/skills/complexity from description | manager |
| `POST` | `/agent/recommendations` | Full 8-node recommendation workflow | manager |

## Environment variables

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| `DATABASE_URL` | ✅ | SQLAlchemy DB connection URL | `postgresql+psycopg2://user:pw@localhost:5432/workforce_intelligence` |
| `JWT_SECRET_KEY` | ✅ | HS256 signing secret | random base64 string |
| `GROQ_API_KEY` | ✅ (AI features) | Groq LLM key | `gsk_...` |
| `PINECONE_API_KEY` | ⚠️ (RAG) | Pinecone key | `pcsk_...` |
| `PINECONE_INDEX_NAME` | ⚠️ (RAG) | Vector index name | `workforce-policies` |
| `LANGCHAIN_ENDPOINT` | ⚠️ (obs) | LangSmith endpoint | `https://api.smith.langchain.com` |
| `LANGCHAIN_API_KEY` | ⚠️ (obs) | LangSmith key | `lsv2_pt_...` |
| `LANGCHAIN_PROJECT` | ⚠️ (obs) | LangSmith project name | `workforce-intelligence-platform` |
| `LANGCHAIN_TRACING_V2` | ⚠️ (obs) | Enable tracing | `true` |

## Troubleshooting & FAQ

**`RuntimeError: cannot import name 'Crypto' from 'psycopg2'` / psycopg2 build errors**
→ The project ships `psycopg2-binary`, so installs work without a C compiler. If you still hit
build issues, make sure `uv sync` used the locked `uv.lock`.

**`KeyError: 'task_description'` when running the agent**
→ This was a stale-code issue: the FastMCP in-process server caches the FastAPI app the first
time the AI chat assistant is constructed. After editing `app/agent/*`, fully **restart
Streamlit** (and uvicorn) — `uvicorn --reload` alone does not reload Streamlit's cached modules.

**Recommendations are empty or no employees matched**
→ Make sure employees exist, have skills assigned, and Pinecone is seeded if you expect policy
context. Check `PINECONE_API_KEY`/`PINECONE_INDEX_NAME`.

**Groq calls fail**
→ Verify `GROQ_API_KEY` and that the model identifier in `app/ai/task_analyzer.py` /
`app/chat/assistant.py` is still available on your Groq account.

**Migrations fail**
→ Confirm `DATABASE_URL` is set and the DB exists; then `uv run alembic upgrade head` again.

**AI chat calls tools with the wrong arguments**
→ The chat tool allowlist (`ALLOWED_TOOL_NAMES` in `app/chat/assistant.py`) is also trusted to
filter what the UI binds. Keep the tool names stable — they are derived from FastAPI operation
IDs/paths, so renaming routes changes them.

## Roadmap ideas

- Cancel/complete assignment transitions that decrement cached workload.
- Unify the two capacity-authority sources (cached `current_workload` vs. live assignment sums).
- Add test coverage (pytest) for the scoring math and the LangGraph pipeline.
- Store RAG sources/metadata in responses for auditability.
- Add CI (`uv sync --frozen` + lint + tests) and a compose file for Postgres + API + UI.