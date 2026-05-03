import sqlite3
import os
from datetime import datetime, timedelta

SOURCE_DB = "Database/olist.sqlite"
TARGET_DB = "Database/olist_dwh.sqlite"

PAYMENT_DESCRIPTIONS = {
    "credit_card": "Credit Card",
    "boleto": "Boleto Bancario",
    "voucher": "Voucher",
    "debit_card": "Debit Card",
    "not_defined": "Not Defined"
}

STATUS_DESCRIPTIONS = {
    "delivered": "Order delivered to customer",
    "shipped": "Order shipped, in transit",
    "canceled": "Order was canceled",
    "unavailable": "Product unavailable",
    "invoiced": "Invoice generated",
    "processing": "Order is being processed",
    "created": "Order created",
    "approved": "Payment approved"
}


def make_date_sk(date_str):
    if date_str is None or date_str.strip() == "":
        return -1
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return int(dt.strftime("%Y%m%d"))
    except ValueError:
        return -1


def days_between(date_str1, date_str2):
    if not date_str1 or not date_str2:
        return None
    try:
        d1 = datetime.strptime(date_str1[:10], "%Y-%m-%d")
        d2 = datetime.strptime(date_str2[:10], "%Y-%m-%d")
        return (d2 - d1).days
    except ValueError:
        return None


def load_dim_date(source_conn, target_conn):
    print("Loading dim_date...")

    dates = set()
    date_columns = [
        ("orders", "order_purchase_timestamp"),
        ("orders", "order_approved_at"),
        ("orders", "order_delivered_carrier_date"),
        ("orders", "order_delivered_customer_date"),
        ("orders", "order_estimated_delivery_date"),
        ("order_reviews", "review_creation_date"),
        ("order_reviews", "review_answer_timestamp"),
        ("order_items", "shipping_limit_date"),
    ]

    for table, col in date_columns:
        rows = source_conn.execute(f"SELECT DISTINCT [{col}] FROM [{table}] WHERE [{col}] IS NOT NULL").fetchall()
        for row in rows:
            if row[0] and row[0].strip():
                try:
                    dates.add(datetime.strptime(row[0][:10], "%Y-%m-%d").date())
                except ValueError:
                    pass

    min_date = min(dates).replace(day=1)
    max_date = (max(dates).replace(day=28) + timedelta(days=4)).replace(day=1)

    target_conn.execute("INSERT OR IGNORE INTO dim_date VALUES (-1, 'N/A', 0, 'N/A', 0, 0, 0, 'N/A', 0, 0, 0)")

    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    current = min_date
    batch = []
    while current <= max_date:
        dow = current.isoweekday()
        batch.append((
            int(current.strftime("%Y%m%d")),
            current.isoformat(),
            dow,
            day_names[dow - 1],
            current.day,
            current.isocalendar()[1],
            current.month,
            month_names[current.month],
            (current.month - 1) // 3 + 1,
            current.year,
            1 if dow >= 6 else 0
        ))
        current += timedelta(days=1)

    target_conn.executemany("""
        INSERT OR IGNORE INTO dim_date
        (date_sk, full_date, day_of_week, day_name, day_of_month, week_of_year,
         month, month_name, quarter, year, is_weekend)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, batch)
    target_conn.commit()
    print(f"  {len(batch)} rows")


def load_dim_customer(source_conn, target_conn):
    print("Loading dim_customer...")

    customers = source_conn.execute("""
        SELECT customer_id, customer_unique_id, customer_city, customer_state, customer_zip_code_prefix
        FROM customers
    """).fetchall()

    target_conn.executemany("""
        INSERT INTO dim_customer
        (customer_id, customer_unique_id, customer_city, customer_state, customer_zip_code_prefix)
        VALUES (?,?,?,?,?)
    """, customers)
    target_conn.commit()
    print(f"  {len(customers)} rows")


def load_dim_product(source_conn, target_conn):
    print("Loading dim_product...")

    translations = {}
    for r in source_conn.execute("SELECT product_category_name, product_category_name_english FROM product_category_name_translation").fetchall():
        translations[r[0]] = r[1]

    products = source_conn.execute("""
        SELECT product_id, product_category_name,
               product_name_lenght, product_description_lenght,
               product_photos_qty, product_weight_g,
               product_length_cm, product_height_cm, product_width_cm
        FROM products
    """).fetchall()

    batch = []
    for pid, cat, name_len, desc_len, photos, weight, length, height, width in products:
        cat_eng = translations.get(cat, None)
        name_len = int(name_len) if name_len else None
        desc_len = int(desc_len) if desc_len else None
        photos = int(photos) if photos else None
        batch.append((pid, cat, cat_eng, name_len, desc_len, photos, weight, length, height, width))

    target_conn.executemany("""
        INSERT INTO dim_product
        (product_id, product_category_name, product_category_name_english,
         product_name_length, product_description_length, product_photos_qty,
         product_weight_g, product_length_cm, product_height_cm, product_width_cm)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, batch)
    target_conn.commit()
    print(f"  {len(batch)} rows")


