"""
loader.py
----------
Responsible for reading the raw CSV files from disk and converting
them into Python lists of dictionaries. No cleaning or validation
happens here - this module only deals with reading data.
"""

import csv
import os


def load_csv(file_path):
    """
    Reads a CSV file and returns its contents as a list of dictionaries.
    Each dictionary represents one row, keyed by the column headers.

    Raises FileNotFoundError if the file does not exist, and a
    generic Exception for any other read error.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Required data file not found: {file_path}")

    records = []
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except Exception as error:
        raise Exception(f"Error while reading {file_path}: {error}")

    return records


def load_orders(file_path):
    """Loads the raw orders CSV file."""
    return load_csv(file_path)


def load_product_master(file_path):
    """
    Loads the product master CSV file and also returns it as a
    dictionary keyed by product_id for fast lookups during cleaning.
    """
    records = load_csv(file_path)
    product_lookup = {}
    for row in records:
        pid = (row.get("product_id") or "").strip().upper()
        if pid:
            product_lookup[pid] = {
                "product_name": row.get("product_name", "").strip(),
                "category": row.get("category", "").strip(),
                "standard_price": row.get("standard_price", "").strip(),
            }
    return records, product_lookup
