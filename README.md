# Advanced Projects

This repository contains 20 advanced software engineering project labs. Each project has an interactive browser demo in its `<project>/frontend/`, a FastAPI backend starter in its `<project>/backend/main.py`, and its own setup guide.

## Run a backend

In a terminal, open a project's `backend` folder and run:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The browser demos store sample data locally. The backend starts separately on your computer at `http://127.0.0.1:8000`; API docs are at `/docs`. These are educational prototypes, not production services. Live payments, cloud storage, GitHub writes, and paid AI APIs are not enabled. Never put real credentials in frontend code.