def load_dim_seller(source_conn, target_conn):
    print("Loading dim_seller...")

    sellers = source_conn.execute("SELECT seller_id, seller_city, seller_state, seller_zip_code_prefix FROM sellers").fetchall()

    target_conn.executemany("""
        INSERT INTO dim_seller (seller_id, seller_city, seller_state, seller_zip_code_prefix)
        VALUES (?,?,?,?)
    """, sellers)
    target_conn.commit()
    print(f"  {len(sellers)} rows")


def load_dim_payment_type(target_conn):
    print("Loading dim_payment_type...")

    batch = []
    for pt in ["credit_card", "boleto", "voucher", "debit_card", "not_defined"]:
        batch.append((pt, PAYMENT_DESCRIPTIONS.get(pt, pt)))

    target_conn.executemany("INSERT INTO dim_payment_type (payment_type, payment_type_description) VALUES (?,?)", batch)
    target_conn.commit()
    print(f"  {len(batch)} rows")


def load_dim_order_status(target_conn):
    print("Loading dim_order_status...")

    batch = []
    for s in ["delivered", "shipped", "canceled", "unavailable", "invoiced", "processing", "created", "approved"]:
        batch.append((s, STATUS_DESCRIPTIONS.get(s, s), 1 if s == "delivered" else 0, 1 if s == "canceled" else 0))

    target_conn.executemany("INSERT INTO dim_order_status (order_status, status_description, is_completed, is_canceled) VALUES (?,?,?,?)", batch)
    target_conn.commit()
    print(f"  {len(batch)} rows")


def build_lookup_maps(target_conn):
    lookups = {}
    lookups["customer"] = dict(target_conn.execute("SELECT customer_id, customer_sk FROM dim_customer").fetchall())
    lookups["product"] = dict(target_conn.execute("SELECT product_id, product_sk FROM dim_product").fetchall())
    lookups["seller"] = dict(target_conn.execute("SELECT seller_id, seller_sk FROM dim_seller").fetchall())
    lookups["status"] = dict(target_conn.execute("SELECT order_status, order_status_sk FROM dim_order_status").fetchall())
    lookups["payment"] = dict(target_conn.execute("SELECT payment_type, payment_type_sk FROM dim_payment_type").fetchall())
    return lookups


