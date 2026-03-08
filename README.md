# Backup Monitor API

A REST API for tracking backup job statuses across multiple SaaS clients. Built to demonstrate production-ready Python backend patterns.

## Overview

The problem this solves: managed service providers (MSPs) run backup jobs for many clients across different sources (Microsoft 365, Salesforce, etc.). They need a central place to register those jobs, track their status lifecycle, and get a health summary at a glance.

This API provides:
- JWT-authenticated endpoints for all operations
- Per-client backup job tracking with full lifecycle states
- A summary endpoint aggregating totals by status and surfacing the latest failure

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (Mapped / mapped_column style) |
| Migrations | Alembic |
| Database | PostgreSQL (SQLite for tests) |
| Auth | JWT via python-jose + passlib[bcrypt] |
| Validation | Pydantic v2 + pydantic-settings |
| Testing | pytest + httpx TestClient |
| Containerization | Docker + docker-compose |

## API Endpoints

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns JWT bearer token |

### Clients
| Method | Path | Description |
|---|---|---|
| GET | `/clients` | List all clients |
| POST | `/clients` | Create a client |
| GET | `/clients/{id}` | Get a single client |

### Backup Jobs
| Method | Path | Description |
|---|---|---|
| GET | `/clients/{id}/backups` | List all backup jobs for a client |
| POST | `/clients/{id}/backups` | Register a new backup job |
| GET | `/backups/summary` | Aggregated status counts + latest failure |

All endpoints except `/auth/register` and `/auth/login` require a `Bearer` token.

## Data Model

### BackupJob

```
id            int         Primary key
client_id     int         FK → clients
source        str         e.g. "Microsoft 365", "Salesforce"
status        enum        PENDING | RUNNING | SUCCESS | FAILED | WARNING
size_bytes    int | null  Backup size
error_message str | null  Populated on failure
started_at    datetime    Job start time
finished_at   datetime    Job end time
created_at    datetime    Record creation (server default)
```

### Client

```
id             int      Primary key
name           str
contact_email  str      Validated as EmailStr
created_at     datetime Server default
```

## Running Locally

**With Docker (recommended):**

```bash
docker-compose up --build
```

API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

**Without Docker:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# copy and edit environment variables
cp .env.example .env

# run migrations
alembic upgrade head

# start the server
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret (change in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL (default: 30) |

See `.env.example` for reference.

## Running Tests

Tests run against an in-memory SQLite database — no external dependencies needed.

```bash
pytest
```

## Project Structure

```
app/
├── auth/
│   ├── dependencies.py   # get_current_user dependency
│   └── jwt.py            # token creation, password hashing
├── models/
│   ├── user.py
│   ├── client.py
│   └── backup_job.py     # BackupStatus enum + BackupJob model
├── routers/
│   ├── auth.py
│   ├── clients.py
│   └── backups.py
├── schemas/
│   ├── user.py
│   ├── client.py
│   └── backup_job.py     # BackupJobCreate, BackupJobOut, BackupSummary
├── config.py             # pydantic-settings
├── database.py           # engine, SessionLocal, get_db()
└── main.py               # app entry point
alembic/                  # database migrations
tests/                    # pytest test suite
```
