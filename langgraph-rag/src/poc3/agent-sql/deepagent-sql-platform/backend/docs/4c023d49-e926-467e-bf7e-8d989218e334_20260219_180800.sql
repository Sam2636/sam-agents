-- Create the CDP.analytics.customer_360 table
CREATE TABLE CDP.analytics.customer_360 AS
SELECT 
    customer_id,
    COUNT(DISTINCT account_id) AS total_accounts,
    COUNT(DISTINCT loan_id) AS total_loans,
    SUM(amount) AS total_spend,
    RANK() OVER (ORDER BY SUM(amount) DESC) AS spend_rank
FROM 
    FDP.banking.customers_clean
LEFT JOIN 
    FDP.finance.loans_enriched ON FDP.banking.customers_clean.customer_id = FDP.finance.loans_enriched.customer_id
LEFT JOIN 
    FDP.finance.transactions_enriched ON FDP.banking.customers_clean.customer_id = FDP.finance.transactions_enriched.account_id
GROUP BY 
    customer_id;

-- Create the CDP.analytics.revenue_dashboard table
CREATE TABLE CDP.analytics.revenue_dashboard AS
SELECT 
    SUM(total_spend) AS total_bank_revenue,
    SUM(total_revenue) AS total_transport_revenue,
    SUM(loan_amount * avg_interest / 100) AS total_interest_income,
    MAX(customer_id) KEEP (DENSE_RANK FIRST ORDER BY total_spend DESC) AS top_customer
FROM 
    CDP.analytics.customer_360;

-- Create the CDP.analytics.transaction_summary table
CREATE TABLE CDP.analytics.transaction_summary AS
SELECT 
    account_id,
    COUNT(transaction_id) AS total_transactions,
    SUM(CASE WHEN amount > 0 THEN amount END) AS total_credit_amount,
    SUM(CASE WHEN amount < 0 THEN amount END) AS total_debit_amount,
    DENSE_RANK() OVER (ORDER BY COUNT(transaction_id) DESC) AS account_rank
FROM 
    FDP.finance.transactions_enriched
GROUP BY 
    account_id
LIMIT 100;