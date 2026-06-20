# Order Data Processing Pipeline — Part 2 (Python)

**Assignment:** Part 2 — Python Data Processing
**Student Name:** Shubhankar Pharasi
**Student ID:** Rotman_ddm_2602001

---

## 1. Project Overview

This project is a data-processing pipeline that:

1. Reads e-commerce file.
2. Cleans and standardizes the data.
3. Validates every record.
4. Splits records into **cleaned (valid)** and **rejected (invalid)** sets.
5. Recalculates `total_amount` for every valid order.
6. Generates a business summary report with revenue breakdowns, top customers,
   top products, and plain-English insights.

Only Python's standard library is used: **No pandas.**

---

## 2. Dataset Description

### `data/raw_orders.csv` (60 rows)
Simulated e-commerce orders with columns:
`order_id, customer_id, customer_name, city, product_id, quantity, unit_price, order_status, payment_method, order_date`

### `data/product_master.csv` (10 products)
Reference catalogue with columns:
`product_id, product_name, category, standard_price`

Categories covered: Electronics, Furniture, Stationery, Footwear, Apparel.

---

## 3. Intentionally Added Data Quality Issues

The raw dataset deliberately contains the following issues (12+ categories, as required):

| # | Issue Type | Example in dataset |
|---|------------|---------------------|
| 1 | Duplicate order IDs | `O1003` appears twice; `O1016` appears twice |
| 2 | Missing customer names | `O1004`, `O1034` have a blank `customer_name` |
| 3 | Missing city values | `O1008`, `O1041` have a blank `city` |
| 4 | Inconsistent city spellings | `Bangalore` / `Bengaluru`, `bombay` / `Mumbai`, `delhi` / `Delhi` |
| 5 | Extra spaces | `"  Arjun Nair  "` (O1005), `"Kolkata "` (O1012), `" Chennai"` (O1059) |
| 6 | Incorrect casing | `RITU AGARWAL`, `completed`, `upi`, `ravi kumar` (O1033) |
| 7 | Quantity = 0 | `O1011` has `quantity = 0` |
| 8 | Negative quantity | `O1015` has `quantity = -3` |
| 9 | Unit price mismatch with product master | `O1017` (₹999 vs standard ₹499), `O1028` (₹1 vs standard ₹5499) |
| 10 | Invalid order status | `InProgress` (O1037), `Shipped` (O1020) |
| 11 | Invalid payment method | `Cheque` (O1024), `Crypto` (O1039) |
| 12 | Invalid date format | `31-15-2025` (O1043 — invalid day/month), `March 5 2025` (O1051) |
| 13 | Invalid / unknown product ID | `P999` (O1045), `PXYZ` (O1056) |

---

## 4. Cleaning Rules Applied (`src/cleaner.py`)

- **Trim extra spaces** from every text field and collapse repeated internal spaces.
- **Standardize customer names** to Title Case.
- **Standardize city names**: trimmed, Title Cased, and known spelling variants
  (`Bangalore`→`Bengaluru`, `bombay`→`Mumbai`, `delhi`→`Delhi`) mapped to one canonical form.
- **Standardize order status** to Title Case (e.g. `completed` → `Completed`).
- **Standardize payment method** using a lookup map so values like
  `cash on delivery` correctly become `Cash on Delivery` (not `Cash On Delivery`).
- **Remove duplicate order IDs** — only the first occurrence of an order ID is
  considered; later duplicates are rejected.
- **Validate product IDs** against `product_master.csv`.
- **Validate quantity** — must be a positive whole number.
- **Validate order date** — accepted formats: `YYYY-MM-DD`, `DD-MM-YYYY`, `DD/MM/YYYY`.
- **Validate unit price** against the product master's `standard_price`.
- **Recalculate `total_amount`** as `quantity × unit_price` for every valid record
  (the raw unit price is never trusted blindly).

---

## 5. Rejection Rules Applied (`src/cleaner.py`)

A record is rejected (sent to `outputs/rejected_records.csv`) if **any** of the
following are true. If a row fails multiple checks, **all** applicable reasons
are recorded, separated by `; `.

