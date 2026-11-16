# Findings

Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.

Successful pulls: 5. The latest API search reported 408 keyword candidates; the title filter retained 39 distinct analyst listings.

The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.

## Most frequently detected skills

Counts are from the latest pull (39 listings); a listing may mention multiple skills.

- Data visualization: 30 listings (76.9%).
- SQL: 29 listings (74.4%).
- Python: 23 listings (59.0%).
- Tableau: 21 listings (53.8%).
- Communication: 20 listings (51.3%).
- Power BI: 20 listings (51.3%).
- Excel: 19 listings (48.7%).
- Statistics: 16 listings (41.0%).
- Cloud (AWS/Azure/GCP): 12 listings (30.8%).
- ETL / data pipelines: 11 listings (28.2%).

## Advertised salary coverage

4 of 39 latest listings (10.3%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.

## Change across weekly pulls

Compare the first and latest pull in the CSV. Changes reflect this API's remote listings and search coverage, not overall labor-market growth.

## Limits

The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback.
