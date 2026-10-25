-- SQLite queries against upi_payments.db after running src/analyze.py.

-- Monthly volume and value by channel.
SELECT strftime('%Y-%m', month) AS month,
       ROUND(upi_volume_mn, 1) AS upi_volume_mn,
       ROUND(credit_card_volume_mn, 1) AS credit_card_volume_mn,
       ROUND(debit_card_volume_mn, 1) AS debit_card_volume_mn,
       ROUND(upi_value_crore, 0) AS upi_value_crore
FROM monthly_payments
ORDER BY month;

-- Current three-channel transaction mix.
SELECT strftime('%Y-%m', month) AS month,
       ROUND(upi_share_of_three_channels_pct, 2) AS upi_share_pct
FROM monthly_payments
ORDER BY month;

-- Latest average transaction value, in rupees.
SELECT strftime('%Y-%m', month) AS month,
       ROUND(upi_avg_ticket_rupees, 0) AS upi_avg_rupees,
       ROUND(credit_card_avg_ticket_rupees, 0) AS credit_card_avg_rupees,
       ROUND(debit_card_avg_ticket_rupees, 0) AS debit_card_avg_rupees
FROM monthly_payments
ORDER BY month DESC
LIMIT 12;
