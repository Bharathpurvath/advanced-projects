-- Run against retail.db created by src/analyze.py.
-- Sales table includes non-cancellation rows with positive quantity and unit price.

-- Monthly gross sales (GBP). December 2011 is partial.
SELECT strftime('%Y-%m', invoice_date) AS month,
       ROUND(SUM(quantity * unit_price), 2) AS revenue,
       COUNT(DISTINCT invoice_no) AS invoices
FROM sales
GROUP BY month
ORDER BY month;

-- Cancellation invoice share, based on distinct invoice numbers.
SELECT COUNT(DISTINCT CASE WHEN is_cancellation = 1 THEN invoice_no END) AS canceled_invoices,
       COUNT(DISTINCT invoice_no) AS all_invoices,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN is_cancellation = 1 THEN invoice_no END)
             / NULLIF(COUNT(DISTINCT invoice_no), 0), 2) AS canceled_invoice_pct
FROM source_lines;

-- Best sellers by units, excluding canceled and invalid sale lines.
SELECT stock_code, description, SUM(quantity) AS units_sold,
       ROUND(SUM(quantity * unit_price), 2) AS revenue
FROM sales
GROUP BY stock_code, description
ORDER BY units_sold DESC
LIMIT 10;

-- Top countries by revenue, excluding the United Kingdom for a clearer international view.
SELECT country, ROUND(SUM(quantity * unit_price), 2) AS revenue,
       COUNT(DISTINCT invoice_no) AS invoices
FROM sales
WHERE country <> 'United Kingdom'
GROUP BY country
ORDER BY revenue DESC
LIMIT 10;

-- Revenue concentration among the top ten products.
WITH product_revenue AS (
  SELECT stock_code, SUM(quantity * unit_price) AS revenue
  FROM sales GROUP BY stock_code
)
SELECT ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM product_revenue), 2)
       AS top_10_product_revenue_pct
FROM (SELECT revenue FROM product_revenue ORDER BY revenue DESC LIMIT 10);
