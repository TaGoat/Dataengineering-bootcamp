# Olist E-Commerce Data Warehouse — Documentation

## 1. Architecture Overview

I chose a **Kimball star schema** architecture for this project because the main goal is enabling analytical queries for business users. Kimball's approach works well here because:

- The data has a clear business process (e-commerce sales) with identifiable facts and dimensions
- Star schemas are simple to query — business users can write straightforward JOINs
- The dataset is relatively small (~100K orders), so the denormalized approach won't cause storage issues
- It's widely used in industry and well-documented

### Architecture Diagram

![Architecture Diagram](architecture_diagram.png)

## 2. Data Model
![modeling_schema](modeling_schema.png)
### Business Process

I identified **1 business process: E-commerce Sales**. This process is modeled using 2 fact tables at different grain levels (the header/line pattern):

| Fact Table | Grain | What It Captures |
|---|---|---|
| `fact_orders` | 1 row per order | Payments, reviews, delivery performance |
| `fact_order_items` | 1 row per item in an order | Price, freight, product, seller |

Why 2 tables instead of 1? Because the source data has measures at 2 different levels:
- Payment totals and review scores belong to the order as a whole
- Price and freight differ for each item within an order

If I put everything in one table, payment and review values would repeat across every item row, creating a double-counting risk when doing SUM aggregations.

### Dimensions

| Dimension | Rows | Key Attributes |
|---|---|---|
| `dim_customer` | 99,441 | unique_id, city, state, zip code |
| `dim_product` | 32,951 | category (Portuguese + English), physical dimensions, weight |
| `dim_seller` | 3,095 | city, state, zip code |
| `dim_date` | 1,340 | full calendar attributes (role-playing) |
| `dim_payment_type` | 5 | type name, description |
| `dim_order_status` | 8 | status, is_completed, is_canceled |



## 3. Pipeline Design

### Approach

I built a **batch ETL pipeline in Python** using the `sqlite3` standard library. Python + SQLite was chosen because:
- No external dependencies needed
- The dataset fits in memory, so batch processing is efficient
- SQLite is portable

### Pipeline Steps

1. **Schema Creation** — Reads `schema.sql` and creates all tables with foreign keys and indexes
2. **Dimension Loading**:
   - `dim_date` — Generated from all date columns in source, with a -1 placeholder for NULLs
   - `dim_customer` — Direct load from customers table
   - `dim_product` — Joined with category translations, typos in column names fixed
   - `dim_seller` — Direct load from sellers table
   - `dim_payment_type` — Static insert of 5 payment types
   - `dim_order_status` — Static insert of 8 statuses
3. **Lookup Maps** — Build in-memory dictionaries mapping natural keys to surrogate keys
4. **Fact Loading**:
   - `fact_orders` — Aggregates payments and items per order, derives shipping and delivery metrics
   - `fact_order_items` — Maps each line item to dimension surrogate keys
5. **Validation** — Prints row counts for all tables

### Reproducibility

The pipeline does a full refresh — if the target database exists, it's deleted and rebuilt from scratch. Running `python etl_pipeline.py` always produces the same result.

## 4. Data Quality Issues & Mitigations

| Issue | How I Handled It |
|---|---|
| Column typos (`product_name_lenght`) | Renamed to `product_name_length` in dim_product |
| Duplicate customer IDs | Kept both `customer_id` and `customer_unique_id` — use unique_id for counting people |
| NULL delivery dates | Mapped to `date_sk = -1` ("N/A" row in dim_date) |
| Missing reviews | `has_review` flag distinguishes no review from score=0, review_score is nullable |
| Canceled orders | Kept in the warehouse but filterable via `dim_order_status.is_canceled` |
| Payment value vs item price mismatch | Stored both `total_payment_value` and `total_order_value` independently |

## 5. Performance Optimization

### Indexing

I created indexes on all foreign key columns in both fact tables:

```
fact_orders:      customer_sk, order_status_sk, purchase_date_sk, order_id
fact_order_items: order_id, product_sk, seller_sk, purchase_date_sk, customer_sk
```

These speed up the star-join pattern which is the most common query type. The `order_id` index on both tables is important for joining the two fact tables together.

### What I Would Add at Scale

- **Partitioning** by `purchase_date_sk` (year/month) since most queries filter by date range
- **Column-oriented storage** (like Parquet or DuckDB) for better scan performance on wide fact tables

## 6. Key Assumptions

1. Each order has at most one review
2. The "primary" payment type is the one with the highest payment value for that order
3. `is_late_delivery` is based on comparing actual delivery date vs estimated delivery date
4. Shipping days = calendar days between purchase and customer delivery

## 7. Trade-offs

| Decision | Pro | Con |
|---|---|---|
| 2 fact tables instead of 1 | No double-counting, each measure at natural grain | Requires JOIN for cross-grain analysis |
| Full refresh ETL | Simple, always consistent | Slower than incremental for large datasets |
| SQLite as DWH | Zero setup, portable | No concurrent users, limited SQL features |
| SCD Type 1 only | Simple to implement | Lose historical attribute values |
| Aggregating payments to order level | Simpler model | Can't analyze individual payment transactions |

## 8. File Structure

```
datawarehouse task/
├── Database/
│   ├── olist.sqlite           # Source database (10 tables)
│   └── olist_dwh.sqlite       # Target data warehouse (star schema)
├── schema.sql                 # DDL — CREATE TABLE statements + indexes
├── etl_pipeline.py            # Python ETL script
├── analytical_queries.sql     # Sample queries for the 4 business questions
└── documentation.md           # This file
```
