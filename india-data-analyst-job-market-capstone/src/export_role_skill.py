"""Export the latest successful pull's role/skill aggregate for Power BI.

Only aggregate counts are written; individual job rows and descriptions are not exported.
"""
import csv
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE = PROJECT_ROOT / "data" / "himalayas_jobs.db"
OUTPUT = PROJECT_ROOT / "reports" / "role_skill_latest.csv"

QUERY = """
SELECT
    CASE
        WHEN lower(j.title) LIKE '%business intelligence%'
          OR lower(j.title) LIKE '%business-intelligence%'
          OR lower(j.title) LIKE '%bi analyst%'
          THEN 'BI analyst'
        WHEN lower(j.title) LIKE '%analytics%'
          THEN 'Analytics analyst'
        ELSE 'Data analyst'
    END AS role_family,
    s.skill,
    COUNT(DISTINCT ps.ad_id) AS postings
FROM pull_skills ps
JOIN jobs j ON j.ad_id = ps.ad_id
JOIN skills s ON s.skill_id = ps.skill_id
WHERE ps.pull_id = (
    SELECT pull_id
    FROM pulls
    WHERE status = 'success'
    ORDER BY collected_at DESC
    LIMIT 1
)
GROUP BY role_family, s.skill
ORDER BY role_family, postings DESC, s.skill
"""

def main() -> None:
    if not DATABASE.exists():
        raise FileNotFoundError(
            f"Local database not found: {DATABASE}. Run src/collect.py first."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE) as connection:
        rows = connection.execute(QUERY).fetchall()
        if not rows:
            raise RuntimeError("No successful pull with role/skill data was found.")
        with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["role_family", "skill", "postings"])
            writer.writerows(rows)

    print(f"Exported {len(rows)} aggregate rows to {OUTPUT}")

if __name__ == "__main__":
    main()
