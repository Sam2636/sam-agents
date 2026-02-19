CREATE TABLE CDP.analytics.CDP.analytics.customer_360 AS
SELECT 
    c.customer_id,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    COUNT(DISTINCT l.loan_id) AS total_loans,
    SUM(t.amount) AS total_spend,
    RANK() OVER (ORDER BY SUM(t.amount) DESC) AS spend_rank
FROM 
    FDP.banking.FDP.banking.customers_clean c
LEFT JOIN 
    FDP.banking.FDP.banking.accounts_enriched a ON c.customer_id = a.customer_id
LEFT JOIN 
    FDP.finance.FDP.finance.loans_enriched l ON c.customer_id = l.customer_id
LEFT JOIN 
    FDP.finance.FDP.finance.transactions_enriched t ON a.account_id = t.account_id
GROUP BY 
    c.customer_id
LIMIT 100;