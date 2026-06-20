"""
analyzer.py
-----------
Performs business analysis on the cleaned order records and the
rejected records. Each function returns plain Python data structures
(dicts / lists) that reporter.py turns into the final text report.
"""


def total_revenue_completed(cleaned_records):
    """Total revenue from orders with status 'Completed'."""
    total = 0.0
    for row in cleaned_records:
        if row["order_status"] == "Completed":
            total += row["total_amount"]
    return round(total, 2)


def revenue_by_category(cleaned_records):
    """Returns a dict of category -> total revenue (completed orders only)."""
    revenue = {}
    for row in cleaned_records:
        if row["order_status"] == "Completed":
            category = row["category"]
            revenue[category] = round(revenue.get(category, 0) + row["total_amount"], 2)
    return dict(sorted(revenue.items(), key=lambda item: item[1], reverse=True))


def revenue_by_city(cleaned_records):
    """Returns a dict of city -> total revenue (completed orders only)."""
    revenue = {}
    for row in cleaned_records:
        if row["order_status"] == "Completed":
            city = row["city"]
            revenue[city] = round(revenue.get(city, 0) + row["total_amount"], 2)
    return dict(sorted(revenue.items(), key=lambda item: item[1], reverse=True))


def orders_by_payment_method(cleaned_records):
    """Returns a dict of payment_method -> number of orders."""
    counts = {}
    for row in cleaned_records:
        method = row["payment_method"]
        counts[method] = counts.get(method, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def top_customers_by_spend(cleaned_records, top_n=3):
    """Returns a list of (customer_name, total_spend) tuples, highest first."""
    spend = {}
    for row in cleaned_records:
        if row["order_status"] == "Completed":
            name = row["customer_name"]
            spend[name] = round(spend.get(name, 0) + row["total_amount"], 2)
    ranked = sorted(spend.items(), key=lambda item: item[1], reverse=True)
    return ranked[:top_n]


def product_highest_quantity_sold(cleaned_records):
    """Returns (product_name, total_quantity) for the best-selling product by quantity."""
    quantities = {}
    for row in cleaned_records:
        name = row["product_name"]
        quantities[name] = quantities.get(name, 0) + row["quantity"]
    if not quantities:
        return None, 0
    best = max(quantities.items(), key=lambda item: item[1])
    return best


def category_highest_revenue(cleaned_records):
    """Returns (category, revenue) for the category with the highest revenue."""
    by_cat = revenue_by_category(cleaned_records)
    if not by_cat:
        return None, 0
    top_category = next(iter(by_cat))
    return top_category, by_cat[top_category]


def rejection_reason_counts(rejected_records):
    """
    Returns a dict of rejection_reason -> count.
    Since a record can have multiple reasons joined by '; ', each
    individual reason is counted separately.
    """
    counts = {}
    for row in rejected_records:
        reasons = row.get("rejection_reason", "").split("; ")
        for reason in reasons:
            reason = reason.strip()
            if reason:
                counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def generate_insights(cleaned_records, rejected_records):
    """
    Builds a short list of plain-English business insights based on
    the computed statistics. Returns a list of strings.
    """
    insights = []

    total_orders = len(cleaned_records) + len(rejected_records)
    if total_orders > 0:
        reject_pct = round(len(rejected_records) / total_orders * 100, 1)
        insights.append(
            f"{reject_pct}% of all incoming orders failed data quality checks, "
            f"indicating a need for stricter validation at the point of order entry."
        )

    top_category, cat_revenue = category_highest_revenue(cleaned_records)
    if top_category:
        insights.append(
            f"The '{top_category}' category generates the highest revenue "
            f"(₹{cat_revenue:,.2f}) among completed orders, suggesting it should "
            f"be prioritized for inventory and marketing investment."
        )

    top_customers = top_customers_by_spend(cleaned_records)
    if top_customers:
        leader_name, leader_spend = top_customers[0]
        insights.append(
            f"'{leader_name}' is the top spending customer with ₹{leader_spend:,.2f} "
            f"in completed purchases, making them a strong candidate for a loyalty program."
        )

    by_payment = orders_by_payment_method(cleaned_records)
    if by_payment:
        leading_method = next(iter(by_payment))
        insights.append(
            f"'{leading_method}' is the most frequently used payment method, "
            f"so ensuring this payment channel is fast and reliable should be a priority."
        )

    return insights
