# Workforce Intelligence Platform

**A smart way to decide who on your team should do which task.**

This is an internal tool for teams and managers. It keeps track of your people, their
skills, and how busy they are. When you have a new task, it suggests the best person
for the job — and explains why.

You do **not** need to be a programmer to use it. This README has two parts:

- **[Part 1 — User guide](#part-1--user-guide-no-technical-knowledge-needed):**
  what the tool does and how to use it, in plain English.
- **[Part 2 — Setup guide for developers](#part-2--setup-guide-for-developers):**
  how to install and run the software.

---

## Table of Contents

- [Part 1 — User guide (no technical knowledge needed)](#part-1--user-guide-no-technical-knowledge-needed)
  - [What is this?](#what-is-this)
  - [What can it do?](#what-can-it-do)
  - [The two types of users](#the-two-types-of-users)
  - [How to open the app and sign in](#how-to-open-the-app-and-sign-in)
  - [A map of every page](#a-map-of-every-page)
  - [Manager walkthrough (step by step)](#manager-walkthrough-step-by-step)
  - [Employee walkthrough (step by step)](#employee-walkthrough-step-by-step)
  - [Using the AI Chat assistant](#using-the-ai-chat-assistant)
  - [What the AI safety messages mean](#what-the-ai-safety-messages-mean)
  - [How the AI chooses the best person (explained simply)](#how-the-ai-chooses-the-best-person-explained-simply)
- [Part 2 — Setup guide for developers](#part-2--setup-guide-for-developers)
  - [The easy way: Docker Compose (recommended)](#the-easy-way-docker-compose-recommended)
  - [The manual way: run it yourself](#the-manual-way-run-it-yourself)
  - [Environment variables](#environment-variables)
  - [Running the tests](#running-the-tests)
  - [How the system is built (architecture)](#how-the-system-is-built-architecture)
  - [What happens when you press "Run AI recommendation"](#what-happens-when-you-press-run-ai-recommendation)
  - [Project folders](#project-folders)
  - [Technology used](#technology-used)
  - [API reference (for developers)](#api-reference-for-developers)
  - [Troubleshooting](#troubleshooting)
  - [Roadmap ideas](#roadmap-ideas)

---

# Part 1 — User guide (no technical knowledge needed)

## What is this?

Imagine your team has 10 tasks to finish this week and 12 people available.
Which person should get which task? Some people are skilled but overloaded.
Some are free but lack the right skills.

**Workforce Intelligence Platform answers that question for you.**

You type in a task (in plain words). The system:

1. **Understands the task** — what kind of role is needed, which skills, how hard it is.
2. **Checks everyone** — who has the skills, who has free time, who is already overloaded.
3. **Scores and ranks people** — the best match comes first.
4. **Explains the choice** — in a short, human-readable sentence.
5. **Checks your company rules** — so the suggestion follows your policies.

A manager then reviews the suggestion and approves it. The AI never assigns work
on its own — a human always makes the final decision.

## What can it do?

| Feature | What it means for you |
| --- | --- |
| **Employee profiles** | Keep a record of every person: their job title, experience, skills, and how many hours per week they can work. |
| **Skill catalogue** | A shared list of skills (e.g. "Python", "Testing", "Project Planning") used to match people to tasks. |
| **Projects and tasks** | Create projects, break them into tasks, set how many hours each task should take, and track status. |
| **AI project breakdown** | Describe a whole project in one paragraph and the AI suggests up to 10 tasks for it. You approve them one by one or all at once. |
| **Workload and availability** | The system always knows how many hours each person has committed vs. their weekly capacity, and warns you when someone is over-utilised. |
| **AI recommendations** | One click suggests the best employees for a task, with scores and reasons. |
| **Company policy awareness** | The AI reads your written company policies before suggesting, so recommendations respect your rules. |
| **AI Chat** | Ask questions in plain language — "Who is free this week?" — and get answers from live data. |
| **Safety checks** | Every chat message is checked first. Dangerous requests (passwords, secrets) are blocked; risky ones are flagged for review. |
| **Two-level access** | Managers can change things. Employees can view their own work. |

## The two types of users

| Role | Can do | Cannot do |
| --- | --- | --- |
| **Manager** | Everything: add people and skills, create projects and tasks, run AI recommendations, approve or reject assignments, use AI Chat. | — |
| **Employee** | See their own profile, skills, workload, and assignments. Browse projects and tasks in read-only mode. | Create or change anything. |

> If an employee tries to open a manager-only page, the app will simply say
> you do not have access.

## How to open the app and sign in

**Step 1.** Open the app in your web browser. Your administrator will give you
the address. When running on your own computer, it is:

```
http://localhost:8501
```

**Step 2.** You will see a **Sign in** screen.

- Already have an account? Enter your email and password, then press **Sign In**.
- New here? Press **Create an account**, fill in your name, email, and password,
  choose your role (`employee` or `manager`), and press **Create Account**.
  Then sign in.

**Step 3.** After signing in you land on your home page.

- **Managers** see the "Workspace at a glance" panel with quick buttons.
- **Employees** see "My workspace" with their own hours and skills.

## A map of every page

| Page | What it is for | Who can use it |
| --- | --- | --- |
| **Home** | Sign in / register. After login: a quick overview and shortcut buttons. | Everyone |
| **Dashboard** | Big-picture view: workload by employee, project pipeline, over-utilisation warnings, and a utilisation table. | Manager |
| **My Workspace** | Your own profile, skills, assigned work, and workload bar. | Everyone |
| **Projects** | Create projects. Use AI to break a project into tasks. See all projects. | Manager (viewing for all) |
| **View Tasks** | Browse projects and their tasks in read-only mode. | Everyone |
| **Tasks** | Create tasks, run AI candidate matching, and approve or reject assignments. | Manager |
| **Employees** | Create employee profiles, assign skills, see who is busy and who is free. | Manager |
| **Skills** | Maintain the skill catalogue used for matching. | Manager |
| **Assignments** | A log of who is working on what: hours, status, and totals. | Manager |
| **AI Chat** | Talk to your data in plain language. | Everyone (tools are filtered by role) |

## Manager walkthrough (step by step)

Follow these steps the first time you set the system up, then use it day to day.

### Step 1 — Add skills

1. Open the **Skills** page.
2. Under **Add a skill**, type a skill name (for example `Python`, `React`,
   `QA Testing`, `Client Communication`).
3. Press **Add**. Repeat for each skill your team needs.

*Why first?* Matching works by comparing tasks against these skills.

### Step 2 — Add your people

1. Open the **Employees** page.
2. Under **Create employee profile**, fill in the details: name (the person's
   user account), job title, years of experience, and weekly capacity
   (how many hours per week they can work — usually 40).
3. Press **Create**.
4. Under **Assign a skill**, pick the employee and a skill, choose their level
   (`Beginner`, `Intermediate`, or `Advanced`), and save.
5. Repeat until everyone has their skills.

### Step 3 — Create a project

1. Open the **Projects** page.
2. Under **Create a project**, enter a title and a short description
   (e.g. "Customer Portal — Phase 1").
3. Press **Create**.

### Step 4 — Break the project into tasks (AI helper)

1. On the **Projects** page, find your project and open
   **AI Project Decomposition**.
2. Press the button to let the AI split your project description into
   up to 10 concrete tasks.
3. Read the proposed tasks. Approve them **one by one** or press
   **Approve all**. You can also discard the ones you do not want.

*Prefer to do it yourself?* Skip this and add tasks manually in Step 5.

### Step 5 — Add tasks by hand (optional)

1. Open the **Tasks** page.
2. Under **Add a task**, choose the project, enter a title, a description,
   and the estimated number of hours.
3. Press **Create**. Repeat for each task.

### Step 6 — Find the best person for a task (the AI part)

1. On the **Tasks** page, scroll to **Work with a task** and select a task
   from the dropdown.
2. Choose one of two buttons:
   - **Run LangGraph Agent** — the full AI. It reads the task, works out the
     role, skills, and difficulty, checks company policies, and returns the
     **top 3 candidates** with a short explanation each.
   - **Run candidate matching** — a quick, formula-based ranking of all
     employees (no AI, just numbers: skills, free time, workload, experience).
3. Read the results. Each candidate shows a score and a breakdown
   (skills / availability / workload / experience).

### Step 7 — Assign the work

1. Next to the candidate you like: enter the **hours to allocate**.
2. Tick the **Confirm** checkbox.
3. Press **✅ Approve**. The assignment becomes active and the person's
   workload updates immediately.
4. Not the right person? Press **❌ Reject** and pick someone else.

> The system checks capacity during approval. If someone does not have enough
> free hours, the approval is refused.

### Step 8 — Monitor progress

1. Open the **Dashboard**.
2. You will see: workload per employee (bars), project pipeline
   (planning / in progress / completed), **utilisation warnings** (people who
   are over or under loaded), and a full utilisation table.
3. Open **Assignments** for a complete log of who is doing what, with hours
   and status totals.

## Employee walkthrough (step by step)

1. **Sign in** with the account your manager created for you.
2. On the **Home** page you see **My workspace**:
   - your title and experience,
   - hours allocated this week vs. your capacity,
   - a workload bar with your status (e.g. `ok`, `busy`, `overloaded`),
   - your skills as tags.
3. Open **My Workspace** for full details and a list of **My assignments**
   (which tasks, how many hours, and their status).
4. Open **View Tasks** to browse projects and tasks in read-only mode.
5. That's it. Your workload updates automatically whenever a manager
   assigns you work.

> **Note:** If your home page says no employee profile is linked to your
> account, ask a manager to link your user account to an employee record
> on the Employees page.

## Using the AI Chat assistant

1. Open the **AI Chat** page.
2. Type a question in plain English and press Enter.

The assistant can look up live data and, for managers, even run the
recommendation workflow or create/approve assignments.

**Examples you can try:**

| Question | What happens |
| --- | --- |
| "Who is free this week?" | Lists employees with free hours. |
| "What projects are in progress?" | Lists current projects and their status. |
| "Show me the skills of employee #3." | Returns that person's skills. |
| "Recommend employees for: build a FastAPI authentication module." | Runs the full AI recommendation workflow and returns ranked candidates. |
| "Assign Sarah to the API task with 20 hours." | Creates the assignment (manager only). |
| "What is the workload of the design team?" | Returns hours, capacity, and utilisation. |

**Good to know:**

- The chat remembers the current conversation, so you can ask follow-ups.
- All real changes still go through the same safety checks as the pages —
  approvals and capacity rules are enforced by the backend, not by the AI.

## What the AI safety messages mean

Every message you type is first checked by a **safety guard** (a second AI
whose only job is to classify your request). You will see one of three results:

| Message | Meaning | What to do |
| --- | --- | --- |
| *(normal answer)* | Your request was allowed — it is a normal workforce question. | Nothing. Continue. |
| **"Request blocked: …"** | The request tried to do something unsafe — reveal passwords or credentials, expose hidden instructions, bypass security, or disclose sensitive personal information. | Rephrase your question. The guard never lets these through. |
| **"Request needs review: …"** | The request was unclear, needs manager approval, could overload one person, or judges an employee without enough data. | Re-read the reason. If it is a real risk, handle it through the normal approval flow instead of the chat. |

> If a safety check fails (for example, the AI service is unavailable), the
> system automatically treats the message as **"needs review"** rather than
> letting it through unchecked.

## How the AI chooses the best person (explained simply)

There is **no magic** — just a clear score that you can read:

**The AI agent (recommended list)** scores each person like this:

```
Score = (Skills match × 60%) + (Free time × 40%)
```

- **Skills match** — how many of the task's required skills the person has,
  and how good they are (Beginner = 50, Intermediate = 75, Advanced = 100).
- **Free time** — how much of their weekly capacity is still unused.

**The quick matching button** uses four factors instead:

```
Score = Skills (40%) + Free time (25%) + Current workload (20%) + Experience (15%)
```

Before suggesting anyone, the AI also:

1. reads your written **company policies** (stored in a searchable knowledge
   base) so the suggestion follows your rules, and
2. writes a **one- or two sentence reason** for each suggestion.

The top 3 people are shown, ranked. **You** decide who actually gets the task.

---

# Part 2 — Setup guide for developers

## The easy way: Docker Compose (recommended)

Docker Compose starts the whole system (backend + website) with one command.

**What you need installed:**

1. [Docker](https://docs.docker.com/get-docker/) (with Docker Compose)
2. **PostgreSQL** running on your machine (port 5432) — Compose does *not*
   include the database itself.
3. A `.env` file in the project root (see [Environment variables](#environment-variables)).
   For Compose you need `DATABASE_URL_DOCKER`, which is like `DATABASE_URL`
   but points at `host.docker.internal` instead of `localhost`.

**Commands you will use:**

```bash
docker compose up --build -d     # start everything (build first time)
docker compose ps                # check it is running
docker compose logs -f           # watch the logs (Ctrl+C to stop watching)
docker compose logs -f api       # backend logs only
docker compose logs -f frontend  # website logs only
docker compose restart           # restart after a change
docker compose down              # stop and remove the containers
```

**Check that it works:**

```bash
curl http://localhost:8000/health     # returns {"status": "healthy"}
```

Then open **http://localhost:8501** in your browser.

> The containers automatically check the API's health and restart if it fails.

## The manual way: run it yourself

Use this if you are developing the code and want things to restart as you edit.

**What you need:**

- [git](https://git-scm.com/)
- **Python 3.11**
- [uv](https://docs.astral.sh/uv/) — a fast Python package manager
- **PostgreSQL**
- A [Groq](https://console.groq.com/) API key (needed for all AI features)
- A [Pinecone](https://www.pinecone.io/) account (optional — only for the
  policy-aware recommendations)

**1. Download the code:**

```bash
git clone https://github.com/muhammedriswanp/workforce-intelligence-platform.git
cd workforce-intelligence-platform
```

**2. Create a `.env` file** in the project root (this file is ignored by git,
so your secrets stay private). Minimum contents:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/workforce_intelligence
JWT_SECRET_KEY=generate-a-random-secret
GROQ_API_KEY=gsk_...
```

Generate a safe secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**3. Install the dependencies:**

```bash
uv sync
```

**4. Create the database** (once):

```sql
CREATE DATABASE workforce_intelligence;
```

**5. Create the tables:**

```bash
uv run alembic upgrade head
```

**6. (Optional) Load the company policies** into the knowledge base:

```bash
uv run python -m app.rag.ingest
```

This uploads the policy files from `app/rag/knowledge/` so the AI can search
them when making recommendations.

**7. Start the backend** (terminal 1):

```bash
uv run uvicorn main:app --reload
```

- API address: http://127.0.0.1:8000
- Interactive API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

**8. Start the website** (terminal 2):

```bash
uv run streamlit run streamlit_app/home.py
```

Open **http://localhost:8501** and sign in.

**Docker for the API only** (instead of Compose):

```bash
docker build -t workforce-api:latest .
docker run -d --name workforce-api -p 8000:8000 --env-file .env \
  -e DATABASE_URL="postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/workforce_intelligence" \
  workforce-api:latest
```

## Environment variables

Everything the app needs is listed in the `.env` file.

| Variable | Needed? | What it is (plain English) |
| --- | --- | --- |
| `DATABASE_URL` | **Yes** | Where the database lives, including username and password. |
| `DATABASE_URL_DOCKER` | For Compose | Same thing, but written for Docker (`host.docker.internal`). |
| `JWT_SECRET_KEY` | **Yes** | A private secret that keeps log-in sessions secure. Never share it. |
| `GROQ_API_KEY` | **Yes** for AI | Key for the Groq AI service (task analysis, chat, safety checks). |
| `PINECONE_API_KEY` | Optional | Key for the Pinecone knowledge base (company policies). |
| `PINECONE_INDEX_NAME` | Optional | Name of the policy search index in Pinecone. |
| `LANGCHAIN_TRACING_V2` | Optional | `true` turns on AI tracing (watching how the AI works) in LangSmith. |
| `LANGCHAIN_ENDPOINT` | Optional | Where to send those traces (usually `https://api.smith.langchain.com`). |
| `LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY` | Optional | Your LangSmith key, if you use tracing. |
| `LANGCHAIN_PROJECT` | Optional | The name your traces are grouped under. |
| `LANGSMITH_TRACING` / `LANGSMITH_ENDPOINT` | Optional | Newer names for the same tracing settings. |

> Never commit the `.env` file. It is listed in `.gitignore` on purpose.

## Running the tests

```bash
uv run pytest                        # run all tests
uv run pytest tests/test_safety_guard.py -v -s   # just the AI safety tests
```

The test suite checks:

- **Health tests** (`tests/test_health.py`) — the API starts and its
  `/` and `/health` endpoints answer correctly.
- **Safety guard tests** (`tests/test_safety_guard.py`) — 10 example messages
  are classified correctly (`allow`, `block`, or `review`): normal requests
  pass, password/secret/jailbreak requests are blocked, and risky ones
  (like overloading one person) are flagged for review.

**Continuous integration (CI):** every push and pull request to `main` runs
automatically on GitHub Actions (`.github/workflows/ci.yml`). It installs the
locked dependencies, runs the tests, and builds the Docker image — so broken
changes are caught before they reach anyone.

## How the system is built (architecture)

```
┌──────────────────────────────────────────────────────────────┐
│                  Website — Streamlit (port 8501)             │
│  Home · Dashboard · Projects · Tasks · Employees · Skills    │
│  Assignments · AI Chat                                       │
└──────────────────────────────┬───────────────────────────────┘
                               │  HTTP requests + login token
┌──────────────────────────────▼───────────────────────────────┐
│                 Backend — FastAPI (port 8000)                │
│   auth · skills · employees · projects · tasks · assignments │
│   ai (task analysis) · agent (AI recommendation workflow)    │
└──────┬────────────────────────┬─────────────────┬────────────┘
       │                        │                 │
┌──────▼──────┐          ┌──────▼──────┐   ┌──────▼──────────┐
│ PostgreSQL  │          │  Groq (AI)  │   │ Pinecone        │
│ (your data) │          │  language   │   │ (company policy │
│             │          │  models     │   │  knowledge)     │
└─────────────┘          └─────────────┘   └─────────────────┘
```

In plain English: the **website** talks to the **backend**; the backend stores
data in **PostgreSQL**, asks **Groq** (the AI) to analyse tasks and chat, and
searches **Pinecone** for your company policies.

**Data model** (how the information is organised):

```
users ──────────► employees ──► employee_skills ──► skills
  │                  │  ▲
  │                  │  │ (assigned to)
  │                  ▼  │
  └─► projects ──► tasks ──► assignments (task, employee, hours)
                       │
                       └──► task_dependencies (task B needs task A first)
```

- **users** — login accounts (name, email, password, role)
- **employees** — job title, experience, weekly capacity, current workload
- **skills** / **employee_skills** — the skill list and each person's level
- **projects** — title, description, status
- **tasks** — the work items inside a project, with estimated hours
- **assignments** — "this employee works on this task for N hours"
- **task_dependencies** — tasks that must finish before others start

## What happens when you press "Run AI recommendation"

The backend runs a **workflow of 8 steps** (built with LangGraph), one after
another:

| # | Step | Plain-English explanation |
| --- | --- | --- |
| 1 | Analyse the task | AI reads the task and works out the role, skills, and difficulty. |
| 2 | Collect people | Loads every employee profile. |
| 3 | Match skills | Compares required skills with each person's skills. |
| 4 | Check free time | Calculates remaining hours: capacity − current workload. |
| 5 | Score | Combines skills and availability into a score (60/40). |
| 6 | Fetch policies | Searches the knowledge base for relevant company rules. |
| 7 | Rank | Sorts by score and keeps the top 3. |
| 8 | Explain | AI writes a short, policy-aware reason for each suggestion. |

The result is returned to the screen (or to the chat), where a manager can
approve or reject it.

## Project folders

```
workforce-intelligence-platform/
├── main.py                  # Starts the backend, adds all routes, /health
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Locked dependency versions (reproducible installs)
├── compose.yaml             # Docker Compose: backend + website together
├── Dockerfile               # Backend image
├── Dockerfile.streamlit     # Website image
├── alembic.ini + alembic/   # Database table creation scripts (migrations)
├── .github/workflows/ci.yml # Automatic tests on every push (GitHub Actions)
├── app/
│   ├── database.py          # Database connection
│   ├── models/              # Database table definitions
│   ├── auth/                # Register, login, roles, permissions
│   ├── skills/              # Skill catalogue
│   ├── employees/           # Employee profiles, skills, workload, availability
│   ├── projects/            # Projects + AI project breakdown
│   ├── tasks/               # Tasks, dependencies, candidate scores
│   ├── assignments/         # Assigning work, approving, rejecting
│   ├── ai/                  # AI task analysis and reasoning
│   ├── agent/               # The 8-step recommendation workflow
│   ├── rag/                 # Company policy knowledge base + search
│   ├── chat/                # AI Chat assistant + safety guard
│   └── services/            # Shared logic (matching, task breakdown)
├── streamlit_app/
│   ├── home.py              # Sign in / register / home page
│   ├── api_client.py        # Talks to the backend
│   ├── ui.py                # Shared styling
│   └── pages/               # All the inner pages (Dashboard, Tasks, ...)
├── tests/                   # Automated tests
└── .streamlit/config.toml   # Website theme settings
```

## Technology used

| Layer | Technology |
| --- | --- |
| Language | Python 3.11 |
| Backend | FastAPI + Uvicorn |
| Website | Streamlit |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| AI models | Groq (via `langchain-groq`) |
| AI workflow | LangGraph |
| Policy search (RAG) | Pinecone + FastEmbed |
| Tool bridge for chat | FastMCP |
| Login security | JWT + Argon2 password hashing |
| AI safety checks | Guardrails AI |
| Package management | uv |
| Testing / CI | pytest + GitHub Actions |
| Optional monitoring | LangSmith |

## API reference (for developers)

> All endpoints except `/auth/*` need the header
> `Authorization: Bearer <token>`. Manager-only endpoints return `403`
> for employees.

| Method | Endpoint | Description | Who |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Create account | Anyone |
| `POST` | `/auth/login` | Sign in → get token | Anyone |
| `GET` | `/auth/me` | Your own profile | Logged in |
| `GET` | `/auth/users` | List users | Manager |
| `POST/GET` | `/skills/` | Create / list skills | Create = Manager |
| `POST` | `/employees/` | Create employee profile | Manager |
| `GET` | `/employees/` | List employees | Logged in |
| `GET` | `/employees/{id}` | One employee | Logged in |
| `POST/GET` | `/employees/{id}/skills` | Give / list skills | Create = Manager |
| `GET` | `/employees/{id}/workload` | Hours, %, status | Logged in |
| `GET` | `/employees/{id}/availability` | Free hours, capacity % | Logged in |
| `POST/GET` | `/projects/` | Create / list projects | Create = Manager |
| `GET` | `/projects/{id}` | One project | Logged in |
| `POST` | `/projects/{id}/decompose` | AI → up to 10 task ideas | Manager |
| `POST` | `/projects/{id}/tasks/approve-proposal` | Save one proposed task | Manager |
| `POST` | `/projects/{id}/tasks/approve-all` | Save all proposed tasks | Manager |
| `POST` | `/tasks/` | Create task | Manager |
| `GET` | `/tasks/project/{project_id}` | Tasks of a project | Logged in |
| `GET` | `/tasks/{id}` | One task | Logged in |
| `POST/GET` | `/tasks/{id}/dependencies` | Add / list prerequisites | Manager / Logged in |
| `GET` | `/tasks/{id}/candidates` | Formula-based candidate scores | Manager |
| `POST` | `/tasks/{id}/agent-recommendations` | Run the AI workflow for a task | Manager |
| `POST/GET` | `/assignments/` | Create / list assignments | Create = Manager |
| `GET` | `/assignments/employee/{id}` | One person's assignments | Logged in |
| `POST` | `/assignments/approve` | Approve (checks capacity) → active | Manager |
| `POST` | `/assignments/reject` | Reject with a reason | Manager |
| `POST` | `/ai/analyze-task` | AI: role / skills / complexity | Manager |
| `POST` | `/agent/recommendations` | Full 8-step AI workflow | Manager |
| `GET` | `/` | Service info | Anyone |
| `GET` | `/health` | Health check for monitoring | Anyone |

## Troubleshooting

**The website opens but signing in fails**
→ The backend is probably not running, or `DATABASE_URL` is wrong. Check
`curl http://localhost:8000/health`. If that fails, look at the backend logs.

**"Safety check could not be completed" / "Request needs review" every time**
→ The Groq AI service could not be reached. Check your `GROQ_API_KEY` and
your internet connection. The system fails safe (it does not let the message
through unchecked).

**AI answers are empty, or recommendations return nothing**
→ Make sure employees exist and have skills assigned. If you expect policy
quotes, check `PINECONE_API_KEY` / `PINECONE_INDEX_NAME` and re-run
`uv run python -m app.rag.ingest`.

**Groq errors**
→ Verify `GROQ_API_KEY` and that the model names in
`app/ai/task_analyzer.py` and `app/chat/assistant.py` still exist on your
Groq account.

**Changes to the AI code do not appear**
→ The AI Chat caches things when it starts. Fully **restart both** Streamlit
and uvicorn — `--reload` alone does not refresh Streamlit.

**Database / migration errors**
→ Confirm PostgreSQL is running, the database exists, and `DATABASE_URL`
is correct, then run `uv run alembic upgrade head` again.

**Install/build problems**
→ Always install with `uv sync` (it uses the locked `uv.lock`). The project
uses `psycopg2-binary`, so no C compiler is needed.

**Docker containers keep restarting**
→ Run `docker compose logs` to see why. Usually it is a bad `DATABASE_URL`
or a missing `.env` file.

**AI chat tool errors after renaming API routes**
→ The chat's list of allowed tools (`ALLOWED_TOOL_NAMES` in
`app/chat/assistant.py`) is derived from API route names. If you rename a
route, update that list too.

## Roadmap ideas

- Cancel / complete an assignment and automatically reduce the workload.
- Unify the two workload sources (the stored number vs. the live sum of assignments).
- Add more tests for the scoring math and the AI workflow.
- Include the source of each policy quote in the response, for auditing.
- Add Postgres to the Docker Compose stack so the whole system runs with one command.
