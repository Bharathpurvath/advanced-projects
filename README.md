# Advanced Projects

This repository contains 20 advanced software engineering project labs and a data analytics capstone. The 20 engineering labs each have an interactive browser demo in `<project>/frontend/`, a FastAPI backend starter in `<project>/backend/main.py`, and a setup guide.

The [India Data Analyst Job Market Capstone](india-data-analyst-job-market-capstone/README.md) is a separate research workflow using Himalayas’ public Jobs API without an API key. Its [dashboard](india-data-analyst-job-market-capstone/reports/dashboard.html) clearly marks when real data is pending; the project does not publish raw job descriptions or credentials.

## Run a backend

In a terminal, open a project's `backend` folder and run:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The browser demos store sample data locally. The backend starts separately on your computer at `http://127.0.0.1:8000`; API docs are at `/docs`. These are educational prototypes, not production services. Live payments, cloud storage, GitHub writes, and paid AI APIs are not enabled. Never put real credentials in frontend code.
