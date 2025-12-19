from utils import generate_expense_id, utc_timestamp

SYSTEM_NOTE = 'Tracked by Python authomation'

def process_expenses(sheet): 
    rows = sheet.get_all_records()
    updates = []

    for index, row in enumerate(rows, start=2): 
        if row.get('expense_id'): 
            continue

        updates.append({
            'row': index, 
            'expense_id': generate_expense_id(),
            'processed': True, 
            'processed_at': utc_timestamp(),
            'script_notes': SYSTEM_NOTE
        })

    return updates