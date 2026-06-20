"""
cleaner.py
----------
Contains all data cleaning and validation rules for the order
records. Produces two lists: cleaned (valid) records and rejected
records (each tagged with one or more rejection reasons).
"""

import datetime

VALID_STATUSES = {"Completed", "Pending", "Cancelled"}
VALID_PAYMENT_METHODS = {"Credit Card", "Debit Card", "UPI", "Cash on Delivery"}

CITY_STANDARDIZATION = {
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

DATE_INPUT_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]


def standardize_text(value):
    """Trims extra spaces and collapses internal multiple spaces."""
    if value is None:
        return ""
    return " ".join(value.strip().split())


def standardize_name(value):
    """Trims spaces and converts a name to Title Case."""
    cleaned = standardize_text(value)
    return cleaned.title()


def standardize_city(value):
    """Trims spaces and maps known city spelling variants to one form."""
    cleaned = standardize_text(value)
    if not cleaned:
        return ""
    key = cleaned.lower()
    return CITY_STANDARDIZATION.get(key, cleaned.title())


def standardize_status(value):
    """Trims spaces and converts order status casing to Title Case."""
    cleaned = standardize_text(value)
    return cleaned.title()


PAYMENT_METHOD_MAP = {
    "credit card": "Credit Card",
    "debit card": "Debit Card",
    "upi": "UPI",
    "cash on delivery": "Cash on Delivery",
}


def standardize_payment(value):
    """Trims spaces and normalizes payment method casing using a lookup map."""
    cleaned = standardize_text(value)
    if not cleaned:
        return ""
    key = cleaned.lower()
    return PAYMENT_METHOD_MAP.get(key, cleaned.title())


def parse_date(value):
    """
    Tries to parse a date string using the accepted formats.
    Returns the date in YYYY-MM-DD format if valid, otherwise None.
    """
    cleaned = standardize_text(value)
    for fmt in DATE_INPUT_FORMATS:
        try:
            parsed = datetime.datetime.strptime(cleaned, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def is_number(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def clean_orders(raw_orders, product_lookup):
    """
    Applies cleaning and validation rules to every raw order record.

    Returns a tuple: (cleaned_records, rejected_records)
    cleaned_records  -> list of dicts ready for the cleaned_orders.csv output
    rejected_records -> list of dicts with a 'rejection_reason' field
    """
    cleaned_records = []
    rejected_records = []
    seen_order_ids = set()

    for row in raw_orders:
        reasons = []

        order_id = standardize_text(row.get("order_id"))
        customer_id = standardize_text(row.get("customer_id"))
        customer_name = standardize_name(row.get("customer_name"))
        city = standardize_city(row.get("city"))
        product_id = standardize_text(row.get("product_id")).upper()
        status = standardize_status(row.get("order_status"))
        payment_method = standardize_payment(row.get("payment_method"))
        raw_quantity = row.get("quantity")
        raw_price = row.get("unit_price")
        raw_date = row.get("order_date")

        # Rule: duplicate order ID
        if not order_id:
            reasons.append("Missing order ID")
        elif order_id in seen_order_ids:
            reasons.append("Duplicate order ID")

        # Rule: missing customer name
        if not customer_name:
            reasons.append("Missing customer name")

        # Rule: missing city
        if not city:
            reasons.append("Missing city")

        # Rule: product ID must exist in product master
        product_info = product_lookup.get(product_id)
        if not product_info:
            reasons.append("Product ID not found")

        # Rule: quantity must be a positive whole number
        quantity_valid = False
        quantity = None
        if is_number(raw_quantity):
            quantity = int(float(raw_quantity))
            if quantity > 0:
                quantity_valid = True
        if not quantity_valid:
            reasons.append("Invalid quantity")

        # Rule: unit price must match the product master standard price
        price_valid = False
        unit_price = None
        if is_number(raw_price):
            unit_price = float(raw_price)
            if product_info:
                standard_price = float(product_info["standard_price"])
                if abs(unit_price - standard_price) < 0.01:
                    price_valid = True
            if not price_valid:
                reasons.append("Unit price mismatch")
        else:
            reasons.append("Unit price mismatch")

        # Rule: order status must be one of the allowed values
        if status not in VALID_STATUSES:
            reasons.append("Invalid order status")

        # Rule: payment method must be one of the allowed values
        if payment_method not in VALID_PAYMENT_METHODS:
            reasons.append("Invalid payment method")

        # Rule: date must be parseable
        parsed_date = parse_date(raw_date)
        if not parsed_date:
            reasons.append("Invalid date format")

        if reasons:
            rejected_row = dict(row)
            rejected_row["rejection_reason"] = "; ".join(reasons)
            rejected_records.append(rejected_row)
            # Still mark the order id as seen so a later duplicate of an
            # already-rejected id is also flagged correctly.
            if order_id:
                seen_order_ids.add(order_id)
            continue

        # If we reach here, the record is fully valid
        seen_order_ids.add(order_id)
        total_amount = round(quantity * unit_price, 2)

        cleaned_records.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "city": city,
            "product_id": product_id,
            "product_name": product_info["product_name"],
            "category": product_info["category"],
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "order_status": status,
            "payment_method": payment_method,
            "order_date": parsed_date,
        })

    return cleaned_records, rejected_records
