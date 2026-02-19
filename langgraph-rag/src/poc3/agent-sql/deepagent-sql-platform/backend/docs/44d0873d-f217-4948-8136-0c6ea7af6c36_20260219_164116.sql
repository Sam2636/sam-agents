SELECT 
    customer_id,
    COUNT(order_id) AS total_orders,
    SUM(order_amount) AS total_amount
FROM 
    ODP.sales.ODP.sales.orders
GROUP BY 
    customer_id
LIMIT 100;