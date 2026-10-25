# Online retail sales deep dive

A reproducible first analytics portfolio project using the UCI Online Retail transaction log. The analysis asks:

1. How did net sales change month to month, and was November a spike?
2. What share of invoices were canceled?
3. Which products and countries contributed the most revenue?

## Data and attribution

Download: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail). The workbook contains transactions from a UK gift retailer from 1 December 2010 through 9 December 2011. The dataset is attributed to Daqing Chen, Sai Laing Sain, and K. Guo and distributed under CC BY 4.0. Download the workbook and place it at `data/raw/Online Retail.xlsx` before running the analysis. The source workbook and derived SQLite database are intentionally not included in the public portfolio; download the source from UCI and regenerate the analysis locally.

## Reproduce

Python 3.10+ and packages in `requirements.txt` are needed.

```powershell
python -m pip install -r requirements.txt
python src/analyze.py
```

The script reads `data/raw/Online Retail.xlsx`, normalizes column names, parses dates, identifies cancellation invoices (invoice numbers beginning with `C`), keeps source rows for audit, and creates a clean positive-quantity, positive-price sales table for revenue analysis. It writes a local SQLite database, CSV summaries, charts, and `reports/findings.md`.

## Definitions and caveats

- Line revenue is `Quantity × UnitPrice` in the dataset's currency (GBP).
- Cancellations are invoices whose invoice number starts with `C`; cancellation share is canceled distinct invoices divided by all distinct invoices. This is an invoice-level rate, not a canceled-value rate.
- Revenue charts exclude cancellation lines and rows with nonpositive quantity or price. Refund/return accounting is therefore not netted from sales; cancellations are reported separately.
- Product ranking uses stock code and description. Missing customer IDs are retained in sales totals because the transaction can still be attributed to a country and product.
- The monthly series ends in December 2011, which is partial (data ends 9 Dec). Do not compare December with full months without labeling the partial period.
- Duplicate rows are not removed blindly. Identical-looking line items can be valid repeated purchases; the report shows their count for review.

## Repository map

- `sql/analysis.sql`: readable SQLite queries for the core questions.
- `src/analyze.py`: end-to-end import, cleaning, storage, aggregation, and report generation.
- `data/`: source archive and extracted workbook (keep raw data out of public Git if size or policy requires it).
- `reports/`: generated findings, tables, and charts.

## Findings

The published run retained 530,104 positive sale lines from 541,909 source rows. Revenue under the stated definition was £10,666,684.54; the November 2011 increase was 30.7% versus October, and 14.81% of distinct invoices were cancellation invoices. December is partial, and the duplicate-looking lines are flagged rather than blindly removed. Re-run the script to reproduce the full tables and charts from the UCI source workbook.
