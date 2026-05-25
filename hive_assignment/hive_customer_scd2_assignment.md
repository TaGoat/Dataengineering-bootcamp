# Hive Customer Tables and SCD Type 2 Assignment

## 1. Database Setup

First I selected the database I'm going to use for this assignment.

```sql
USE customer_dw;
```

All the tables in this report are created inside this database.

---

## 2. Creating External and Internal Customer Tables

### External Table

I created an external table to load the initial customer data. At first I used `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` but this caused problems with the Address column (more on that in Section 4). So I switched to `OpenCSVSerde` right away.

```sql
CREATE EXTERNAL TABLE ext_customer (
    CustomerID STRING,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\""
)
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/ext_customer'
TBLPROPERTIES ("skip.header.line.count"="1");
```

Note: `OpenCSVSerde` treats all columns as STRING type, so even `CustomerID` is defined as STRING here. This is a known limitation of this SerDe.

### Internal (Managed) Table

I also created a managed table to see the difference in behavior when dropping tables.

```sql
CREATE TABLE int_customer (
    CustomerID STRING,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");
```

### Loading Data

I loaded the `customer_scd2_mixed.csv` file into the external table.

```sql
LOAD DATA LOCAL INPATH '/home/cloudera/customer_scd2_mixed.csv'
OVERWRITE INTO TABLE ext_customer;
```

And also loaded data into the internal table.

```sql
INSERT INTO TABLE int_customer
SELECT * FROM ext_customer;
```

Both loaded successfully.

---

## 3. Dropping External and Internal Tables

I tested dropping both tables to see the difference.

```sql
DROP TABLE ext_customer;
DROP TABLE int_customer;
```

### What I Observed

- When I dropped the **external table**, Hive only removed the metadata (the table definition). The actual data files stayed in the HDFS location `/user/hive/warehouse/ext_customer`. I could still see the files with `hdfs dfs -ls`.

- When I dropped the **internal (managed) table**, Hive removed both the metadata and the data files from the warehouse directory. The data was completely gone.

This is the main difference between external and internal tables. External tables are safer if you don't want Hive to delete your data when you drop the table. Internal tables are fully managed by Hive.

After testing, I recreated the external table using the same DDL from Section 2 and reloaded the data since I needed it for the next steps.

---

## 4. Solving the Delimiter Problem in the Address Column

### The Problem

The customer CSV files use commas as separators. But some addresses also have commas inside them. For example:

```text
"36923 Bowers Gateway Suite 027 New Kristi, MP 44312"
```

If I use the normal `FIELDS TERMINATED BY ','`, Hive sees the comma after "Kristi" and thinks it's a new column. So the address gets split and all the columns after it shift over. The data becomes messy.

I noticed this when I first tried a simple delimited table and the results looked wrong, some rows had NULL values in the last columns and the Address was cut short.

### Solution: OpenCSVSerde

After some research I found that Hive has a built-in SerDe called `OpenCSVSerde` that can handle this. It reads the file as a proper CSV where quoted values are respected. So if an address is wrapped in double quotes, any commas inside won't be treated as column separators.

```sql
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\""
)
```

