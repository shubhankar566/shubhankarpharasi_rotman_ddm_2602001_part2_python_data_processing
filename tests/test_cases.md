# Test Cases — Order Data Processing Pipeline

These are manual / logical test cases describing how the pipeline should
behave for specific input conditions. Each test case lists the input
condition, the expected output, and the reason behind it.

---

### TC01 — Valid record
- **Input condition:** A row with a unique `order_id`, non-empty
  `customer_name` and `city`, a valid `product_id`, `quantity > 0`,
  `unit_price` equal to the product master's `standard_price`, a valid
  `order_status`, a valid `payment_method`, and a parseable `order_date`.
- **Expected output:** Record appears in `cleaned_orders.csv` with
  `total_amount = quantity * unit_price` and enriched `product_name`/`category`.
- **Reason:** This row satisfies every cleaning and validation rule, so it
  must be accepted, not rejected.

---

### TC02 — Duplicate order ID
- **Input condition:** Two rows share the same `order_id` (e.g. `O1003`
  appears twice in `raw_orders.csv`).
- **Expected output:** The first occurrence is processed normally (accepted
  if otherwise valid). The second occurrence appears in
  `rejected_records.csv` with reason `Duplicate order ID`.
- **Reason:** Order IDs must be unique; only the first occurrence is trusted.

---

### TC03 — Missing customer name
- **Input condition:** `customer_name` is empty or blank (e.g. row `O1004`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Missing customer name`.
- **Reason:** A customer name is mandatory for any valid order record.

---

### TC04 — Missing city
- **Input condition:** `city` is empty or blank (e.g. row `O1008`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Missing city`.
- **Reason:** City is required for the revenue-by-city analysis to be accurate.

---

### TC05 — Invalid quantity (zero)
- **Input condition:** `quantity = 0` (e.g. row `O1011`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Invalid quantity`.
- **Reason:** An order cannot be placed for zero units; this indicates bad data.

---

### TC06 — Invalid quantity (negative)
- **Input condition:** `quantity` is negative (e.g. row `O1015`, `quantity = -3`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Invalid quantity`.
- **Reason:** Negative quantities are not physically meaningful for an order.

---

### TC07 — Invalid product ID
- **Input condition:** `product_id` does not exist in `product_master.csv`
  (e.g. `P999`, `PXYZ`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Product ID not found`.
- **Reason:** Every product sold must be traceable to the product catalogue.

---

### TC08 — Invalid payment method
- **Input condition:** `payment_method` is not one of `Credit Card`,
  `Debit Card`, `UPI`, `Cash on Delivery` (e.g. `Cheque`, `Crypto`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Invalid payment method`.
- **Reason:** Only the four supported payment channels are accepted by the business.

---

### TC09 — Invalid order status
- **Input condition:** `order_status` is not one of `Completed`, `Pending`,
  `Cancelled` (e.g. `Shipped`, `InProgress`).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Invalid order status`.
- **Reason:** The reporting logic only understands these three statuses.

---

### TC10 — Unit price mismatch
- **Input condition:** `unit_price` does not equal the product master's
  `standard_price` for that `product_id` (e.g. row `O1017`, sold at ₹999
  but standard price is ₹499).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Unit price mismatch`.
- **Reason:** Prices must match the catalogue to ensure accurate revenue figures.

---

### TC11 — Invalid date format
- **Input condition:** `order_date` cannot be parsed by any accepted format
  (e.g. `31-15-2025` which has an invalid month, or `March 5 2025` which is
  in an unsupported text format).
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Invalid date format`.
- **Reason:** A clean, consistent date is required for any time-based reporting.

---

### TC12 — Revenue calculation
- **Input condition:** A valid `Completed` order with `quantity = 2` and
  `unit_price = 1899.0`.
- **Expected output:** `total_amount = 3798.0` in `cleaned_orders.csv`, and
  this amount is included in `total_revenue_completed()` and in the
  category/city revenue breakdowns.
- **Reason:** `total_amount` must always be recalculated as
  `quantity × unit_price`, never copied blindly from raw input.

---

### TC13 — Rejection reason generation (multiple issues)
- **Input condition:** A row that is missing `customer_name` **and** has an
  invalid `payment_method` at the same time.
- **Expected output:** Record appears in `rejected_records.csv` with reason
  `Missing customer name; Invalid payment method` (both reasons listed,
  separated by `; `).
- **Reason:** When multiple rules are violated, all of them must be reported
  so the business can fully understand why a record failed.

---

### TC14 — Inconsistent city spelling is standardized, not rejected
- **Input condition:** `city = "bombay"` or `city = "Bangalore"` on an
  otherwise valid row.
- **Expected output:** Record is accepted into `cleaned_orders.csv` with
  `city` standardized to `Mumbai` or `Bengaluru` respectively.
- **Reason:** Spelling variants are a cleaning problem, not a rejection
  reason — they should be normalized rather than discarded.

---

### TC15 — Extra spaces and casing are cleaned, not rejected
- **Input condition:** `customer_name = "  Arjun Nair  "` or
  `order_status = "completed"` on an otherwise valid row.
- **Expected output:** Record is accepted with `customer_name = "Arjun Nair"`
  and `order_status = "Completed"`.
- **Reason:** Whitespace and casing issues should be normalized by the
  cleaning functions before validation runs, not treated as fatal errors.
