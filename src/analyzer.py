# analyzer.py
# All the number-crunching for the summary report happens here.
# Functions just take the cleaned/rejected lists and return plain dicts/lists.

def total_revenue_completed(orders):
    total = 0.0
    for o in orders:
        if o["order_status"] == "Completed":
            total += o["total_amount"]
    return round(total, 2)


def revenue_by_category(orders):
    out = {}
    for o in orders:
        if o["order_status"] != "Completed":
            continue
        cat = o["category"]
        out[cat] = out.get(cat, 0) + o["total_amount"]
    for k in out:
        out[k] = round(out[k], 2)
    # biggest revenue first
    return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))


def revenue_by_city(orders):
    out = {}
    for o in orders:
        if o["order_status"] != "Completed":
            continue
        city = o["city"]
        out[city] = out.get(city, 0) + o["total_amount"]
    for k in out:
        out[k] = round(out[k], 2)
    return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))


def orders_by_payment_method(orders):
    counts = {}
    for o in orders:
        m = o["payment_method"]
        counts[m] = counts.get(m, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def top_customers_by_spend(orders, n=3):
    spend = {}
    for o in orders:
        if o["order_status"] != "Completed":
            continue
        name = o["customer_name"]
        spend[name] = spend.get(name, 0) + o["total_amount"]
    for k in spend:
        spend[k] = round(spend[k], 2)
    ranked = sorted(spend.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n]


def product_highest_quantity_sold(orders):
    qty_map = {}
    for o in orders:
        name = o["product_name"]
        qty_map[name] = qty_map.get(name, 0) + o["quantity"]
    if len(qty_map) == 0:
        return None, 0
    # find the product with max units sold
    best_name = None
    best_qty = -1
    for name, qty in qty_map.items():
        if qty > best_qty:
            best_qty = qty
            best_name = name
    return best_name, best_qty


def category_highest_revenue(orders):
    by_cat = revenue_by_category(orders)
    if len(by_cat) == 0:
        return None, 0
    top = list(by_cat.keys())[0]
    return top, by_cat[top]


def rejection_reason_counts(rejected):
    counts = {}
    for row in rejected:
        reason_str = row.get("rejection_reason", "")
        for reason in reason_str.split("; "):
            reason = reason.strip()
            if reason:
                counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def generate_insights(cleaned, rejected):
    notes = []

    total = len(cleaned) + len(rejected)
    if total > 0:
        pct = round(len(rejected) / total * 100, 1)
        notes.append(
            f"{pct}% of incoming orders failed data quality checks, which means "
            f"order entry probably needs tighter validation before data even "
            f"reaches this pipeline."
        )

    cat, cat_rev = category_highest_revenue(cleaned)
    if cat:
        notes.append(
            f"'{cat}' brings in the most revenue among completed orders "
            f"(₹{cat_rev:,.2f}), so it's probably worth pushing more stock "
            f"and marketing budget toward this category."
        )

    top_cust = top_customers_by_spend(cleaned)
    if top_cust:
        top_name, top_spend = top_cust[0]
        notes.append(
            f"'{top_name}' is the single biggest spender at ₹{top_spend:,.2f} "
            f"in completed orders - a good candidate for some kind of loyalty perk."
        )

    pay = orders_by_payment_method(cleaned)
    if pay:
        top_method = list(pay.keys())[0]
        notes.append(
            f"Most customers pay using '{top_method}', so keeping that payment "
            f"option fast and reliable matters more than the others."
        )

    return notes
