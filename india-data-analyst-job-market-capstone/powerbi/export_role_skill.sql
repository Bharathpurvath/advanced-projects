-- Run from the capstone project root with sqlite3 installed.
-- Writes aggregates only; no job descriptions or listing-level rows are exported.
.headers on
.mode csv
.once reports/role_skill_latest.csv
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
ORDER BY role_family, postings DESC, s.skill;
