-- Q1: How are sales trending over time?

SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(f.order_sk) AS total_orders,
    SUM(f.total_payment_value) AS total_revenue,
    ROUND(AVG(f.total_payment_value), 2) AS avg_order_value,
    SUM(f.num_items) AS total_items_sold
FROM fact_orders f
JOIN dim_date d ON f.purchase_date_sk = d.date_sk
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


WITH quarterly AS (
    SELECT
        d.year,
        d.quarter,
        SUM(f.total_payment_value) AS revenue
    FROM fact_orders f
    JOIN dim_date d ON f.purchase_date_sk = d.date_sk
    JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
    WHERE s.is_canceled = 0
    GROUP BY d.year, d.quarter
)
SELECT
    year,
    quarter,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year, quarter))
        / LAG(revenue) OVER (ORDER BY year, quarter) * 100
    , 1) AS growth_pct
FROM quarterly
ORDER BY year, quarter;


SELECT
    CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(f.order_sk) AS total_orders,
    ROUND(SUM(f.total_payment_value), 2) AS total_revenue,
    ROUND(AVG(f.total_payment_value), 2) AS avg_order_value
FROM fact_orders f
JOIN dim_date d ON f.purchase_date_sk = d.date_sk
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
GROUP BY day_type;


-- Q2: Who are the most valuable customers?

SELECT
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(f.order_sk) AS num_orders,
    ROUND(SUM(f.total_payment_value), 2) AS total_spent,
    ROUND(AVG(f.review_score), 1) AS avg_review_score
FROM fact_orders f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
ORDER BY total_spent DESC
LIMIT 20;


WITH customer_spend AS (
    SELECT
        c.customer_unique_id,
        SUM(f.total_payment_value) AS total_spent,
        COUNT(f.order_sk) AS num_orders
    FROM fact_orders f
    JOIN dim_customer c ON f.customer_sk = c.customer_sk
    JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
    WHERE s.is_canceled = 0
    GROUP BY c.customer_unique_id
)
SELECT
    CASE
        WHEN total_spent >= 1000 THEN 'High Value'
        WHEN total_spent >= 300 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_tier,
    COUNT(*) AS num_customers,
    ROUND(AVG(total_spent), 2) AS avg_spending,
    ROUND(SUM(total_spent), 2) AS tier_total_revenue
FROM customer_spend
GROUP BY customer_tier
ORDER BY avg_spending DESC;


SELECT
    c.customer_state,
    COUNT(f.order_sk) AS total_orders,
    ROUND(SUM(f.total_payment_value), 2) AS total_revenue,
    ROUND(AVG(f.total_payment_value), 2) AS avg_order_value
FROM fact_orders f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
GROUP BY c.customer_state
ORDER BY total_revenue DESC;


-- Q3: What affects delivery performance?

SELECT
    c.customer_state,
    COUNT(f.order_sk) AS total_orders,
    SUM(f.is_late_delivery) AS late_deliveries,
    ROUND(SUM(f.is_late_delivery) * 100.0 / COUNT(f.order_sk), 1) AS late_pct,
    ROUND(AVG(f.shipping_days), 1) AS avg_shipping_days,
    ROUND(AVG(f.review_score), 2) AS avg_review_score
FROM fact_orders f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_completed = 1
GROUP BY c.customer_state
HAVING total_orders >= 50
ORDER BY late_pct DESC;


SELECT
    CASE WHEN f.is_late_delivery = 1 THEN 'Late' ELSE 'On Time' END AS delivery_status,
    COUNT(f.order_sk) AS total_orders,
    ROUND(AVG(f.review_score), 2) AS avg_review_score,
    ROUND(AVG(f.shipping_days), 1) AS avg_shipping_days
FROM fact_orders f
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_completed = 1 AND f.has_review = 1
GROUP BY delivery_status;


SELECT
    sel.seller_state,
    COUNT(fi.order_item_sk) AS total_items,
    ROUND(AVG(fo.shipping_days), 1) AS avg_shipping_days,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score
FROM fact_order_items fi
JOIN dim_seller sel ON fi.seller_sk = sel.seller_sk
JOIN fact_orders fo ON fi.order_id = fo.order_id
JOIN dim_order_status s ON fo.order_status_sk = s.order_status_sk
WHERE s.is_completed = 1
GROUP BY sel.seller_state
ORDER BY avg_shipping_days DESC;


-- Q4: Which products/categories drive revenue?

SELECT
    p.product_category_name_english,
    COUNT(fi.order_item_sk) AS items_sold,
    ROUND(SUM(fi.price), 2) AS total_revenue,
    ROUND(AVG(fi.price), 2) AS avg_price,
    ROUND(SUM(fi.freight_value), 2) AS total_freight
FROM fact_order_items fi
JOIN dim_product p ON fi.product_sk = p.product_sk
JOIN dim_order_status s ON fi.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
  AND p.product_category_name_english IS NOT NULL
GROUP BY p.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 15;


SELECT
    sel.seller_id,
    sel.seller_city,
    sel.seller_state,
    COUNT(fi.order_item_sk) AS items_sold,
    ROUND(SUM(fi.price), 2) AS total_revenue,
    ROUND(AVG(fi.price), 2) AS avg_item_price
FROM fact_order_items fi
JOIN dim_seller sel ON fi.seller_sk = sel.seller_sk
JOIN dim_order_status s ON fi.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
GROUP BY sel.seller_id, sel.seller_city, sel.seller_state
ORDER BY total_revenue DESC
LIMIT 10;


SELECT
    p.product_category_name_english,
    COUNT(fi.order_item_sk) AS items_sold,
    ROUND(SUM(fi.price), 2) AS total_revenue,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score,
    ROUND(AVG(fo.shipping_days), 1) AS avg_shipping_days
FROM fact_order_items fi
JOIN dim_product p ON fi.product_sk = p.product_sk
JOIN fact_orders fo ON fi.order_id = fo.order_id
JOIN dim_order_status s ON fi.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
  AND fo.has_review = 1
  AND p.product_category_name_english IS NOT NULL
GROUP BY p.product_category_name_english
HAVING items_sold >= 100
ORDER BY avg_review_score ASC
LIMIT 15;


SELECT
    pt.payment_type_description,
    COUNT(f.order_sk) AS total_orders,
    ROUND(SUM(f.total_payment_value), 2) AS total_revenue,
    ROUND(AVG(f.total_payment_value), 2) AS avg_order_value,
    ROUND(AVG(f.max_installments), 1) AS avg_max_installments
FROM fact_orders f
JOIN dim_payment_type pt ON f.primary_payment_type_sk = pt.payment_type_sk
JOIN dim_order_status s ON f.order_status_sk = s.order_status_sk
WHERE s.is_canceled = 0
GROUP BY pt.payment_type_description
ORDER BY total_revenue DESC;
