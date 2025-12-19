# Google Sheets Expense Automation (Version 1)

## Overview

This project is a **Python-based automation** that connects to a Google Sheets budget workbook and **tracks expenses in a reliable, repeatable way**.

Version 1 focuses on one core goal:

> **Ensure every expense row in Google Sheets is uniquely identified and safely marked as processed.**

This mirrors real-world finance and operations automation patterns (ETL-style processing, idempotency, and system-managed fields).

---

## What This Project Does (Version 1)

* Connects to a Google Sheet using a **Google Service Account**
* Reads rows from the `Expenses` worksheet
* Identifies which rows have **not yet been processed**
* For each unprocessed row, the script:

  * Generates a unique `expense_id`
  * Marks the row as `processed = TRUE`
  * Adds a `processed_at` timestamp (UTC)
  * Adds a system note for traceability
* Can be run **multiple times safely** without duplicating work

If the script is re-run with no new expenses, it will correctly report:

```
Processed 0 new expenses
```

---

## Google Sheets Structure

### Required Worksheet

The spreadsheet must contain a worksheet named:

```
Expenses
```

### Column Schema

| Column | Name             | Description                      |
| ------ | ---------------- | -------------------------------- |
| A      | `date`           | Expense date (manual entry)      |
| B      | `description`    | Description of the expense       |
| C      | `amount`         | Expense amount                   |
| D      | `category`       | Category (Food, Rent, etc.)      |
| E      | `payment_method` | Card, Cash, Bank, etc.           |
| F      | `expense_id`     | **System-managed** unique ID     |
| G      | `processed`      | **System-managed** TRUE/FALSE    |
| H      | `processed_at`   | **System-managed** UTC timestamp |
| I      | `script_notes`   | **System-managed** notes         |

Users should only manually edit columns **A–E**.

---

## Project Structure

```
google-sheets/01_basic/
│
├── main.py              # Orchestrates the automation
├── sheets_client.py     # Google Sheets authentication + access
├── expense_tracker.py   # Expense processing logic
├── utils.py             # Helpers (UUIDs, timestamps)
├── requirements.txt     # Python dependencies
├── service_account.json # Google service account key (gitignored)
├── .gitignore
└── README.md
```

---

## How the Automation Works

### High-Level Flow

1. Authenticate to Google Sheets using a service account
2. Load all rows from the `Expenses` worksheet
3. For each row:

   * Skip it if it has already been processed
   * Otherwise, prepare updates
4. Write updates back to Google Sheets
5. Print a summary of how many rows were processed

---

## Idempotency (Why This Is Safe to Re-Run)

This automation is **idempotent**:

* A row with an existing `expense_id` and `processed = TRUE` will be skipped
* Running the script multiple times will **not duplicate IDs or overwrite data**

This is a critical pattern in real automation and data pipelines.

---

## Authentication

* Uses a **Google Cloud service account**
* Authentication is handled via `service_account.json`
* The Google Sheet must be **shared with the service account email** (Editor access)

⚠️ **Security Note**

* `service_account.json` must never be committed to Git
* The file is included in `.gitignore`
* Keys should be rotated if exposed

---

## How to Run

1. Activate the virtual environment:

```bash
source .venv/bin/activate
```

2. Run the script:

```bash
python main.py
```

Expected output:

```
Processed X new expenses
```

---

## What Version 1 Does NOT Do (By Design)

* No validations (amounts, categories)
* No summaries or reports
* No monthly rollups
* No scheduling

These are intentionally deferred to later versions.

---

## Planned Next Versions (Future Work)

Potential extensions include:

* Batch updates for performance
* Data validation and error logging
* Monthly and category summaries
* Budget vs actual reporting
* Scheduled execution (cron / task scheduler)
* Reusable automation template

---

## Status

✅ **Version 1 Complete**

This project now serves as a solid foundation for real-world Google Sheets automation using Python.
