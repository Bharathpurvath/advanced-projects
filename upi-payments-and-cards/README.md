# UPI and cards: growth, value, and the payment mix

This project asks how India's UPI transaction volume, value, and average payment size have changed relative to credit- and debit-card payments. It uses RBI DBIE's official monthly **Payment System Indicators** table, rather than an unofficial aggregator. The monthly series begins in November 2019 for the current table layout and is updated by the RBI.

## Data source

- RBI Database on Indian Economy (DBIE), [Payment System Indicators](https://dbie.rbihub.in/statistics?table=financial_sector.r612_payment_system_indicators), monthly, table `financial_sector.r612_payment_system_indicators`.
- The DBIE page offers CSV/JSON downloads. This project reads the public JSON table endpoint used by the DBIE statistics interface and saves the raw response under `data/raw/` for provenance.
- Volume is reported in lakh transactions; value is in ₹ crore. The script normalizes to million transactions for charts and derives average transaction value in rupees.
- RBI warns that card payment data definitions become more granular from November 2019, so avoid comparing card series across that break. This project starts at November 2019.

## Run

```powershell
python -m pip install -r requirements.txt
python src/collect.py
python src/analyze.py
```

The collector refreshes `data/monthly_payments.csv`; the analysis produces `reports/findings.md`, CSV summaries, and charts. A SQLite query file is provided in `sql/analysis.sql`.

The public snapshot was refreshed from RBI DBIE on 25 October 2026. The table returned 81 observations, from November 2019 through July 2026. A monthly GitHub Actions workflow in the portfolio repository can refresh the series when RBI publishes later observations.

## Questions and definitions

- How fast did UPI volume and value grow year over year?
- Did credit- and debit-card transaction volume move in the same direction?
- How did UPI's share of the combined UPI + card transaction count change?
- Did average ticket size move with transaction growth?

Average ticket size = value in ₹ crore × 100 / volume in lakh. UPI share denominator is UPI + credit-card + debit-card payment counts in the RBI table. It is an analytic comparison of these reported channels, not a share of all Indian payments and not proof that UPI transactions replaced card transactions.

## Limitations

DBIE payment statistics are provisional and definitions vary by payment type and period. UPI includes person-to-person and merchant payments, while card totals aggregate payment channels differently; these series are comparable as reported counts and values, not as equivalent use cases. Changes in aggregate volumes do not establish causation. App-wise market-share statistics are published separately in NPCI's [UPI Ecosystem Statistics](https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics); they are not mixed into this RBI channel time series.

## Attribution

Source: Reserve Bank of India, Database on Indian Economy, Payment System Indicators. Include the table name, access date, and these unit/definition caveats in any portfolio presentation.
