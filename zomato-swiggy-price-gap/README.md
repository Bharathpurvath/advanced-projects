# Zomato vs Swiggy: a neighbourhood price comparison

This project compares publicly displayed prices for the same restaurant and dish on both apps. It uses **manual observations only**; it does not automate, scrape, log in, or collect customer-specific prices. You control the location and timing, and record what each app shows.

## Collection workbook

Open `collection_template.xlsx`. Select 25–30 restaurants, choose one comparable dish/portion for each, and record each app once per week for four weeks. That is up to 240 observations (30 restaurants × 4 weeks × 2 apps). Capture the same restaurant and dish on both apps on the same date and as close together in time as practical. Enter `0` only when a fee is explicitly shown as zero; leave a fee blank when it is unavailable, rather than treating missing data as free.

Record neighborhood rather than a home or delivery address. Avoid logging in or applying account-specific coupons. Note relevant offers in the notes field, and do not combine a discounted payable amount with the listed menu price.

## Analysis

Export the workbook's `Collection` worksheet as `data/observations.csv`, then run:

```powershell
python -m pip install -r requirements.txt
python src/analyze.py --input data/observations.csv
```

The script pairs records by week, date, restaurant, and standardized dish, then computes app price gaps, delivery/packaging fee patterns, and rating differences. It writes aggregate tables, charts, and `reports/findings.md`. Pair only observations with matching keys; unmatched rows stay visible in a separate coverage table.

## Public demonstration

`data/synthetic_demo_observations.csv` contains invented restaurant names and prices to show the analysis workflow. The published findings are explicitly marked synthetic; they are not observations from Zomato or Swiggy and do not describe local pricing. Use the workbook to collect your own manual observations before making real comparisons.

## Definitions and limits

- Menu price and observed total are kept separate. Observed total is menu price + delivery fee + packaging fee before taxes or discounts.
- Price gap is Zomato minus Swiggy; positive means Zomato was higher. Percent gap uses Swiggy as the denominator.
- Delivery fees can vary with address, distance, time, membership, demand, and account. The workbook captures what appeared in the selected observation and is not a universal app price comparison.
- Ratings can be defined differently across apps and should not be read as a quality score on one shared scale without that caveat.
- This is a convenience sample of selected restaurants and a short collection window. It supports a narrow neighbourhood comparison, not a claim about all restaurants or users.

## Privacy and publishing

Do not publish raw screenshots, account details, precise addresses, or personally identifying notes. Review and aggregate your data before sharing. The workbook and analysis folder ignore collected observations and generated reports by default.
