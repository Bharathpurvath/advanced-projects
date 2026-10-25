# Findings

Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.

Successful pulls: 1. The latest API search reported 467 keyword candidates; the title filter retained 44 distinct analyst listings.

The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.

## Most frequently detected skills

Counts are from the latest pull (44 listings); a listing may mention multiple skills.

- SQL: 34 listings (77.3%).
- Data visualization: 32 listings (72.7%).
- Python: 30 listings (68.2%).
- Tableau: 24 listings (54.5%).
- Power BI: 22 listings (50.0%).
- Statistics: 20 listings (45.5%).
- Communication: 20 listings (45.5%).
- Excel: 17 listings (38.6%).
- ETL / data pipelines: 16 listings (36.4%).
- Machine learning: 11 listings (25.0%).

## Advertised salary coverage

2 of 44 latest listings (4.5%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.

## Change across weekly pulls

Only one successful pull exists, so this snapshot establishes the baseline; no week-over-week change can be inferred yet.

## Limits

The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback.
