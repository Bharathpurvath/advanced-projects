from __future__ import annotations
import argparse
import hashlib
import html
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "himalayas_jobs.db"
API = "https://himalayas.app/jobs/api/search"
QUERY = "data analyst"
COUNTRY = "IN"
TITLE_PATTERN = re.compile(r"\bdata\s+analyst\b|\b(?:business intelligence|bi|analytics?)\s+analyst\b|\banalyst[,/]\s*(?:data|analytics?)\b", re.I)
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
 ad_id TEXT PRIMARY KEY, title TEXT NOT NULL, company TEXT, city TEXT,
 created_at TEXT, salary_min REAL, salary_max REAL, salary_currency TEXT, salary_period TEXT,
 experience_level TEXT NOT NULL DEFAULT 'unspecified', source_url TEXT,
 description_hash TEXT, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL
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

def plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()

def seniority(job: dict, content: str) -> str:
    labels = " ".join(job.get("seniority") or []).lower()
    text = labels + " " + content.lower()
    if re.search(r"\b(intern|internship)\b", text): return "internship"
    if re.search(r"\b(entry[- ]level|junior|graduate|fresher)\b", labels): return "entry"
    if re.search(r"\b(senior|lead|principal|staff)\b", labels): return "senior"
    if re.search(r"\b(mid[- ]level|mid)\b", labels): return "mid"
    years = re.search(r"\b(\d+)\s*\+?\s*years?\b", text)
    if years:
        n = int(years.group(1))
        if n <= 2: return "entry"
        if n >= 5: return "senior"
        return "mid"
    return "unspecified"

def save_job(con, job: dict, pull_id: str, collected: str):
    ad_id = str(job.get("guid") or "").strip()
    if not ad_id: return False
    title = str(job.get("title") or "Unknown title")
    if not TITLE_PATTERN.search(title): return False
    excerpt = plain_text(job.get("excerpt") or "")
    description = plain_text(job.get("description") or "")
    content = f"{title}\n{excerpt}\n{description}"
    description_hash = hashlib.sha256(description.encode("utf-8")).hexdigest()
    pub_date = job.get("pubDate")
    try: created_at = datetime.fromtimestamp(int(pub_date), tz=timezone.utc).isoformat(timespec="seconds") if pub_date else None
    except (TypeError, ValueError, OSError): created_at = None
    def number(value):
        try: return float(value) if value is not None else None
        except (TypeError, ValueError): return None
    salary_min, salary_max = number(job.get("minSalary")), number(job.get("maxSalary"))
    # Country-filtered API results are remote-eligible for India; source fields do not establish a Chennai worksite.
    city = "India-eligible remote"
    con.execute("""INSERT INTO jobs(ad_id,title,company,city,created_at,salary_min,salary_max,salary_currency,salary_period,experience_level,source_url,description_hash,first_seen,last_seen)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(ad_id) DO UPDATE SET title=excluded.title,company=excluded.company,city=excluded.city,
    created_at=excluded.created_at,salary_min=excluded.salary_min,salary_max=excluded.salary_max,
    salary_currency=excluded.salary_currency,salary_period=excluded.salary_period,
    experience_level=excluded.experience_level,source_url=excluded.source_url,
    description_hash=excluded.description_hash,last_seen=excluded.last_seen""",
    (ad_id,title,job.get("companyName"),city,created_at,salary_min,salary_max,job.get("currency"),job.get("salaryPeriod"),
     seniority(job,content),job.get("applicationLink") or ad_id,description_hash,collected,collected))
    inserted = con.execute("INSERT OR IGNORE INTO pull_jobs(pull_id,ad_id,scope) VALUES(?,?,?)",(pull_id,ad_id,"india_remote")).rowcount == 1
    for skill, patterns in SKILLS.items():
        if any(re.search(pattern,content,flags=re.I) for pattern in patterns):
            skill_id=con.execute("SELECT skill_id FROM skills WHERE skill=?",(skill,)).fetchone()[0]
            con.execute("INSERT OR IGNORE INTO pull_skills(pull_id,ad_id,skill_id) VALUES(?,?,?)",(pull_id,ad_id,skill_id))
    return inserted

def main():
    parser=argparse.ArgumentParser(description="Collect India-eligible remote analyst jobs from Himalayas' public API.")
    parser.add_argument("--max-pages",type=int,default=50,help="Maximum search pages per pull; stop sooner when an empty page is reached")
    parser.add_argument("--sleep",type=float,default=1.0,help="Pause between API requests")
    args=parser.parse_args()
    if args.max_pages < 1: parser.error("max-pages must be at least 1")
    con=connect()
    collected=datetime.now(timezone.utc).isoformat(timespec="seconds")
    pull_id=str(uuid.uuid4())
    con.execute("INSERT INTO pulls(pull_id,scope,collected_at,query,pages_requested,results_per_page) VALUES(?,?,?,?,?,?)",
                (pull_id,"india_remote",collected,QUERY,args.max_pages,20))
    con.commit()
    session=requests.Session()
    session.headers.update({"Accept":"application/json","User-Agent":"IndiaRemoteAnalystResearch/1.0 (personal portfolio study)"})
    received=0
    try:
        for page in range(1,args.max_pages+1):
            response=session.get(API,params={"q":QUERY,"country":COUNTRY,"sort":"recent","page":page},timeout=45)
            response.raise_for_status()
            payload=response.json()
            if not isinstance(payload,dict) or not isinstance(payload.get("jobs"),list):
                raise ValueError("Unexpected API response shape; expected JSON with jobs[].")
            if page == 1:
                con.execute("UPDATE pulls SET total_reported=? WHERE pull_id=?",(payload.get("totalCount"),pull_id))
            jobs=payload["jobs"]
            if not jobs: break
            for job in jobs:
                received += bool(save_job(con,job,pull_id,collected))
            con.commit()
            print(f"Page {page}: {len(jobs)} returned; {received} unique saved so far")
            if page < args.max_pages: time.sleep(args.sleep)
        con.execute("UPDATE pulls SET records_received=?,status='success' WHERE pull_id=?",(received,pull_id))
        con.commit()
        print(f"Completed pull {pull_id}: {received} unique India-eligible remote jobs saved to {DB}")
    except Exception as exc:
        con.execute("UPDATE pulls SET records_received=?,status='failed',error=? WHERE pull_id=?",(received,str(exc)[:500],pull_id))
        con.commit()
        raise
    finally:
        con.close()

if __name__ == "__main__": main()



