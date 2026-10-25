from __future__ import annotations
import argparse
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "jobs.db"
BASE = "https://api.adzuna.com/v1/api/jobs/in/search/{page}"
SCOPES = (("india", None), ("chennai", "Chennai"))
SKILLS = {
    "SQL": [r"\bsql\b", r"mysql", r"postgres(?:ql)?", r"sqlite", r"sql server"],
    "Excel": [r"\bexcel\b", r"spreadsheets?", r"\bgoogle sheets\b"],
    "Python": [r"\bpython\b", r"pandas", r"numpy"],
    "Power BI": [r"\bpower\s?bi\b", r"powerbi"],
    "Tableau": [r"\btableau\b"],
    "R": [r"\br programming\b", r"\blanguage r\b", r"\br studio\b"],
    "Statistics": [r"\bstatistical?\b", r"\bstatistics\b", r"hypothesis testing"],
    "Data visualization": [r"data visuali[sz]ation", r"\bdashboards?\b", r"\bvisuali[sz]ation\b"],
    "ETL / data pipelines": [r"\betl\b", r"data pipeline", r"data warehouse", r"\bel\s?t\b"],
    "Cloud (AWS/Azure/GCP)": [r"\baws\b", r"\bazure\b", r"\bgcp\b", r"google cloud"],
    "Machine learning": [r"machine learning", r"\bml\b", r"predictive model"],
    "Big data (Spark/Hadoop)": [r"\bspark\b", r"\bhadoop\b", r"\bbig data\b"],
    "Communication": [r"communication skills", r"stakeholder management", r"present findings"],
}
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS pulls(
 pull_id TEXT PRIMARY KEY, scope TEXT NOT NULL, collected_at TEXT NOT NULL,
 query TEXT NOT NULL, pages_requested INTEGER NOT NULL, results_per_page INTEGER NOT NULL,
 total_reported INTEGER, records_received INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'running', error TEXT
);
CREATE TABLE IF NOT EXISTS jobs(
 ad_id TEXT PRIMARY KEY, title TEXT NOT NULL, company TEXT, city TEXT, location_display TEXT,
 created_at TEXT, salary_min REAL, salary_max REAL, salary_is_predicted INTEGER,
 contract_type TEXT, contract_time TEXT, category TEXT, redirect_url TEXT,
 description TEXT, description_hash TEXT, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
 experience_level TEXT NOT NULL DEFAULT 'unspecified'
);
CREATE TABLE IF NOT EXISTS pull_jobs(
 pull_id TEXT NOT NULL REFERENCES pulls(pull_id), ad_id TEXT NOT NULL REFERENCES jobs(ad_id),
 scope TEXT NOT NULL, PRIMARY KEY(pull_id, ad_id, scope), UNIQUE(pull_id, ad_id)
);
CREATE TABLE IF NOT EXISTS skills(skill_id INTEGER PRIMARY KEY, skill TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS pull_skills(
 pull_id TEXT NOT NULL, ad_id TEXT NOT NULL, skill_id INTEGER NOT NULL REFERENCES skills(skill_id),
 PRIMARY KEY(pull_id, ad_id, skill_id),
 FOREIGN KEY(pull_id, ad_id) REFERENCES pull_jobs(pull_id, ad_id)
);
CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city);
CREATE INDEX IF NOT EXISTS idx_pull_jobs_pull ON pull_jobs(pull_id);
"""

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA)
    for name in SKILLS:
        con.execute("INSERT OR IGNORE INTO skills(skill) VALUES(?)", (name,))
    return con

def experience(text: str) -> str:
    import re
    t = text.lower()
    if re.search(r"\b(intern|internship)\b", t): return "internship"
    if re.search(r"\b(fresher|entry[- ]level|graduate|0\s*[-–to]{1,3}\s*2\s*years?)\b", t): return "entry"
    if re.search(r"\b(senior|sr\.?|lead|principal|staff analyst)\b", t): return "senior"
    if re.search(r"\b(\d+)\s*\+?\s*years?\b", t):
        n = int(re.search(r"\b(\d+)\s*\+?\s*years?\b", t).group(1))
        if n <= 2: return "entry"
        if n >= 5: return "senior"
        return "mid"
    return "unspecified"

def city_from(ad: dict, scope: str) -> str:
    loc = ad.get("location") or {}
    areas = loc.get("area") or []
    display = (loc.get("display_name") or "").strip()
    if scope == "chennai": return "Chennai"
    for item in reversed(areas):
        if item and item.lower() not in {"india", "in"}:
            return str(item)
    return display.split(",")[0].strip() if display else "Unspecified"

def save_ad(con, ad, pull_id: str, scope: str, collected: str):
    import hashlib
    import re
    ad_id = str(ad.get("id") or "").strip()
    if not ad_id: return False
    title = str(ad.get("title") or "Unknown title")
    desc = str(ad.get("description") or "")
    company = (ad.get("company") or {}).get("display_name")
    location = ad.get("location") or {}
    city = city_from(ad, scope)
    text = f"{title}\n{desc}"
    h = hashlib.sha256(desc.encode("utf-8")).hexdigest()
    salary_min, salary_max = ad.get("salary_min"), ad.get("salary_max")
    try: salary_min = float(salary_min) if salary_min is not None else None
    except (TypeError, ValueError): salary_min = None
    try: salary_max = float(salary_max) if salary_max is not None else None
    except (TypeError, ValueError): salary_max = None
    con.execute("""INSERT INTO jobs(ad_id,title,company,city,location_display,created_at,salary_min,salary_max,salary_is_predicted,contract_type,contract_time,category,redirect_url,description,description_hash,first_seen,last_seen,experience_level)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(ad_id) DO UPDATE SET title=excluded.title, company=excluded.company, city=excluded.city,
      location_display=excluded.location_display, created_at=excluded.created_at, salary_min=excluded.salary_min,
      salary_max=excluded.salary_max, salary_is_predicted=excluded.salary_is_predicted,
      contract_type=excluded.contract_type, contract_time=excluded.contract_time, category=excluded.category,
      redirect_url=excluded.redirect_url, description=excluded.description, description_hash=excluded.description_hash,
      last_seen=excluded.last_seen, experience_level=excluded.experience_level""",
      (ad_id,title,company,city,str(location.get("display_name") or ""),ad.get("created"),salary_min,salary_max,
       int(bool(ad.get("salary_is_predicted"))),ad.get("contract_type"),ad.get("contract_time"),
       (ad.get("category") or {}).get("label"),ad.get("redirect_url"),desc,h,collected,collected,experience(text)))
    con.execute("INSERT OR IGNORE INTO pull_jobs(pull_id,ad_id,scope) VALUES(?,?,?)", (pull_id,ad_id,scope))
    for skill, patterns in SKILLS.items():
        if any(re.search(p, text, flags=re.I) for p in patterns):
            sid = con.execute("SELECT skill_id FROM skills WHERE skill=?", (skill,)).fetchone()[0]
            con.execute("INSERT OR IGNORE INTO pull_skills(pull_id,ad_id,skill_id) VALUES(?,?,?)", (pull_id,ad_id,sid))
    return True

def main():
    parser = argparse.ArgumentParser(description="Collect job ads using Adzuna's official API.")
    parser.add_argument("--pages", type=int, default=1, help="Pages per scope; API page numbering starts at 1")
    parser.add_argument("--results-per-page", type=int, default=50)
    parser.add_argument("--sleep", type=float, default=1.0, help="Pause between requests")
    args = parser.parse_args()
    if args.pages < 1 or args.results_per_page < 1 or args.results_per_page > 50:
        parser.error("Use pages >= 1 and results-per-page from 1 to 50.")
    load_dotenv(ROOT / ".env")
    app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key or app_id == "your_app_id" or app_key == "your_app_key":
        sys.exit("Set ADZUNA_APP_ID and ADZUNA_APP_KEY in .env. No request was sent.")
    con = connect()
    session = requests.Session()
    session.headers.update({"Accept":"application/json", "User-Agent":"IndiaJobMarketResearch/1.0 (personal research)"})
    grand = 0
    try:
        for scope, where in SCOPES:
            pull_id = str(uuid.uuid4())
            collected = datetime.now(timezone.utc).isoformat(timespec="seconds")
            query = "data analyst"
            con.execute("INSERT INTO pulls(pull_id,scope,collected_at,query,pages_requested,results_per_page) VALUES(?,?,?,?,?,?)",
                        (pull_id,scope,collected,query,args.pages,args.results_per_page))
            received = 0
            try:
                for page in range(1,args.pages+1):
                    params = {"app_id":app_id,"app_key":app_key,"results_per_page":args.results_per_page,
                              "what":query,"content-type":"application/json"}
                    if where:
                        params["where"] = where
                        params["distance"] = 25
                    response = session.get(BASE.format(page=page), params=params, timeout=45)
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, dict) or not isinstance(payload.get("results", []), list):
                        raise ValueError("Unexpected API response shape; expected a JSON object with results[].")
                    if page == 1:
                        con.execute("UPDATE pulls SET total_reported=? WHERE pull_id=?", (payload.get("count"),pull_id))
                    ads = payload.get("results", [])
                    for ad in ads:
                        save_ad(con,ad,pull_id,scope,collected); received += bool(ad.get("id"))
                    con.commit()
                    if not ads: break
                    if page < args.pages: time.sleep(args.sleep)
                con.execute("UPDATE pulls SET records_received=?,status='success' WHERE pull_id=?", (received,pull_id))
                con.commit()
                print(f"{scope}: received {received} ads; pull_id={pull_id}")
                grand += received
            except Exception as exc:
                con.execute("UPDATE pulls SET records_received=?,status='failed',error=? WHERE pull_id=?", (received,str(exc)[:500],pull_id))
                con.commit()
                raise
    finally:
        con.close()
    print(f"Done. {grand} scope-records saved to {DB}")

if __name__ == "__main__": main()



