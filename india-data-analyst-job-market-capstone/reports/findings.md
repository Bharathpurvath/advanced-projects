# Findings

Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.

Successful pulls: 2. The latest API search reported 467 keyword candidates; the title filter retained 45 distinct analyst listings.

The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.

## Most frequently detected skills

Counts are from the latest pull (45 listings); a listing may mention multiple skills.

- SQL: 35 listings (77.8%).
- Data visualization: 32 listings (71.1%).
- Python: 30 listings (66.7%).
- Communication: 23 listings (51.1%).
- Power BI: 23 listings (51.1%).
- Tableau: 23 listings (51.1%).
- Statistics: 19 listings (42.2%).
- Excel: 18 listings (40.0%).
- ETL / data pipelines: 15 listings (33.3%).
- Cloud (AWS/Azure/GCP): 11 listings (24.4%).

## Advertised salary coverage

3 of 45 latest listings (6.7%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.

## Change across weekly pulls

Compare the first and latest pull in the CSV. Changes reflect this API's remote listings and search coverage, not overall labor-market growth.

## Limits

The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback.
