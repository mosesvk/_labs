"""
Expense Tracker Module - Version 2
Handles expense validation, duplicate checking, and batch operations.
"""
import gspread
from utils import generate_expense_id, utc_timestamp

def validate_expense(expense_data: dict) -> tuple[bool, str]:
    """
    Validates an expense entry and prompts user for missing required fields.
    
    Required fields: date, description, amount
    
    Args:
        expense_data: Dictionary containing expense fields (date, description, amount, etc.)
                     This dict will be modified in place if user provides missing values.
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, error_message will be empty string.
    """
    # Check for missing required fields and prompt user
    required_fields = {
        'date': 'Enter the expense date (e.g., 2024-01-15): ',
        'description': 'Enter the expense description: ',
        'amount': 'Enter the expense amount: '
    }
    
    # Loop through required_fields and check if each exists and is not empty
    # If missing or empty, use input() to prompt user
    # Update expense_data with the user's input
    for field_name, prompt_message in required_fields.items():
        # Get current value, default to empty string if not present
        current_value = expense_data.get(field_name, '')
        
        # Check if value is missing or empty (after stripping whitespace)
        if not current_value or not str(current_value).strip():
            # Prompt user for the missing value
            user_input = input(prompt_message)
            # Update expense_data with user's input
            expense_data[field_name] = user_input.strip()
    
    
    # After ensuring all required fields exist, validate amount is numeric
    try:
        # Try to convert amount to float
        float(expense_data['amount'])
        return True, ""
    except (ValueError, TypeError):
        # If conversion fails, return error
        return False, "Amount must be a valid number"


def check_duplicate(sheet, date: str, description: str, amount: str) -> bool:
    """
    Checks if an expense with the same date, description, and amount already exists.
    
    Args:
        sheet: The gspread worksheet object
        date: Expense date
        description: Expense description
        amount: Expense amount (as string)
        
    Returns:
        True if duplicate exists, False otherwise
    """
    # Get all existing expense records from the sheet
    existing_expenses = sheet.get_all_records()
    
    # Normalize the input amount to float for comparison
    # This handles cases where amounts might be stored as strings or numbers
    try:
        input_amount = float(amount)
    except (ValueError, TypeError):
        # If amount can't be converted, it's invalid, so no duplicate possible
        return False
    
    # Loop through all existing expenses
    for expense in existing_expenses:
        # Get values from the existing expense row
        existing_date = expense.get('date', '')
        existing_description = expense.get('description', '')
        existing_amount_str = expense.get('amount', '')
        
        # Normalize existing amount to float for comparison
        try:
            existing_amount = float(existing_amount_str)
        except (ValueError, TypeError):
            # Skip this row if amount is invalid
            continue
        
        # Compare all three fields: date, description, and amount
        # Strip whitespace for date and description to handle formatting differences
        if (str(existing_date).strip() == str(date).strip() and
            str(existing_description).strip().lower() == str(description).strip().lower() and
            existing_amount == input_amount):
            # Found a duplicate!
            return True
    
    # No duplicate found after checking all rows
    return False


def add_expense(sheet, expense_data: dict) -> tuple[bool, dict, str]:
    """
    Validates and adds an expense, checking for duplicates and prompting user if needed.
    
    Args:
        sheet: The gspread worksheet object
        expense_data: Dictionary containing expense fields (date, description, amount, etc.)
        
    Returns:
        Tuple of (success: bool, expense_data: dict, error_message: str)
        - If success is True: expense_data will contain the validated expense with system fields
        - If success is False: error_message will contain the reason
    """
    # Step 1: Validate the expense (this will prompt for missing fields)
    is_valid, error_message = validate_expense(expense_data)
    
    if not is_valid:
        # Validation failed, return error
        return False, expense_data, error_message
    
    # Step 2: Check for duplicates
    date = expense_data.get('date', '')
    description = expense_data.get('description', '')
    amount = expense_data.get('amount', '')
    
    is_duplicate = check_duplicate(sheet, date, description, amount)
    
    if is_duplicate:
        # Duplicate found - prompt user for confirmation
        print(f"\n⚠️  Duplicate expense detected!")
        print(f"   Date: {date}")
        print(f"   Description: {description}")
        print(f"   Amount: {amount}")
        user_response = input("This expense was added before. Do you want to add it again? (yes/no): ")
        
        if user_response.lower() not in ['yes', 'y']:
            # User chose not to add duplicate
            return False, expense_data, "Duplicate expense - user chose not to add"
    
    # Step 3: Add system-managed fields to expense_data
    expense_data['expense_id'] = generate_expense_id()
    expense_data['processed'] = True
    expense_data['processed_at'] = utc_timestamp()
    expense_data['script_notes'] = 'Tracked by Python automation v2'
    
    # Success! Return the complete expense data
    return True, expense_data, ""


