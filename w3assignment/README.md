# Week 3 Assignment — FastAPI CRUD with React Frontend

A full-stack CRUD application built with **FastAPI**, **SQLAlchemy**, and **React**.

## Project Structure

```
w3assignment/
├── main.py           # FastAPI app entry point
├── database.py       # PostgreSQL connection (SQLAlchemy)
├── models/           # SQLAlchemy ORM models
│   ├── user.py
│   ├── project.py
│   └── task.py
├── schemas/          # Pydantic validation schemas
│   ├── user.py
│   ├── project.py
│   └── task.py
├── routers/          # API route handlers (CRUD endpoints)
│   ├── users.py
│   ├── projects.py
│   └── tasks.py
└── frontend/         # React UI (Vite)
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/
    └── package.json
```

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React, Axios, Vite

## API Endpoints

| Resource | POST | GET (all) | GET (one) | PUT | DELETE |
|----------|------|-----------|-----------|-----|--------|
| `/users/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/projects/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/tasks/` | ✅ | ✅ | ✅ | ✅ | ✅ |

## Setup & Run

### Backend

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic[email]
```

Update `database.py` with your PostgreSQL credentials, then:

```bash
uvicorn main:app --reload
```

API docs available at: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5500

## Entity Relationships

- **User** → owns many **Projects**
- **Project** → has many **Tasks**
- **User** → assigned to many **Tasks**