def load_fact_orders(source_conn, target_conn, lookups):
    print("Loading fact_orders...")

    payment_agg = {}
    for r in source_conn.execute("SELECT order_id, SUM(payment_value), COUNT(payment_sequential), MAX(payment_installments) FROM order_payments GROUP BY order_id").fetchall():
        payment_agg[r[0]] = {"total": r[1], "methods": r[2], "max_install": r[3]}

    primary_payment = {}
    for r in source_conn.execute("""
        SELECT op.order_id, op.payment_type
        FROM order_payments op
        INNER JOIN (
            SELECT order_id, MAX(payment_value) AS max_val FROM order_payments GROUP BY order_id
        ) mx ON op.order_id = mx.order_id AND op.payment_value = mx.max_val
        GROUP BY op.order_id
    """).fetchall():
        primary_payment[r[0]] = r[1]

    item_agg = {}
    for r in source_conn.execute("SELECT order_id, SUM(price), SUM(freight_value), COUNT(*), COUNT(DISTINCT seller_id) FROM order_items GROUP BY order_id").fetchall():
        item_agg[r[0]] = {"price": r[1], "freight": r[2], "num_items": r[3], "num_sellers": r[4]}

    review_data = {}
    for r in source_conn.execute("SELECT order_id, review_score FROM order_reviews").fetchall():
        review_data[r[0]] = r[1]

    orders = source_conn.execute("""
        SELECT order_id, customer_id, order_status,
               order_purchase_timestamp, order_approved_at,
               order_delivered_carrier_date, order_delivered_customer_date,
               order_estimated_delivery_date
        FROM orders
    """).fetchall()

    batch = []
    for oid, cid, status, purchase, approved, carrier, delivered, estimated in orders:
        customer_sk = lookups["customer"].get(cid)
        status_sk = lookups["status"].get(status, lookups["status"].get("processing"))
        pp_sk = lookups["payment"].get(primary_payment.get(oid, "not_defined"), lookups["payment"].get("not_defined"))

        pay = payment_agg.get(oid, {"total": 0, "methods": 0, "max_install": 0})
        items = item_agg.get(oid, {"price": 0, "freight": 0, "num_items": 0, "num_sellers": 0})
        total_order = (items["price"] or 0) + (items["freight"] or 0)

        shipping_d = days_between(purchase, delivered)
        est_days = days_between(delivered, estimated)
        is_late = 1 if (est_days is not None and est_days < 0) else 0

        review_score = review_data.get(oid)
        has_review = 1 if review_score is not None else 0

        batch.append((
            oid, customer_sk, status_sk, pp_sk,
            make_date_sk(purchase), make_date_sk(approved), make_date_sk(carrier),
            make_date_sk(delivered), make_date_sk(estimated),
            pay["total"], pay["methods"], pay["max_install"],
            items["price"], items["freight"], total_order,
            items["num_items"], items["num_sellers"],
            shipping_d, is_late, review_score, has_review, 1
        ))

    target_conn.executemany("""
        INSERT INTO fact_orders
        (order_id, customer_sk, order_status_sk, primary_payment_type_sk,
         purchase_date_sk, approved_date_sk, delivered_carrier_date_sk,
         delivered_customer_date_sk, estimated_delivery_date_sk,
         total_payment_value, num_payment_methods, max_installments,
         total_items_price, total_freight_value, total_order_value,
         num_items, num_distinct_sellers,
         shipping_days, is_late_delivery, review_score, has_review, order_count)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, batch)
    target_conn.commit()
    print(f"  {len(batch)} rows")


def load_fact_order_items(source_conn, target_conn, lookups):
    print("Loading fact_order_items...")

    order_info = {}
    for r in source_conn.execute("SELECT order_id, customer_id, order_status, order_purchase_timestamp FROM orders").fetchall():
        order_info[r[0]] = {"customer_id": r[1], "status": r[2], "purchase": r[3]}

    items = source_conn.execute("""
        SELECT order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value
        FROM order_items
    """).fetchall()

    batch = []
    for oid, item_id, pid, sid, ship_date, price, freight in items:
        info = order_info.get(oid, {})
        customer_sk = lookups["customer"].get(info.get("customer_id"))
        product_sk = lookups["product"].get(pid)
        seller_sk = lookups["seller"].get(sid)
        status_sk = lookups["status"].get(info.get("status"), lookups["status"].get("processing"))

        batch.append((
            oid, item_id, customer_sk, product_sk, seller_sk, status_sk,
            make_date_sk(info.get("purchase")), make_date_sk(ship_date),
            price, freight, (price or 0) + (freight or 0), 1
        ))

    target_conn.executemany("""
        INSERT INTO fact_order_items
        (order_id, order_item_id, customer_sk, product_sk, seller_sk, order_status_sk,
         purchase_date_sk, shipping_limit_date_sk,
         price, freight_value, total_item_value, item_count)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, batch)
    target_conn.commit()
    print(f"  {len(batch)} rows")


if __name__ == "__main__":
    print("Starting ETL pipeline...")

    if os.path.exists(TARGET_DB):
        os.remove(TARGET_DB)

    source_conn = sqlite3.connect(SOURCE_DB)
    target_conn = sqlite3.connect(TARGET_DB)

    with open("schema.sql", "r") as f:
        target_conn.executescript(f.read())
    print("Schema created.")

    load_dim_date(source_conn, target_conn)
    load_dim_customer(source_conn, target_conn)
    load_dim_product(source_conn, target_conn)
    load_dim_seller(source_conn, target_conn)
    load_dim_payment_type(target_conn)
    load_dim_order_status(target_conn)

    lookups = build_lookup_maps(target_conn)

    load_fact_orders(source_conn, target_conn, lookups)
    load_fact_order_items(source_conn, target_conn, lookups)

    print("\nRow counts:")
    for table in ["dim_date", "dim_customer", "dim_product", "dim_seller",
                   "dim_payment_type", "dim_order_status", "fact_orders", "fact_order_items"]:
        count = target_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")

    source_conn.close()
    target_conn.close()
    print("\nDone.")