- Missing or duplicate `order_id`
- Missing `customer_name`
- Missing `city`
- `product_id` not found in the product master
- Invalid `quantity` (zero, negative, or non-numeric)
- `unit_price` does not match the product master's `standard_price`
- `order_status` not in `{Completed, Pending, Cancelled}`
- `payment_method` not in `{Credit Card, Debit Card, UPI, Cash on Delivery}`
- `order_date` cannot be parsed in any accepted format

Rejected records are **never deleted** — they are written to a CSV file with an
extra `rejection_reason` column.

---

## 6. Folder Structure

```
shubhankarpharasi_rotman_ddm_2602001_part2_python_data_processing/
│
├── README.md
├── main.py
├── src/
│   ├── __init__.py
│   ├── loader.py
│   ├── cleaner.py
│   ├── analyzer.py
│   └── reporter.py
├── data/
│   ├── raw_orders.csv
│   └── product_master.csv
├── outputs/
│   ├── cleaned_orders.csv
│   ├── rejected_records.csv
│   ├── summary_report.txt
│   └── screenshots/
└── tests/
    └── test_cases.md
```

---

## 7. How to Run the Project

**Requirements:** Python 3.8+ (standard library only, no installs needed).

```bash
# 1. Clone the repository
git clone https://github.com/shubhankar566/shubhankarpharasi_rotman_ddm_2602001_part2_python_data_processing.git
cd shubhankarpharasi_rotman_ddm_2602001_part2_python_data_processing

# 2. Run the pipeline
python3 main.py
```

The script prints progress to the console and writes all output files into
the `outputs/` folder.

---

## 8. Explanation of Generated Output Files

| File | Description |
|------|--------------|
| `outputs/cleaned_orders.csv` | All valid, cleaned order records with recalculated `total_amount`, enriched with `product_name` and `category` from the product master. |
| `outputs/rejected_records.csv` | All invalid records in their original raw form, plus a `rejection_reason` column listing every rule that was violated. |
| `outputs/summary_report.txt` | Human-readable business report: record counts, revenue by category/city, payment method breakdown, top 3 customers, best-selling product, highest-revenue category, rejection-reason counts, and plain-English insights. |

### Sample results from this run
- Total raw records: **60** | Cleaned: **42** | Rejected: **18**
- Total revenue (completed orders): **₹70,923.00**
- Highest-revenue category: **Furniture (₹30,699.00)**
- Top customer by spend: **Shalini Rao (₹15,995.00)**

(See `outputs/summary_report.txt` for the full report — numbers will match
whatever is in `data/raw_orders.csv` at the time the pipeline is run.)

---

## 9. Key Business Insights

1. Roughly 30% of all incoming orders failed data quality checks, mostly due to
   invalid dates, price mismatches, and bad product IDs — pointing to a need for
   stricter validation at the point of order entry.
2. The **Furniture** category drives the highest revenue among completed orders,
   so it is the strongest candidate for additional inventory and marketing spend.
3. **Credit Card** is the most frequently used payment method, so reliability of
   that payment channel directly affects the largest share of orders.
4. A small group of repeat customers (e.g. Shalini Rao, Karan Malhotra) account
   for a disproportionate share of completed-order revenue, making them good
   targets for a loyalty or retention program.

---

## 10. Assumptions

- `order_status` is restricted to `Completed`, `Pending`, and `Cancelled`.
  Any other value (e.g. `Shipped`, `InProgress`) is treated as invalid for
  this assignment's scope.
- `payment_method` is restricted to `Credit Card`, `Debit Card`, `UPI`, and
  `Cash on Delivery`. Other methods (e.g. `Cheque`, `Crypto`) are rejected.
- Accepted date formats are `YYYY-MM-DD`, `DD-MM-YYYY`, and `DD/MM/YYYY`. Any
  other format (including malformed dates like `31-15-2025`) is rejected.
- `unit_price` must match the product master's `standard_price` exactly
  (within floating-point rounding tolerance); no discount logic is assumed.
- If an `order_id` repeats, only the **first** occurrence is evaluated normally;
  every later occurrence is automatically rejected as a duplicate.
- Revenue and customer-spend calculations only include orders with
  `order_status = Completed`.
  