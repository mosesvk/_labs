# Google Sheets Expense Automation (Version 2)

## Overview

This project is a **Python-based automation** that connects to a Google Sheets budget workbook and **tracks expenses with validation, duplicate detection, and batch processing**.

Version 2 builds on Version 1 by adding:

> **Data validation, duplicate checking, error handling, and efficient batch operations for adding new expenses.**

This version transforms the automation from a **read-only processor** (Version 1) into an **interactive expense entry system** with robust error handling and performance optimizations.

---
## What's New in Version 2?

### Key Upgrades from Version 1:

| Feature | Version 1 | Version 2 |
|---------|-----------|-----------|
| **Functionality** | Processes existing rows | **Adds new expenses interactively** |
| **Validation** | None | ✅ Validates required fields & numeric amounts |
| **Duplicate Detection** | None | ✅ Checks for duplicate expenses (date + description + amount) |
| **Error Handling** | None | ✅ Logs invalid expenses to "Errors" sheet |
| **API Efficiency** | Individual cell updates | ✅ **Batch operations** (1 API call vs N calls) |
| **User Interaction** | None | ✅ Interactive prompts for missing data |
| **Error Recovery** | None | ✅ Invalid expenses logged for review |

### What Version 2 Does:

* ✅ **Adds new expenses** interactively (single or batch mode)
* ✅ **Validates** that required fields (date, description, amount) are present
* ✅ **Validates** that amounts are numeric
* ✅ **Checks for duplicates** before adding (same date + description + amount)
* ✅ **Prompts user** for missing required fields
* ✅ **Logs errors** to a separate "Errors" worksheet for invalid expenses
* ✅ **Batches updates** for efficient API usage (reduces API calls significantly)
* ✅ **Interactive menu** for easy expense entry

---

## Google Sheets Structure

### Required Worksheets

The spreadsheet must contain:

1. **`Expenses`** worksheet (same as Version 1)
2. **`Errors`** worksheet (created automatically if missing)

### Column Schema (Same as Version 1)

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

### Errors Worksheet Schema

The `Errors` worksheet is automatically created with these columns:

| Column | Name             | Description                      |
| ------ | ---------------- | -------------------------------- |
| A      | `date`           | Invalid expense date             |
| B      | `description`    | Invalid expense description      |
| C      | `amount`         | Invalid expense amount           |
| D      | `category`       | Category (if provided)           |
| E      | `payment_method` | Payment method (if provided)       |
| F      | `error_message`    | **Why the expense is invalid**   |
| G      | `logged_at`      | **When the error was logged**    |

---

## Project Structure

```
google-sheets/02_validation-batching/
│
├── main.py              # Interactive menu & orchestration
├── sheets_client.py     # Google Sheets authentication + access
├── expense_tracker.py   # Validation, duplicate checking, batch operations
├── utils.py             # Helpers (UUIDs, timestamps)
├── requirements.txt     # Python dependencies
├── service_account.json # Google service account key (gitignored)
├── .venv/               # Virtual environment (gitignored)
├── .gitignore
└── README.md
```

---

## Dependencies Explained

### Why Each Import Matters:

#### `requirements.txt`:

1. **`gspread`** - The main library for interacting with Google Sheets
   - **Why needed**: Provides the API client to read/write to Google Sheets
   - **What it does**: Handles authentication, reading rows, writing data, batch operations

2. **`google-auth`** - Google authentication library
   - **Why needed**: Authenticates with Google APIs using service account credentials
   - **What it does**: Manages OAuth2 tokens, validates credentials, handles token refresh

3. **`python-dotenv`** - Environment variable management
   - **Why needed**: (Optional) Loads environment variables from `.env` files
   - **What it does**: Keeps sensitive configuration out of code

#### In `expense_tracker.py`:

- **`gspread`** - Used for worksheet operations and error handling
- **`utils`** - Helper functions for generating IDs and timestamps

#### In `sheets_client.py`:

- **`gspread`** - Main Google Sheets client
- **`google.oauth2.service_account`** - Service account authentication

---

## Why Virtual Environment?

### The Problem:

Modern Python installations (especially on macOS/Linux) are **"externally managed"** - meaning you can't install packages system-wide without special permissions. This prevents conflicts and protects your system Python.

### The Solution: Virtual Environment

A **virtual environment** (`.venv`) is an isolated Python environment for your project:

✅ **Isolated dependencies** - Packages installed here don't affect system Python  
✅ **Project-specific versions** - Each project can use different package versions  
✅ **Clean separation** - No conflicts between projects  
✅ **Reproducible** - Others can recreate your exact environment  

