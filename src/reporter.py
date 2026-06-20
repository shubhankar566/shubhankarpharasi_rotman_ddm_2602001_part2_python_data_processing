# reporter.py
# Writes the three output files: cleaned csv, rejected csv, summary txt.

import csv

CLEANED_COLS = [
    "order_id", "customer_id", "customer_name", "city", "product_id",
    "product_name", "category", "quantity", "unit_price", "total_amount",
    "order_status", "payment_method", "order_date",
]


def write_cleaned_orders(rows, path):
    f = open(path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=CLEANED_COLS)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    f.close()


def write_rejected_records(rows, path):
    if len(rows) == 0:
        fields = [
            "order_id", "customer_id", "customer_name", "city", "product_id",
            "quantity", "unit_price", "order_status", "payment_method",
            "order_date", "rejection_reason",
        ]
    else:
        fields = list(rows[0].keys())

    f = open(path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    f.close()


def write_summary_report(path, stats):
    lines = []
    lines.append("=" * 60)
    lines.append("BUSINESS SUMMARY REPORT - ORDER DATA PIPELINE")
    lines.append("=" * 60)
    lines.append("")

    lines.append("1. RECORD COUNTS")
    lines.append("-" * 60)
    lines.append("Total raw records      : " + str(stats["total_raw"]))
    lines.append("Total cleaned records  : " + str(stats["total_cleaned"]))
    lines.append("Total rejected records : " + str(stats["total_rejected"]))
    lines.append("")

    lines.append("2. TOTAL REVENUE (COMPLETED ORDERS)")
    lines.append("-" * 60)
    lines.append(f"₹{stats['total_revenue']:,.2f}")
    lines.append("")

    lines.append("3. REVENUE BY CATEGORY (COMPLETED ORDERS)")
    lines.append("-" * 60)
    for cat, rev in stats["revenue_by_category"].items():
        lines.append(f"{cat:<20} ₹{rev:,.2f}")
    lines.append("")

    lines.append("4. REVENUE BY CITY (COMPLETED ORDERS)")
    lines.append("-" * 60)
    for city, rev in stats["revenue_by_city"].items():
        lines.append(f"{city:<20} ₹{rev:,.2f}")
    lines.append("")

    lines.append("5. ORDERS BY PAYMENT METHOD")
    lines.append("-" * 60)
    for method, count in stats["orders_by_payment"].items():
        lines.append(f"{method:<20} {count} orders")
    lines.append("")

    lines.append("6. TOP 3 CUSTOMERS BY TOTAL SPEND")
    lines.append("-" * 60)
    rank = 1
    for name, spend in stats["top_customers"]:
        lines.append(f"{rank}. {name:<25} ₹{spend:,.2f}")
        rank += 1
    lines.append("")

    lines.append("7. PRODUCT WITH HIGHEST QUANTITY SOLD")
    lines.append("-" * 60)
    product, qty = stats["top_product"]
    lines.append(f"{product} ({qty} units sold)")
    lines.append("")

    lines.append("8. CATEGORY WITH HIGHEST REVENUE")
    lines.append("-" * 60)
    cat2, rev2 = stats["top_category"]
    lines.append(f"{cat2} (₹{rev2:,.2f})")
    lines.append("")

    lines.append("9. REJECTED RECORDS BY REASON")
    lines.append("-" * 60)
    for reason, count in stats["rejection_counts"].items():
        lines.append(f"{reason:<25} {count}")
    lines.append("")

    lines.append("10. KEY BUSINESS INSIGHTS")
    lines.append("-" * 60)
    i = 1
    for note in stats["insights"]:
        lines.append(f"{i}. {note}")
        i += 1
    lines.append("")

    lines.append("=" * 60)
    lines.append("END OF REPORT")
    lines.append("=" * 60)

    f = open(path, "w", encoding="utf-8")
    f.write("\n".join(lines))
    f.close()
