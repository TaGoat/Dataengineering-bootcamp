import csv
import random
import time
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

output_dir = "streaming_data"
os.makedirs(output_dir, exist_ok=True)

headers = ["order_id", "customer_name", "email", "product", "quantity", "price", "order_date", "shipping_address", "status"]

products = [
    ("Wireless Mouse", 25.99),
    ("USB Keyboard", 45.50),
    ("Monitor Stand", 89.99),
    ("Laptop Bag", 34.75),
    ("Webcam HD", 59.00),
    ("Desk Lamp", 22.30),
    ("Phone Charger", 15.99),
    ("Bluetooth Speaker", 42.00),
    ("Mouse Pad", 12.50),
    ("HDMI Cable", 8.99),
    ("Gaming Headset", 79.99),
    ("USB Hub", 19.49),
    ("Laptop Stand", 55.00),
    ("Wireless Earbuds", 64.99),
    ("Screen Protector", 9.99),
]

statuses = ["pending", "shipped", "delivered", "cancelled", "processing", "returned"]


def random_timestamp():
    fmt = random.choice(["iso", "us", "eu", "unix", "weird"])
    base = fake.date_time_between(start_date="-30d", end_date="now")

    if fmt == "iso":
        return base.strftime("%Y-%m-%dT%H:%M:%S")
    elif fmt == "us":
        return base.strftime("%m/%d/%Y %I:%M %p")
    elif fmt == "eu":
        return base.strftime("%d-%m-%Y %H:%M")
    elif fmt == "unix":
        return str(int(base.timestamp()))
    else:
        return base.strftime("%B %d %Y, %H:%M:%S")


def generate_normal_record(order_id):
    name = fake.name()
    email = fake.email()
    product, base_price = random.choice(products)
    qty = random.randint(1, 5)
    price = round(base_price * qty, 2)
    date = random_timestamp()
    address = fake.address().replace("\n", ", ")
    status = random.choice(statuses)

    return [order_id, name, email, product, qty, price, date, address, status]


def add_missing_values(record):
    rec = list(record)
    indexes_to_blank = random.sample(range(1, len(rec)), random.randint(1, 3))
    for i in indexes_to_blank:
        rec[i] = random.choice(["", "N/A", "null", "None", "  "])
    return rec


def make_corrupted_row():
    garbage = []
    for _ in range(random.randint(2, 12)):
        garbage.append(random.choice(["@#$", "???", "NULL", "", "0x00", "corrupted", "ERR", str(random.randint(-999, 999))]))
    return garbage


def make_invalid_record(order_id):
    rec = generate_normal_record(order_id)
    problem = random.choice(["neg_qty", "neg_price", "zero_price", "bad_email", "future_date", "huge_qty"])

    if problem == "neg_qty":
        rec[4] = -random.randint(1, 10)
    elif problem == "neg_price":
        rec[5] = -round(random.uniform(1, 100), 2)
    elif problem == "zero_price":
        rec[5] = 0.0
    elif problem == "bad_email":
        rec[2] = random.choice(["notanemail", "user@@domain", "missing.com", "@no_user.com", "spaces in email@test.com"])
    elif problem == "future_date":
        future = datetime.now() + timedelta(days=random.randint(100, 1000))
        rec[6] = future.strftime("%Y-%m-%d")
    elif problem == "huge_qty":
        rec[4] = random.randint(10000, 99999)

    return rec


def make_numeric_inconsistency(record):
    rec = list(record)
    issue = random.choice(["string_qty", "string_price", "comma_price", "extra_decimal"])

    if issue == "string_qty":
        rec[4] = random.choice(["two", "five", "ten", "three items", "1 or 2"])
    elif issue == "string_price":
        rec[5] = random.choice(["free", "TBD", "call for price", "$25", "USD 40.00"])
    elif issue == "comma_price":
        rec[5] = "1,234.56"
    elif issue == "extra_decimal":
        rec[5] = round(random.uniform(10, 500), 5)

    return rec


def generate_record(order_id):
    roll = random.random()
    rows = []

    if roll < 0.50:
        rows.append(generate_normal_record(order_id))
    elif roll < 0.65:
        rows.append(add_missing_values(generate_normal_record(order_id)))
    elif roll < 0.75:
        rec = generate_normal_record(order_id)
        rows.append(rec)
        rows.append(list(rec))
    elif roll < 0.83:
        rows.append(make_invalid_record(order_id))
    elif roll < 0.90:
        rows.append(make_corrupted_row())
    elif roll < 0.95:
        rows.append(make_numeric_inconsistency(generate_normal_record(order_id)))
    else:
        rec = generate_normal_record(order_id)
        rec[6] = random_timestamp()
        rows.append(rec)

    return rows


order_counter = 1000
file_count = 0
batch_size = random.randint(5, 2000)

print("Starting e-commerce data generator...")
print("Output directory:", output_dir)
print("Press Ctrl+C to stop\n")

try:
    while True:
        batch_size = random.randint(5, 2000)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_{timestamp}_{file_count}.csv"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for _ in range(batch_size):
                rows = generate_record(order_counter)
                for row in rows:
                    writer.writerow(row)
                order_counter += 1

        file_count += 1
        print(f"[File {file_count}] {filename} - {batch_size} orders written")

        time.sleep(random.uniform(1, 3))

except KeyboardInterrupt:
    print(f"\nStopped. Total files created: {file_count}")
    print(f"Total orders generated: {order_counter - 1000}")