### How It Works:

```bash
# Create virtual environment (one time)
python3 -m venv .venv

# Activate it (every time you work on the project)
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate      # Windows

# Now pip installs go into .venv, not system Python
pip install -r requirements.txt

# Deactivate when done
deactivate
```

**Think of it like**: A separate toolbox for each project, so tools don't get mixed up.

---

## Setup Instructions

### Prerequisites:

1. **Python 3.8+** installed
2. **Google Service Account** credentials (`service_account.json`)
3. **Google Sheet** shared with service account email (Editor access)

### Step-by-Step Setup:

#### 1. Create Virtual Environment

```bash
cd 02_validation-batching
python3 -m venv .venv
```

**Why**: Creates isolated Python environment for this project.

#### 2. Activate Virtual Environment

```bash
source .venv/bin/activate  # Linux/Mac/WSL
```

You should see `(.venv)` in your terminal prompt.

**Why**: Tells Python to use the project's isolated environment.

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**What this installs**:
- `gspread` - Google Sheets API client
- `google-auth` - Authentication library
- `python-dotenv` - Environment variable loader

**Why**: These packages provide the functionality to connect to and manipulate Google Sheets.

#### 4. Add Service Account Credentials

Copy `service_account.json` from `01_basic/` or create a new one:

```bash
cp ../01_basic/service_account.json .
```

**Why**: This file contains the credentials needed to authenticate with Google Sheets API.

⚠️ **Security**: Never commit this file to Git! It's already in `.gitignore`.

#### 5. Update Spreadsheet ID (if needed)

Edit `main.py` and update `SPREADSHEET_ID` if using a different spreadsheet:

```python
SPREADSHEET_ID = "your-spreadsheet-id-here"
```

---

## How to Run

### Every Time You Use the Script:

1. **Navigate to project directory**:
   ```bash
   cd 02_validation-batching
   ```

2. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Run the script**:
   ```bash
   python main.py
   ```

4. **Follow the interactive menu**:
   - Choose option 1 to add a single expense
   - Choose option 2 to add multiple expenses (batch mode)
   - Choose option 3 to exit

### Example Session:

```
==================================================
Google Sheets Expense Automation - Version 2
==================================================

✅ Connected to spreadsheet: 1MEUDScbDaq2FhiNy8G8I3eeVItdrBLIaYvYjwZREVLs
✅ Worksheet: Expenses

--------------------------------------------------
What would you like to do?
1. Add a single expense
2. Add multiple expenses (batch)
3. Exit
--------------------------------------------------

Enter your choice (1-3): 1

==================================================
Add New Expense
==================================================

Enter expense details (press Enter to skip optional fields):
Date (e.g., 2024-01-15): 2024-01-20
Description: Coffee
Amount: 5.50
Category (optional): Food
Payment Method (optional): Card

✅ Expense added successfully!
   Expense ID: abc123-def456-...
```

---

## How the Automation Works

### High-Level Flow:

```
User runs main.py
    ↓
Connects to Google Sheets
    ↓
User chooses: Single or Batch mode
    ↓
┌─────────────────────────────────────────┐
│  For Each Expense:                      │
│  1. Validate required fields            │
│     → Prompt if missing                 │
│  2. Validate amount is numeric          │
│     → Log to Errors if invalid          │
│  3. Check for duplicates                │
│     → Prompt user if duplicate found    │
│  4. Add system fields (ID, timestamp)   │
└─────────────────────────────────────────┘
    ↓
Batch all valid expenses
    ↓
Single API call to add all rows
    ↓
Display summary (success/errors/duplicates)
```

### Key Functions:

#### `validate_expense(expense_data)`
- Checks for required fields (date, description, amount)
- Prompts user if any are missing
- Validates amount is numeric
- Returns `(is_valid, error_message)`

#### `check_duplicate(sheet, date, description, amount)`
- Reads all existing expenses
- Compares date, description, and amount
- Returns `True` if duplicate found, `False` otherwise

#### `add_expense(sheet, expense_data)`
- Orchestrates validation and duplicate checking
- Prompts user for duplicate confirmation
- Adds system-managed fields
- Returns `(success, expense_data, error_message)`

#### `batch_add_expenses(sheet, expenses_list, spreadsheet)`
- Processes multiple expenses efficiently
- Validates all, checks duplicates
- Batches all valid expenses into single API call
- Logs errors automatically
- Returns summary dictionary

