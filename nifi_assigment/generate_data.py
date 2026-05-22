import os, csv, random, time, json
from datetime import datetime

output_dir = r"D:\Data Engineering Bootcamp\Data\nifi_data"


names = ["Ahmad", "Sara", "Omar", "Lina", "Khaled", "Noor", "Tareq", "Dana", "Youssef", "Hana"]
cities = ["Sanaa", "sanaa", "SANAA", "Aden", "aden", "Taiz", "taiz", "Mukalla"]
products = ["Laptop", "laptop", "Phone", "phone", "Tablet", "tablet", "Headphones", "headphones"]

def make_row():
    row = {
        "name": random.choice(names) if random.random() > 0.1 else "",
        "age": random.choice([random.randint(18, 65), "", "N/A", None]),
        "city": random.choice(cities) if random.random() > 0.08 else None,
        "product": random.choice(products),
        "price": round(random.uniform(5, 500), 2) if random.random() > 0.12 else "",
        "quantity": random.randint(1, 10),
        "timestamp": datetime.now().strftime(random.choice(["%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m-%d-%Y %H:%M"]))
    }
    return row

batch = 1
while True:
    rows = [make_row() for _ in range(random.randint(5, 15))]

    if random.random() > 0.5 and len(rows) > 2:
        rows.append(rows[random.randint(0, len(rows)-1)])

    fmt = random.choice(["csv", "json", "txt"])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_{ts}_batch{batch}.{fmt}"
    filepath = os.path.join(output_dir, filename)

    if fmt == "csv":
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["name","age","city","product","price","quantity","timestamp"])
            w.writeheader()
            w.writerows(rows)
    elif fmt == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(rows, f, default=str)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            for r in rows:
                f.write("|".join(str(v) for v in r.values()) + "\n")

    print(f"[{ts}] wrote {filepath} ({len(rows)} rows)")
    batch += 1
    time.sleep(random.randint(3, 7))
