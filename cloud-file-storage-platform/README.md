# Cloud File Storage Platform

**Skills:** Object storage · permissions · signed URLs

An advanced learning lab exploring object storage · permissions · signed urls. The browser demo demonstrates the main workflow using local sample data.

## Run the API backend

Open this folder's `backend` directory in a terminal and run:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

API: `http://127.0.0.1:8000` · API reference: `http://127.0.0.1:8000/docs`

## Browser demo

Open `frontend/index.html` locally or visit the published page. The browser demo uses local sample data. The backend starter is separate; configure production database, authentication, integrations, and deployment before using real data.

## Production considerations

This is an educational prototype. Never commit `.env` files, API keys, tokens, personal data, or production database files.