#### `log_error(spreadsheet, expense_data, error_message)`
- Creates "Errors" worksheet if missing
- Logs invalid expenses with error details
- Includes timestamp for audit trail

---

## Batch Operations Explained

### Why Batch Operations Matter:

**Version 1 approach** (inefficient):
```python
for expense in expenses:
    sheet.update_cell(row, col, value)  # 1 API call per cell
# Result: 9 API calls per expense (9 cells × N expenses)
```

**Version 2 approach** (efficient):
```python
sheet.append_rows(all_expenses)  # 1 API call for all expenses
# Result: 1 API call total, regardless of expense count
```

### Benefits:

✅ **Performance**: 10x-100x faster for multiple expenses  
✅ **API Limits**: Stays within Google Sheets API rate limits  
✅ **Reliability**: Fewer network calls = fewer failure points  
✅ **Cost**: Reduces API quota usage (important for production)  

### Batch Size:

Google Sheets API allows up to **10,000 cells per request**. With 9 columns per expense:
- **Safe batch size**: ~100-200 expenses per batch
- **Maximum**: ~1,100 expenses per batch (theoretical)

The current implementation handles this automatically.

---

## Error Handling

### What Gets Logged to Errors Sheet:

1. **Invalid amounts** - Non-numeric values
2. **Missing required fields** - If validation fails after user prompts
3. **User-rejected duplicates** - If user chooses not to add duplicate

### Error Log Structure:

Each error row contains:
- Original expense data (date, description, amount, etc.)
- Error message explaining why it's invalid
- Timestamp of when error was logged

This allows you to:
- Review invalid expenses later
- Fix and re-add them
- Track data quality issues

---

## Comparison: Version 1 vs Version 2

| Aspect | Version 1 | Version 2 |
|--------|-----------|-----------|
| **Purpose** | Process existing rows | Add new expenses |
| **Mode** | Read-only processing | Interactive entry |
| **Validation** | None | Full validation |
| **Duplicates** | Not checked | Detected & prompted |
| **Errors** | None | Logged to Errors sheet |
| **API Calls** | N calls (one per cell) | 1 call (batch) |
| **User Input** | None | Interactive prompts |
| **Use Case** | Backfill existing data | Daily expense entry |

---

## Troubleshooting

### Common Issues:

#### 1. "Module not found" errors
**Solution**: Make sure virtual environment is activated (`source .venv/bin/activate`)

#### 2. "Permission denied" when accessing sheet
**Solution**: Share the Google Sheet with the service account email (Editor access)

#### 3. "service_account.json not found"
**Solution**: Copy the file from `01_basic/` or create a new service account

#### 4. "Externally managed environment" error
**Solution**: Use virtual environment (see "Why Virtual Environment?" section)

#### 5. Duplicate expenses still being added
**Solution**: Check that date, description, and amount match exactly (case-insensitive for description)

---

## Security Notes

⚠️ **Important Security Practices**:

1. **Never commit `service_account.json`** to Git
   - Already in `.gitignore`
   - Contains sensitive credentials

2. **Rotate credentials** if exposed
   - Delete old service account
   - Create new one
   - Update `service_account.json`

3. **Limit service account permissions**
   - Only grant access to specific spreadsheets
   - Use "Editor" access, not "Owner"

4. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

---

## Next Steps / Future Enhancements

Potential improvements for Version 3:

* 📊 **Reports & Analytics** - Monthly summaries, category breakdowns
* 📅 **Date Range Filtering** - View expenses by date range
* 🔍 **Search Functionality** - Find expenses by description, category
* 💰 **Budget Tracking** - Compare expenses vs budget
* 📧 **Notifications** - Email summaries, alerts
* 🔄 **Scheduled Execution** - Automated daily/weekly runs
* 📱 **CLI Improvements** - Better formatting, colors, progress bars

---

## Status

✅ **Version 2 Complete**

This version provides a robust, production-ready expense entry system with validation, error handling, and efficient batch operations. It's ready for daily use and can be extended with additional features as needed.

---

## Quick Reference

### Daily Workflow:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run script
python main.py

# 3. Choose option 1 or 2
# 4. Enter expenses
# 5. Review results

# 6. Deactivate (optional)
deactivate
```

### Key Files:

- `main.py` - Start here! Interactive menu
- `expense_tracker.py` - Core logic (validation, duplicates, batching)
- `sheets_client.py` - Google Sheets connection
- `utils.py` - Helper functions
- `requirements.txt` - Dependencies list

---

**Happy expense tracking! 🎉**

