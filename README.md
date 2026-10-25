# Bharath B — Project Portfolio

**Live portfolio:** [bharathpurvath.github.io/advanced-projects](https://bharathpurvath.github.io/advanced-projects/)  
**GitHub:** [Bharathpurvath](https://github.com/Bharathpurvath)

A project portfolio spanning data analysis, research, and software engineering prototypes.

## Featured data project

The [India Remote Data Analyst Job Market Capstone](india-data-analyst-job-market-capstone/README.md) explores which skills appear in remote analyst listings open to applicants in India.

- [Open the dashboard](https://bharathpurvath.github.io/advanced-projects/india-data-analyst-job-market-capstone/reports/dashboard.html)
- [Read the findings](india-data-analyst-job-market-capstone/reports/findings.md)
- [Review the methodology and run instructions](india-data-analyst-job-market-capstone/README.md)

The first snapshot retained 44 analyst-title postings from 467 broad search candidates. SQL appeared in 34 listings and Python in 30. Only two listings disclosed salary. This is a single Himalayas remote-job snapshot filtered for India eligibility, not a census of the Indian job market or a Chennai/on-site study. Weekly changes need additional successful pulls.

The project uses Himalayas' public Jobs API without an API key. It publishes aggregate reporting, not raw job descriptions or individual listings. See the [API documentation](https://himalayas.app/api) and [terms](https://himalayas.app/terms).

## Engineering project labs

The repository also contains 20 educational software engineering labs. Each includes an interactive browser demo, a FastAPI backend starter, and setup notes. The demos use sample data locally; backend services run on your computer. They are learning prototypes, not production services. Live payments, cloud storage, GitHub writes, and paid AI APIs are not enabled. Do not put real credentials in frontend code.

## Running a backend

Open a project's `backend` folder and run:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs` while the backend is running.
