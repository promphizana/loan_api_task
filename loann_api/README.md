# Loan Prediction API

FastAPI service that returns a default-risk prediction for a loan application.

- `POST /predict`: body `{"amount_usd": 1500, "term_months": 12, "monthly_income_usd": 400}`
- `GET /health`: health check
- `/docs`: interactive documentation
- The model file is read from `MODEL_PATH` (default `model/model.json`).

## Run locally (Windows PowerShell)

Run these commands from the `loann_api` folder (the folder containing `main.py`):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open <http://127.0.0.1:8000/docs> to try the API, or
<http://127.0.0.1:8000/health> to check that it is running. PostgreSQL is optional
for local use; without `DATABASE_URL`, predictions are returned but not stored.

## Run with Docker

With Docker Desktop running, start the API and PostgreSQL using
`docker compose up -d --build`. The API will be available at
<http://localhost:8000/docs>.

Run tests from the project folder:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```
