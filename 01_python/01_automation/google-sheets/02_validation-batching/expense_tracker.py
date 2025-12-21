"""
Expense Tracker Module - Version 2
Handles expense validation, duplicate checking, and batch operations.
"""

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

