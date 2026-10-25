-- Skill demand in one pull, as a count and share of observed listings.
SELECT s.skill, COUNT(DISTINCT ps.ad_id) AS listings,
       ROUND(100.0 * COUNT(DISTINCT ps.ad_id) /
         NULLIF((SELECT COUNT(DISTINCT ad_id) FROM pull_jobs WHERE pull_id = ps.pull_id), 0), 1) AS pct_listings
FROM pull_skills ps JOIN skills s ON s.skill_id = ps.skill_id
WHERE ps.pull_id = :pull_id
GROUP BY s.skill ORDER BY listings DESC;

-- Advertised salaries, split by experience label, currency, and pay period.
SELECT j.experience_level, j.salary_currency, j.salary_period, COUNT(*) AS salary_listings,
       ROUND(AVG((COALESCE(j.salary_min,j.salary_max)+COALESCE(j.salary_max,j.salary_min))/2.0),0) AS mean_midpoint,
       MIN(j.salary_min) AS min_salary, MAX(j.salary_max) AS max_salary
FROM jobs j JOIN pull_jobs pj ON pj.ad_id=j.ad_id
WHERE pj.pull_id=:pull_id AND (j.salary_min IS NOT NULL OR j.salary_max IS NOT NULL)
GROUP BY j.experience_level,j.salary_currency,j.salary_period
HAVING COUNT(*) >= 3 ORDER BY salary_listings DESC;

-- First/latest result counts per collection scope.
WITH ranked AS (
 SELECT p.scope,p.pull_id,p.collected_at,COUNT(DISTINCT pj.ad_id) AS listings,
 ROW_NUMBER() OVER(PARTITION BY p.scope ORDER BY p.collected_at) AS first_n,
 ROW_NUMBER() OVER(PARTITION BY p.scope ORDER BY p.collected_at DESC) AS last_n
 FROM pulls p LEFT JOIN pull_jobs pj ON pj.pull_id=p.pull_id
 WHERE p.status='success' GROUP BY p.scope,p.pull_id,p.collected_at
)
SELECT scope,MAX(CASE WHEN first_n=1 THEN listings END) AS first_listings,
       MAX(CASE WHEN last_n=1 THEN listings END) AS latest_listings
FROM ranked GROUP BY scope;