I kept comma as the separator (the assignment said don't change it) and set double-quote as the quote character. This way Hive reads the file correctly without me needing to modify the CSV at all.

The only downside is that `OpenCSVSerde` makes all columns STRING type, so I can't use INT or DATE directly. But for this assignment that's fine.

---

## 5. Creating the Customer Dimension Table (SCD Type 2)

I created the customer dimension table that will store the full history using SCD Type 2. I used ORC format since it compresses well and is efficient for queries.

```sql
CREATE TABLE customer_dim (
    CustomerID STRING,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
STORED AS ORC;
```

Then I loaded the initial dimension data from the `customer_scd2_mixed.csv` file through the external table. This file already has `Start_Date`, `End_Date`, and `Is_Current` columns so it serves as the starting point for the SCD2 dimension.

```sql
INSERT INTO TABLE customer_dim
SELECT * FROM ext_customer;
```

This ran successfully and loaded all the initial customer records into the dimension table.

---

## 6. Loading the Updated Customer Data

Next I needed to load the `customer_updated.csv` file which contains new and changed customer records. I created an external table for it. This file only has 6 columns (no Start_Date, End_Date, Is_Current) since those will be set during the SCD2 merge.

```sql
CREATE EXTERNAL TABLE ext_customer_updates (
    CustomerID STRING,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\""
)
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/ext_customer_updates'
TBLPROPERTIES ("skip.header.line.count"="1");
```

Then I loaded the CSV:

```sql
LOAD DATA LOCAL INPATH '/home/cloudera/customer_updated.csv'
OVERWRITE INTO TABLE ext_customer_updates;
```

The data loaded successfully.

---

## 7. SCD Type 2 Implementation (Without UPDATE or DELETE)

### The Problem

Hive doesn't support `UPDATE` or `DELETE` unless you enable ACID transactional tables. The assignment said not to use transactional tables, so I needed a workaround.

### The Workaround: INSERT OVERWRITE

The idea is simple: rebuild the entire dimension table from scratch using `INSERT OVERWRITE` with a `UNION ALL` of three parts:

1. **Unchanged records** - all rows for customers who are NOT in the update file. These stay exactly as they are.
2. **Existing records for updated customers** - for customers who appear in the update file, keep all their existing rows but expire the current one (set `End_Date` and `Is_Current = '0'`). Old already-expired rows stay unchanged so we don't lose history.
3. **New current records** - insert the updated/new customer data with `Start_Date = today`, `End_Date = NULL`, and `Is_Current = '1'`.

```sql
INSERT OVERWRITE TABLE customer_dim
SELECT * FROM (

    -- Part 1: All rows for customers NOT in the update file (unchanged)
    SELECT
        c.CustomerID, c.Name, c.Email, c.Phone_Number, c.Address,
        c.JOIN_Date, c.Start_Date, c.End_Date, c.Is_Current
    FROM customer_dim c
    LEFT JOIN ext_customer_updates u ON c.CustomerID = u.CustomerID
    WHERE u.CustomerID IS NULL

    UNION ALL

    -- Part 2: All existing rows for customers IN the update file
    -- Only expire the current row, keep already-expired history as-is
    SELECT
        c.CustomerID, c.Name, c.Email, c.Phone_Number, c.Address,
        c.JOIN_Date, c.Start_Date,
        CASE
            WHEN c.Is_Current = '1' THEN CAST(current_date() AS STRING)
            ELSE c.End_Date
        END AS End_Date,
        CASE
            WHEN c.Is_Current = '1' THEN '0'
            ELSE c.Is_Current
        END AS Is_Current
    FROM customer_dim c
    JOIN ext_customer_updates u ON c.CustomerID = u.CustomerID

    UNION ALL

    -- Part 3: New current records from the update file
    SELECT
        u.CustomerID, u.Name, u.Email, u.Phone_Number, u.Address,
        u.JOIN_Date,
        CAST(current_date() AS STRING) AS Start_Date,
        NULL AS End_Date,
        '1' AS Is_Current
    FROM ext_customer_updates u

) combined_data;
```

### Why Part 2 Uses CASE Instead of a Simple WHERE

This is important. At first I had Part 2 with `WHERE c.Is_Current = '1'` which only selected the current active rows for updated customers. But I realized that would lose any old expired history rows for those customers since Part 1 excludes them too (they have a matching CustomerID in the update file).

So instead, Part 2 selects ALL rows for customers who appear in the update file. The `CASE` statements only change the `End_Date` and `Is_Current` for rows that are currently active (`Is_Current = '1'`). Already-expired rows pass through unchanged. This way no historical data gets lost.

---

## 8. Checking the Results

To verify the SCD Type 2 worked, I ran a few checks.

### Check 1: Specific Customer History

I picked customer 12738 (Jimmy Johnson) who appears in both the original dimension and the update file to see if the history was tracked properly.

```sql
SELECT CustomerID, Name, Email, Start_Date, End_Date, Is_Current
FROM customer_dim
WHERE CustomerID = '12738'
ORDER BY Start_Date;
```

Result:

```text
+-----------+---------------+---------------------------+------------+------------+------------+
|CustomerID |      Name     |          Email            | Start_Date |  End_Date  | Is_Current |
+-----------+---------------+---------------------------+------------+------------+------------+
|   12738   | Jimmy Johnson | candace51@example.net     | 4/1/2025   | 2025-05-24 |     0      |
|   12738   | Jimmy Johnson | upd_candace51@example.net | 2025-05-24 |    NULL    |     1      |
+-----------+---------------+---------------------------+------------+------------+------------+
```

The old record got expired (End_Date set to today, Is_Current = 0) and the new record from the update file is now current. The email changed from `candace51@example.net` to `upd_candace51@example.net` which shows the update was tracked.

### Check 2: Count of Current vs Expired Records

```sql
SELECT Is_Current, COUNT(*) AS cnt
FROM customer_dim
GROUP BY Is_Current;
```

This helped me confirm that the number of expired and current records makes sense. There should be more current records than expired ones since not every customer had a change.

### Check 3: No Duplicate Current Records

```sql
SELECT CustomerID, COUNT(*) AS cnt
FROM customer_dim
WHERE Is_Current = '1'
GROUP BY CustomerID
HAVING COUNT(*) > 1;
```

This returned 0 rows which means no customer has more than one current record. That's correct for SCD Type 2.

