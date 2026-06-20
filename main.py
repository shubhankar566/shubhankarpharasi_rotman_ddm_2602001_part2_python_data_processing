# main.py
# Entry point. Doesn't do any real logic itself - just calls into src/
# in order: load -> clean -> write outputs -> analyze -> write report.

import os
import sys

from src import loader
from src import cleaner
from src import analyzer
from src import reporter

RAW_ORDERS_PATH = os.path.join("data", "raw_orders.csv")
PRODUCT_MASTER_PATH = os.path.join("data", "product_master.csv")

CLEANED_OUTPUT_PATH = os.path.join("outputs", "cleaned_orders.csv")
REJECTED_OUTPUT_PATH = os.path.join("outputs", "rejected_records.csv")
SUMMARY_OUTPUT_PATH = os.path.join("outputs", "summary_report.txt")


def run_pipeline():
    print("Starting order data processing pipeline...")
    print("")

    try:
        raw_orders = loader.load_orders(RAW_ORDERS_PATH)
        _, product_lookup = loader.load_product_master(PRODUCT_MASTER_PATH)
        print("Loaded " + str(len(raw_orders)) + " raw order records.")
        print("Loaded " + str(len(product_lookup)) + " products into the product master.")
        print("")
    except Exception as e:
        print("ERROR while loading data: " + str(e))
        sys.exit(1)

    cleaned_records, rejected_records = cleaner.clean_orders(raw_orders, product_lookup)
    print("Cleaning complete: " + str(len(cleaned_records)) + " valid, " +
          str(len(rejected_records)) + " rejected.")
    print("")

    os.makedirs("outputs", exist_ok=True)
    try:
        reporter.write_cleaned_orders(cleaned_records, CLEANED_OUTPUT_PATH)
        reporter.write_rejected_records(rejected_records, REJECTED_OUTPUT_PATH)
        print("Wrote cleaned records to " + CLEANED_OUTPUT_PATH)
        print("Wrote rejected records to " + REJECTED_OUTPUT_PATH)
        print("")
    except Exception as e:
        print("ERROR while writing output files: " + str(e))
        sys.exit(1)

    stats = {
        "total_raw": len(raw_orders),
        "total_cleaned": len(cleaned_records),
        "total_rejected": len(rejected_records),
        "total_revenue": analyzer.total_revenue_completed(cleaned_records),
        "revenue_by_category": analyzer.revenue_by_category(cleaned_records),
        "revenue_by_city": analyzer.revenue_by_city(cleaned_records),
        "orders_by_payment": analyzer.orders_by_payment_method(cleaned_records),
        "top_customers": analyzer.top_customers_by_spend(cleaned_records),
        "top_product": analyzer.product_highest_quantity_sold(cleaned_records),
        "top_category": analyzer.category_highest_revenue(cleaned_records),
        "rejection_counts": analyzer.rejection_reason_counts(rejected_records),
        "insights": analyzer.generate_insights(cleaned_records, rejected_records),
    }

    try:
        reporter.write_summary_report(SUMMARY_OUTPUT_PATH, stats)
        print("Wrote business summary report to " + SUMMARY_OUTPUT_PATH)
        print("")
    except Exception as e:
        print("ERROR while writing summary report: " + str(e))
        sys.exit(1)

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    run_pipeline()
