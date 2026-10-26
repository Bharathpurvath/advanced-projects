# Findings

Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.

Successful pulls: 1. The latest API search reported 478 keyword candidates; the title filter retained 46 distinct analyst listings.

The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.

## Most frequently detected skills

Counts are from the latest pull (46 listings); a listing may mention multiple skills.

- SQL: 36 listings (78.3%).
- Data visualization: 34 listings (73.9%).
- Python: 32 listings (69.6%).
- Tableau: 25 listings (54.3%).
- Power BI: 24 listings (52.2%).
- Communication: 22 listings (47.8%).
- Statistics: 21 listings (45.7%).
- Excel: 18 listings (39.1%).
- ETL / data pipelines: 16 listings (34.8%).
- Machine learning: 11 listings (23.9%).

## Advertised salary coverage

3 of 46 latest listings (6.5%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.

## Change across weekly pulls

Only one successful pull exists, so this snapshot establishes the baseline; no week-over-week change can be inferred yet.

## Limits

The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback.
