# Enterprise Expense Management API

![Status](https://img.shields.io/badge/status-in%20progress-yellow)

Backend for tracking, approving and reporting company expenses.
Built with **FastAPI**, **SQLModel**, **SQLite**, **Alembic**, **JWT auth**, **Docker Compose**. Frontend: **Streamlit**.

> 🚧 **Work in progress** — core API + auth + migrations are working, features below are actively being added. Not production-ready yet (see Roadmap).

---

## Why these choices

- **Alembic migrations on startup** → schema always in sync, no manual DB edits
- **Argon2 password hashing** (`pwdlib`) → not a weak/deprecated hash
- **JWT auth** (`PyJWT`) → stateless, scalable
- **Pydantic v2 / SQLModel** → single source of truth for validation + DB model
- **Docker Compose** → reproducible setup, no "works on my machine"
- **fastapi-mail** → notifications built-in, not an afterthought

---

## Business case

- **Problem:** expenses tracked via spreadsheets/email → slow, no audit trail, error-prone
- **Target:** SMBs (10–500 employees) that outgrew spreadsheets but don't need SAP/Concur
- **Value:** structured approval flow, real-time visibility, audit trail, secure by default
- **API-first:** same backend can power web, mobile, Slack bot, accounting integrations — no rewrite
- **Roadmap below = known gaps**, not hidden ones (shows scoping, not overselling)

---

## Tech Stack

| Layer | Tech |
|---|---|
| API | FastAPI + Uvicorn |
| ORM | SQLModel (SQLAlchemy 2.x) |
| DB | SQLite (via `aiosqlite`) |
| Migrations | Alembic |
| Auth | JWT + Argon2 |
| Validation | Pydantic v2 |
| Email | fastapi-mail |
| Frontend | Streamlit |
| Infra | Docker / Docker Compose |

---

## Architecture

```
Streamlit (8501) → FastAPI (8000) → SQLite
                         ↓
                     fastapi-mail
```

Backend runs `alembic upgrade head` before starting Uvicorn — every environment guaranteed schema-safe.

---

## Getting Started

```bash
git clone https://github.com/Phabi95/expenses-fastapi.git
cd expenses-fastapi
docker compose up --build
```

- API: `http://localhost:8000` (docs at `/docs`, `/redoc`)
- Frontend: `http://localhost:8501`

### `.env` example

```env
DATABASE_URL=sqlite+aiosqlite:////app/data/database.db
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=change-me
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
SECRET_KEY=generate-a-long-random-value
```
> Matches `src/config.py` (`Settings` class). **Never commit real values** — this file is a template only; the real `.env` stays in `.gitignore`.

---

## Project Structure

```
alembic/        # migrations
src/             # API, models, schemas, services
frontend/       # Streamlit UI
requirements/  # split deps
Dockerfile
compose.yaml
```

---

## Roadmap

- [ ] Migrate to PostgreSQL (production-grade DB)
- [ ] Role-based access control
- [ ] pytest suite
- [ ] CI (lint, type-check, tests)
- [ ] Receipt/file upload
- [ ] CSV/PDF export

---

## License

MIT
