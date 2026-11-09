# Findings

Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.

Successful pulls: 4. The latest API search reported 415 keyword candidates; the title filter retained 38 distinct analyst listings.

The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.

## Most frequently detected skills

Counts are from the latest pull (38 listings); a listing may mention multiple skills.

- Data visualization: 30 listings (78.9%).
- SQL: 28 listings (73.7%).
- Python: 24 listings (63.2%).
- Tableau: 21 listings (55.3%).
- Excel: 20 listings (52.6%).
- Power BI: 19 listings (50.0%).
- Communication: 18 listings (47.4%).
- Statistics: 18 listings (47.4%).
- ETL / data pipelines: 11 listings (28.9%).
- Cloud (AWS/Azure/GCP): 10 listings (26.3%).

## Advertised salary coverage

4 of 38 latest listings (10.5%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.

## Change across weekly pulls

Compare the first and latest pull in the CSV. Changes reflect this API's remote listings and search coverage, not overall labor-market growth.

## Limits

The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback.
