# loader.py
# Just handles reading the two CSV files into Python lists/dicts.
# Nothing fancy here - no cleaning, no validation, just IO.

import csv
import os


def load_csv(path):
    # basic check first, no point trying to open something that isn't there
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find file: " + path)

    rows = []
    try:
        f = open(path, "r", newline="", encoding="utf-8")
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
        f.close()
    except Exception as e:
        raise Exception("Something went wrong reading " + path + " -> " + str(e))

    return rows


def load_orders(path):
    return load_csv(path)


def load_product_master(path):
    # we need this twice - once as plain rows, once as a dict so we can
    # look products up by id quickly while cleaning
    rows = load_csv(path)

    lookup = {}
    for r in rows:
        pid = r.get("product_id", "")
        if pid:
            pid = pid.strip().upper()
        if not pid:
            continue
        lookup[pid] = {
            "product_name": r.get("product_name", "").strip(),
            "category": r.get("category", "").strip(),
            "standard_price": r.get("standard_price", "").strip(),
        }

    return rows, lookup