def log_error(spreadsheet, expense_data: dict, error_message: str) -> None:
    """
    Logs an invalid expense to the "Errors" worksheet.
    
    Creates the "Errors" worksheet if it doesn't exist.
    
    Args:
        spreadsheet: The gspread spreadsheet object (not worksheet)
        expense_data: Dictionary containing the invalid expense data
        error_message: The error message explaining why it's invalid
    """
    ERROR_SHEET_NAME = "Errors"
    
    try:
        # Try to get the Errors worksheet
        error_sheet = spreadsheet.worksheet(ERROR_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        # If it doesn't exist, create it with headers
        error_sheet = spreadsheet.add_worksheet(
            title=ERROR_SHEET_NAME,
            rows=1000,
            cols=10
        )
        # Set up headers
        headers = [
            'date',
            'description',
            'amount',
            'category',
            'payment_method',
            'error_message',
            'logged_at'
        ]
        error_sheet.append_row(headers)
    
    # Prepare the error row data
    error_row = [
        expense_data.get('date', ''),
        expense_data.get('description', ''),
        expense_data.get('amount', ''),
        expense_data.get('category', ''),
        expense_data.get('payment_method', ''),
        error_message,
        utc_timestamp()
    ]
    
    # Append the error row to the Errors sheet
    error_sheet.append_row(error_row)


def batch_add_expenses(sheet, expenses_list: list[dict], spreadsheet=None) -> dict:
    """
    Processes and adds multiple expenses in a batch operation.
    
    Validates each expense, checks for duplicates, and batches all valid expenses
    into a single API call for efficiency.
    
    Args:
        sheet: The gspread worksheet object (Expenses sheet)
        expenses_list: List of expense dictionaries to process
        spreadsheet: Optional spreadsheet object (needed for error logging)
                     If not provided, will be extracted from sheet
        
    Returns:
        Dictionary with summary:
        {
            'success_count': int,
            'error_count': int,
            'duplicate_count': int,
            'added_expenses': list[dict],
            'errors': list[dict]  # Each error dict has 'expense' and 'message'
        }
    """
    # Get spreadsheet object if not provided (needed for error logging)
    if spreadsheet is None:
        spreadsheet = sheet.spreadsheet
    
    # Results tracking
    valid_expenses = []
    errors = []
    duplicate_count = 0
    
    # Process each expense
    for expense_data in expenses_list:
        # Make a copy to avoid modifying the original
        expense = expense_data.copy()
        
        # Validate the expense
        is_valid, error_message = validate_expense(expense)
        
        if not is_valid:
            # Validation failed - log error
            errors.append({
                'expense': expense,
                'message': error_message
            })
            if spreadsheet:
                log_error(spreadsheet, expense, error_message)
            continue
        
        # Check for duplicates
        date = expense.get('date', '')
        description = expense.get('description', '')
        amount = expense.get('amount', '')
        
        is_duplicate = check_duplicate(sheet, date, description, amount)
        
        if is_duplicate:
            # Duplicate found - skip it (in batch mode, we skip duplicates)
            # You could modify this to prompt user, but for batch operations,
            # skipping is usually better
            duplicate_count += 1
            errors.append({
                'expense': expense,
                'message': 'Duplicate expense - skipped'
            })
            continue
        
        # Add system-managed fields
        expense['expense_id'] = generate_expense_id()
        expense['processed'] = True
        expense['processed_at'] = utc_timestamp()
        expense['script_notes'] = 'Tracked by Python automation v2'
        
        # Add to valid expenses list
        valid_expenses.append(expense)
    
    # Batch add all valid expenses at once
    if valid_expenses:
        # Prepare rows for batch append
        # Column order: date, description, amount, category, payment_method,
        #               expense_id, processed, processed_at, script_notes
        rows_to_add = []
        for expense in valid_expenses:
            row = [
                expense.get('date', ''),
                expense.get('description', ''),
                expense.get('amount', ''),
                expense.get('category', ''),
                expense.get('payment_method', ''),
                expense.get('expense_id', ''),
                expense.get('processed', ''),
                expense.get('processed_at', ''),
                expense.get('script_notes', '')
            ]
            rows_to_add.append(row)
        
        # Batch append all rows in a single API call
        # This is much more efficient than individual append_row calls
        sheet.append_rows(rows_to_add)
    
    # Return summary
    return {
        'success_count': len(valid_expenses),
        'error_count': len(errors),
        'duplicate_count': duplicate_count,
        'added_expenses': valid_expenses,
        'errors': errors
    }

