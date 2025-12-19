from sheets_client import get_sheet
from expense_tracker import process_expenses

SPREADSHEET_ID = "1MEUDScbDaq2FhiNy8G8I3eeVItdrBLIaYvYjwZREVLs"
WORKSHEET_NAME = "Expenses"

def main():
    sheet = get_sheet(SPREADSHEET_ID, WORKSHEET_NAME)

    updates = process_expenses(sheet)

    for update in updates:
        row = update["row"]
        sheet.update_cell(row, 6, update["expense_id"])      # F
        sheet.update_cell(row, 7, update["processed"])       # G
        sheet.update_cell(row, 8, update["processed_at"])    # H
        sheet.update_cell(row, 9, update["script_notes"])    # I

    print(f"Processed {len(updates)} new expenses")

if __name__ == "__main__":
    main()
