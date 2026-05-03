CREATE TABLE IF NOT EXISTS dim_date (
    date_sk INTEGER PRIMARY KEY,
    full_date TEXT,
    day_of_week INTEGER,
    day_name TEXT,
    day_of_month INTEGER,
    week_of_year INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER,
    year INTEGER,
    is_weekend INTEGER
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT,
    customer_unique_id TEXT,
    customer_city TEXT,
    customer_state TEXT,
    customer_zip_code_prefix INTEGER
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,
    product_category_name TEXT,
    product_category_name_english TEXT,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g REAL,
    product_length_cm REAL,
    product_height_cm REAL,
    product_width_cm REAL
);

CREATE TABLE IF NOT EXISTS dim_seller (
    seller_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id TEXT,
    seller_city TEXT,
    seller_state TEXT,
    seller_zip_code_prefix INTEGER
);

CREATE TABLE IF NOT EXISTS dim_payment_type (
    payment_type_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_type TEXT,
    payment_type_description TEXT
);

CREATE TABLE IF NOT EXISTS dim_order_status (
    order_status_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    order_status TEXT,
    status_description TEXT,
    is_completed INTEGER,
    is_canceled INTEGER
);

CREATE TABLE IF NOT EXISTS fact_orders (
    order_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    customer_sk INTEGER,
    order_status_sk INTEGER,
    primary_payment_type_sk INTEGER,
    purchase_date_sk INTEGER,
    approved_date_sk INTEGER,
    delivered_carrier_date_sk INTEGER,
    delivered_customer_date_sk INTEGER,
    estimated_delivery_date_sk INTEGER,
    total_payment_value REAL,
    num_payment_methods INTEGER,
    max_installments INTEGER,
    total_items_price REAL,
    total_freight_value REAL,
    total_order_value REAL,
    num_items INTEGER,
    num_distinct_sellers INTEGER,
    shipping_days INTEGER,
    is_late_delivery INTEGER,
    review_score INTEGER,
    has_review INTEGER,
    order_count INTEGER DEFAULT 1,
    FOREIGN KEY (customer_sk) REFERENCES dim_customer(customer_sk),
    FOREIGN KEY (order_status_sk) REFERENCES dim_order_status(order_status_sk),
    FOREIGN KEY (primary_payment_type_sk) REFERENCES dim_payment_type(payment_type_sk),
    FOREIGN KEY (purchase_date_sk) REFERENCES dim_date(date_sk),
    FOREIGN KEY (approved_date_sk) REFERENCES dim_date(date_sk),
    FOREIGN KEY (delivered_carrier_date_sk) REFERENCES dim_date(date_sk),
    FOREIGN KEY (delivered_customer_date_sk) REFERENCES dim_date(date_sk),
    FOREIGN KEY (estimated_delivery_date_sk) REFERENCES dim_date(date_sk)
);

CREATE TABLE IF NOT EXISTS fact_order_items (
    order_item_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    order_item_id INTEGER,
    customer_sk INTEGER,
    product_sk INTEGER,
    seller_sk INTEGER,
    order_status_sk INTEGER,
    purchase_date_sk INTEGER,
    shipping_limit_date_sk INTEGER,
    price REAL,
    freight_value REAL,
    total_item_value REAL,
    item_count INTEGER DEFAULT 1,
    FOREIGN KEY (customer_sk) REFERENCES dim_customer(customer_sk),
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
    FOREIGN KEY (seller_sk) REFERENCES dim_seller(seller_sk),
    FOREIGN KEY (order_status_sk) REFERENCES dim_order_status(order_status_sk),
    FOREIGN KEY (purchase_date_sk) REFERENCES dim_date(date_sk),
    FOREIGN KEY (shipping_limit_date_sk) REFERENCES dim_date(date_sk)
);

CREATE INDEX IF NOT EXISTS idx_fact_orders_customer ON fact_orders(customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_status ON fact_orders(order_status_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_purchase_date ON fact_orders(purchase_date_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_order_id ON fact_orders(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_items_order_id ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_items_product ON fact_order_items(product_sk);
CREATE INDEX IF NOT EXISTS idx_fact_items_seller ON fact_order_items(seller_sk);
CREATE INDEX IF NOT EXISTS idx_fact_items_purchase_date ON fact_order_items(purchase_date_sk);
CREATE INDEX IF NOT EXISTS idx_fact_items_customer ON fact_order_items(customer_sk);
