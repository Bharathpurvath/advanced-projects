# Findings

Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.

Successful pulls: 6. The latest API search reported 409 keyword candidates; the title filter retained 34 distinct analyst listings.

The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.

## Most frequently detected skills

Counts are from the latest pull (34 listings); a listing may mention multiple skills.

- Data visualization: 27 listings (79.4%).
- SQL: 26 listings (76.5%).
- Python: 21 listings (61.8%).
- Tableau: 18 listings (52.9%).
- Statistics: 17 listings (50.0%).
- Power BI: 17 listings (50.0%).
- Communication: 17 listings (50.0%).
- Excel: 16 listings (47.1%).
- ETL / data pipelines: 11 listings (32.4%).
- Cloud (AWS/Azure/GCP): 10 listings (29.4%).

## Advertised salary coverage

4 of 34 latest listings (11.8%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.

## Change across weekly pulls

Compare the first and latest pull in the CSV. Changes reflect this API's remote listings and search coverage, not overall labor-market growth.

## Limits

The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback.
