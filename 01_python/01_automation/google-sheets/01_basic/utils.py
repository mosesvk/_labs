import uuid 
from datetime import datetime

def generate_expense_id() -> str:
    return str(uuid.uuid4())

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()