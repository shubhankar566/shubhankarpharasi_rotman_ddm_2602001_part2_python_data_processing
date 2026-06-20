"""
reporter.py
-----------
Handles writing all output files: cleaned_orders.csv,
rejected_records.csv, and summary_report.txt.
"""

import csv

CLEANED_COLUMNS = [
    "order_id", "customer_id", "customer_name", "city", "product_id",
    "product_name", "category", "quantity", "unit_price", "total_amount",
    "order_status", "payment_method", "order_date",
]


def write_cleaned_orders(cleaned_records, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CLEANED_COLUMNS)
        writer.writeheader()
        for row in cleaned_records:
            writer.writerow(row)


def write_rejected_records(rejected_records, file_path):
    if not rejected_records:
        fieldnames = [
            "order_id", "customer_id", "customer_name", "city", "product_id",
            "quantity", "unit_price", "order_status", "payment_method",
            "order_date", "rejection_reason",
        ]
    else:
        # Preserve original column order plus rejection_reason at the end
        fieldnames = [k for k in rejected_records[0].keys()]

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rejected_records:
            writer.writerow(row)


def write_summary_report(file_path, stats):
    """
    stats is a dictionary containing all the precomputed values needed
    for the report (see main.py for the keys it must contain).
    """
    lines = []
    lines.append("=" * 60)
    lines.append("BUSINESS SUMMARY REPORT - ORDER DATA PIPELINE")
    lines.append("=" * 60)
    lines.append("")

    lines.append("1. RECORD COUNTS")
    lines.append("-" * 60)
    lines.append(f"Total raw records      : {stats['total_raw']}")
    lines.append(f"Total cleaned records  : {stats['total_cleaned']}")
    lines.append(f"Total rejected records : {stats['total_rejected']}")
    lines.append("")

    lines.append("2. TOTAL REVENUE (COMPLETED ORDERS)")
    lines.append("-" * 60)
    lines.append(f"₹{stats['total_revenue']:,.2f}")
    lines.append("")

    lines.append("3. REVENUE BY CATEGORY (COMPLETED ORDERS)")
    lines.append("-" * 60)
    for category, revenue in stats["revenue_by_category"].items():
        lines.append(f"{category:<20} ₹{revenue:,.2f}")
    lines.append("")

    lines.append("4. REVENUE BY CITY (COMPLETED ORDERS)")
    lines.append("-" * 60)
    for city, revenue in stats["revenue_by_city"].items():
        lines.append(f"{city:<20} ₹{revenue:,.2f}")
    lines.append("")

    lines.append("5. ORDERS BY PAYMENT METHOD")
    lines.append("-" * 60)
    for method, count in stats["orders_by_payment"].items():
        lines.append(f"{method:<20} {count} orders")
    lines.append("")

    lines.append("6. TOP 3 CUSTOMERS BY TOTAL SPEND")
    lines.append("-" * 60)
    for rank, (name, spend) in enumerate(stats["top_customers"], start=1):
        lines.append(f"{rank}. {name:<25} ₹{spend:,.2f}")
    lines.append("")

    lines.append("7. PRODUCT WITH HIGHEST QUANTITY SOLD")
    lines.append("-" * 60)
    product, qty = stats["top_product"]
    lines.append(f"{product} ({qty} units sold)")
    lines.append("")

    lines.append("8. CATEGORY WITH HIGHEST REVENUE")
    lines.append("-" * 60)
    category, revenue = stats["top_category"]
    lines.append(f"{category} (₹{revenue:,.2f})")
    lines.append("")

    lines.append("9. REJECTED RECORDS BY REASON")
    lines.append("-" * 60)
    for reason, count in stats["rejection_counts"].items():
        lines.append(f"{reason:<25} {count}")
    lines.append("")

    lines.append("10. KEY BUSINESS INSIGHTS")
    lines.append("-" * 60)
    for idx, insight in enumerate(stats["insights"], start=1):
        lines.append(f"{idx}. {insight}")
    lines.append("")

    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
