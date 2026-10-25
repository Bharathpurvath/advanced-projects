-- Query demand by skill for one selected pull (replace the pull_id).
SELECT s.skill,
       COUNT(DISTINCT ps.ad_id) AS postings,
       ROUND(100.0 * COUNT(DISTINCT ps.ad_id) /
         NULLIF((SELECT COUNT(DISTINCT ad_id) FROM pull_jobs WHERE pull_id = ps.pull_id), 0), 1) AS pct_postings
FROM pull_skills ps
JOIN skills s ON s.skill_id = ps.skill_id
WHERE ps.pull_id = :pull_id
GROUP BY s.skill
ORDER BY postings DESC;

-- Salary ranges by normalized city and experience classification.
SELECT j.city, j.experience_level, COUNT(*) AS salary_ads,
       ROUND(AVG((j.salary_min + j.salary_max) / 2.0), 0) AS mean_midpoint,
       ROUND(MIN(j.salary_min), 0) AS min_salary,
       ROUND(MAX(j.salary_max), 0) AS max_salary
FROM jobs j
JOIN pull_jobs pj ON pj.ad_id = j.ad_id
WHERE pj.pull_id = :pull_id AND j.salary_min IS NOT NULL
GROUP BY j.city, j.experience_level
HAVING COUNT(*) >= 5
ORDER BY salary_ads DESC;

-- Posting counts between the first and latest pull per query scope.
WITH ranked AS (
  SELECT p.scope, p.pull_id, p.collected_at,
         COUNT(DISTINCT pj.ad_id) AS ads,
         ROW_NUMBER() OVER (PARTITION BY p.scope ORDER BY p.collected_at) AS rn_first,
         ROW_NUMBER() OVER (PARTITION BY p.scope ORDER BY p.collected_at DESC) AS rn_last
  FROM pulls p LEFT JOIN pull_jobs pj ON pj.pull_id = p.pull_id
  GROUP BY p.scope, p.pull_id, p.collected_at
)
SELECT scope,
       MAX(CASE WHEN rn_first = 1 THEN ads END) AS first_ads,
       MAX(CASE WHEN rn_last = 1 THEN ads END) AS latest_ads
FROM ranked GROUP BY scope;
