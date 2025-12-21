"""
Main script for Google Sheets Expense Automation - Version 2
Handles expense validation, duplicate checking, and batch operations.
"""
from sheets_client import get_sheet
from expense_tracker import add_expense, batch_add_expenses, log_error

# Configuration
SPREADSHEET_ID = "1MEUDScbDaq2FhiNy8G8I3eeVItdrBLIaYvYjwZREVLs"
WORKSHEET_NAME = "Expenses"


def add_single_expense(sheet, spreadsheet):
    """
    Interactive function to add a single expense.
    """
    print("\n" + "="*50)
    print("Add New Expense")
    print("="*50)
    
    # Get expense data from user
    expense_data = {}
    print("\nEnter expense details (press Enter to skip optional fields):")
    expense_data['date'] = input("Date (e.g., 2024-01-15): ").strip()
    expense_data['description'] = input("Description: ").strip()
    expense_data['amount'] = input("Amount: ").strip()
    expense_data['category'] = input("Category (optional): ").strip()
    expense_data['payment_method'] = input("Payment Method (optional): ").strip()
    
    # Add the expense (validation and duplicate checking happens inside)
    success, expense_data, error_message = add_expense(sheet, expense_data)
    
    if success:
        # Add to sheet (single row append)
        row = [
            expense_data.get('date', ''),
            expense_data.get('description', ''),
            expense_data.get('amount', ''),
            expense_data.get('category', ''),
            expense_data.get('payment_method', ''),
            expense_data.get('expense_id', ''),
            expense_data.get('processed', ''),
            expense_data.get('processed_at', ''),
            expense_data.get('script_notes', '')
        ]
        sheet.append_row(row)
        print(f"\n✅ Expense added successfully!")
        print(f"   Expense ID: {expense_data.get('expense_id')}")
    else:
        # Log error
        print(f"\n❌ Error: {error_message}")
        log_error(spreadsheet, expense_data, error_message)
        print("   Error has been logged to the Errors sheet.")


def add_multiple_expenses(sheet, spreadsheet):
    """
    Interactive function to add multiple expenses in batch.
    """
    print("\n" + "="*50)
    print("Add Multiple Expenses (Batch Mode)")
    print("="*50)
    
    expenses_list = []
    print("\nEnter expenses (press Enter with empty date to finish):")
    
    while True:
        print(f"\n--- Expense #{len(expenses_list) + 1} ---")
        date = input("Date (e.g., 2024-01-15) or Enter to finish: ").strip()
        
        if not date:
            break
        
        expense_data = {
            'date': date,
            'description': input("Description: ").strip(),
            'amount': input("Amount: ").strip(),
            'category': input("Category (optional): ").strip(),
            'payment_method': input("Payment Method (optional): ").strip()
        }
        
        expenses_list.append(expense_data)
    
    if not expenses_list:
        print("\nNo expenses to add.")
        return
    
    # Process batch
    print(f"\nProcessing {len(expenses_list)} expense(s)...")
    result = batch_add_expenses(sheet, expenses_list, spreadsheet)
    
    # Display results
    print("\n" + "="*50)
    print("Batch Processing Results")
    print("="*50)
    print(f"✅ Successfully added: {result['success_count']}")
    print(f"❌ Errors: {result['error_count']}")
    print(f"⚠️  Duplicates skipped: {result['duplicate_count']}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  - {error['message']}: {error['expense'].get('description', 'N/A')}")


def main():
    """
    Main function that orchestrates the expense tracking automation.
    """
    print("="*50)
    print("Google Sheets Expense Automation - Version 2")
    print("="*50)
    
    # Connect to spreadsheet
    try:
        sheet = get_sheet(SPREADSHEET_ID, WORKSHEET_NAME)
        spreadsheet = sheet.spreadsheet
        print(f"\n✅ Connected to spreadsheet: {SPREADSHEET_ID}")
        print(f"✅ Worksheet: {WORKSHEET_NAME}")
    except Exception as e:
        print(f"\n❌ Error connecting to spreadsheet: {e}")
        return
    
    # Main menu loop
    while True:
        print("\n" + "-"*50)
        print("What would you like to do?")
        print("1. Add a single expense")
        print("2. Add multiple expenses (batch)")
        print("3. Exit")
        print("-"*50)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            add_single_expense(sheet, spreadsheet)
        elif choice == '2':
            add_multiple_expenses(sheet, spreadsheet)
        elif choice == '3':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
