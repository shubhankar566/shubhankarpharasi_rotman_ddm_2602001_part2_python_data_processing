# cleaner.py
# This is where most of the actual logic lives - cleaning text fields,
# checking each rule, and splitting orders into "good" and "rejected" piles.

import datetime

ALLOWED_STATUS = ["Completed", "Pending", "Cancelled"]
ALLOWED_PAYMENT = ["Credit Card", "Debit Card", "UPI", "Cash on Delivery"]

# some cities show up with weird spelling in the raw file, fixing those here
CITY_FIXES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "delhi": "Delhi",
    "kolkata": "Kolkata",
    "chennai": "Chennai",
    "pune": "Pune",
    "jaipur": "Jaipur",
    "hyderabad": "Hyderabad",
}

PAYMENT_FIXES = {
    "credit card": "Credit Card",
    "debit card": "Debit Card",
    "upi": "UPI",
    "cash on delivery": "Cash on Delivery",
}

DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]


def clean_text(value):
    # trims spaces front/back and squashes double spaces in the middle
    if not value:
        return ""
    return " ".join(value.strip().split())


def fix_name(value):
    txt = clean_text(value)
    return txt.title()


def fix_city(value):
    txt = clean_text(value)
    if txt == "":
        return ""
    lower = txt.lower()
    if lower in CITY_FIXES:
        return CITY_FIXES[lower]
    return txt.title()


def fix_status(value):
    return clean_text(value).title()


def fix_payment(value):
    txt = clean_text(value)
    if txt == "":
        return ""
    lower = txt.lower()
    if lower in PAYMENT_FIXES:
        return PAYMENT_FIXES[lower]
    return txt.title()


def try_parse_date(value):
    txt = clean_text(value)
    for fmt in DATE_FORMATS:
        try:
            d = datetime.datetime.strptime(txt, fmt)
            return d.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def looks_numeric(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def clean_orders(raw_rows, product_lookup):
    good = []
    bad = []
    used_ids = set()

    for row in raw_rows:
        problems = []

        oid = clean_text(row.get("order_id"))
        cust_id = clean_text(row.get("customer_id"))
        name = fix_name(row.get("customer_name"))
        city = fix_city(row.get("city"))
        pid = clean_text(row.get("product_id")).upper()
        status = fix_status(row.get("order_status"))
        payment = fix_payment(row.get("payment_method"))
        qty_raw = row.get("quantity")
        price_raw = row.get("unit_price")
        date_raw = row.get("order_date")

        if oid == "":
            problems.append("Missing order ID")
        elif oid in used_ids:
            problems.append("Duplicate order ID")

        if name == "":
            problems.append("Missing customer name")

        if city == "":
            problems.append("Missing city")

        product = product_lookup.get(pid)
        if product is None:
            problems.append("Product ID not found")

        # quantity check - has to be a whole number above zero
        qty_ok = False
        qty = None
        if looks_numeric(qty_raw):
            qty = int(float(qty_raw))
            if qty > 0:
                qty_ok = True
        if not qty_ok:
            problems.append("Invalid quantity")

        # price check against the product master
        price_ok = False
        price = None
        if looks_numeric(price_raw):
            price = float(price_raw)
            if product is not None:
                std_price = float(product["standard_price"])
                if abs(price - std_price) < 0.01:
                    price_ok = True
            if not price_ok:
                problems.append("Unit price mismatch")
        else:
            problems.append("Unit price mismatch")

        if status not in ALLOWED_STATUS:
            problems.append("Invalid order status")

        if payment not in ALLOWED_PAYMENT:
            problems.append("Invalid payment method")

        good_date = try_parse_date(date_raw)
        if good_date is None:
            problems.append("Invalid date format")

        if len(problems) > 0:
            rejected_row = dict(row)
            rejected_row["rejection_reason"] = "; ".join(problems)
            bad.append(rejected_row)
            if oid != "":
                used_ids.add(oid)
            continue

        used_ids.add(oid)
        total = round(qty * price, 2)

        good.append({
            "order_id": oid,
            "customer_id": cust_id,
            "customer_name": name,
            "city": city,
            "product_id": pid,
            "product_name": product["product_name"],
            "category": product["category"],
            "quantity": qty,
            "unit_price": price,
            "total_amount": total,
            "order_status": status,
            "payment_method": payment,
            "order_date": good_date,
        })

    return good, bad
