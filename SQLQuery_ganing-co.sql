WITH customer_transactions AS (
    SELECT
        c.customer_id,
        FORMAT(c.signup_date, 'yyyy-MM') AS cohort_month,
        FORMAT(t.transaction_date, 'yyyy-MM') AS active_month,
        COUNT(DISTINCT t.transaction_id) AS transaction_count
    FROM customers c
    JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.signup_date, t.transaction_date
)
SELECT
    cohort_month,
    active_month,
    COUNT(DISTINCT customer_id) AS active_users
FROM customer_transactions
GROUP BY cohort_month, active_month
ORDER BY cohort_month, active_month;

WITH weekly_activity AS (
    SELECT
        c.customer_id,
        DATEDIFF(WEEK, c.signup_date, t.transaction_date) AS weeks_since_signup
    FROM customers c
    JOIN transactions t ON c.customer_id = t.customer_id
)
SELECT
    weeks_since_signup,
    COUNT(DISTINCT customer_id) AS active_users
FROM weekly_activity
GROUP BY weeks_since_signup
ORDER BY weeks_since_signup;

SELECT
    c.customer_id,
    SUM(t.amount) AS lifetime_value
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id
ORDER BY lifetime_value DESC;

SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    SUM(t.amount) AS total_revenue,
    AVG(t.amount) AS avg_revenue_per_customer
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.acquisition_channel
ORDER BY total_revenue DESC;

SELECT
    c.country,
    COUNT(DISTINCT c.customer_id) AS num_customers,
    SUM(t.amount) AS total_revenue,
    AVG(t.amount) AS avg_revenue
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.country
ORDER BY total_revenue DESC;

WITH purchase_counts AS (
    SELECT
        customer_id,
        COUNT(transaction_id) AS txn_count
    FROM transactions
    GROUP BY customer_id
)
SELECT
    COUNT(CASE WHEN txn_count > 1 THEN 1 END) * 1.0 / COUNT(*) AS repeat_purchase_rate
FROM purchase_counts;

WITH campaign_groups AS (
    SELECT
        customer_id,
        CASE WHEN customer_id % 2 = 0 THEN 'Group A' ELSE 'Group B' END AS test_group
    FROM customers
),
group_revenue AS (
    SELECT
        cg.test_group,
        AVG(t.amount) AS avg_revenue
    FROM campaign_groups cg
    JOIN transactions t ON cg.customer_id = t.customer_id
    GROUP BY cg.test_group
)
SELECT * FROM group_revenue;


SELECT
    FORMAT(session_date, 'yyyy-MM-dd') AS week_start,
    COUNT(DISTINCT customer_id) AS active_users
FROM sessions
GROUP BY FORMAT(session_date, 'yyyy-MM-dd')
ORDER BY week_start;
