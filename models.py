from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class Payment(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str
    payee_added_date_utc: Optional[datetime] = None
    payee_due_date: date
    payee_address_line_1: str
    payee_city: str
    payee_country: str
    payee_postal_code: str
    payee_phone_number: str
    payee_email: EmailStr
    currency: str
    due_amount: float
    discount_percent: Optional[float] = 0.0
    tax_percent: Optional[float] = 0.0
    total_due: Optional[float] = 0.0
    evidence_file: Optional[str] = None
