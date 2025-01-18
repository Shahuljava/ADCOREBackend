
import pandas as pd
from pymongo import MongoClient
from pydantic import BaseModel, ValidationError
from typing import Optional
import datetime
import requests


MONGO_URI = "mongodb+srv://shahulshaik2727:SHh3DfJrSoM6VEcV@learning.2g9xfoz.mongodb.net/payment_db"
client = MongoClient(MONGO_URI)
db = client["payment_db"]
payments_collection = db["payments"]

class Payment(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str
    payee_added_date_utc: Optional[datetime.datetime]
    payee_due_date: Optional[datetime.datetime]
    payee_address_line_1: str
    payee_address_line_2: Optional[str]
    payee_city: str
    payee_country: Optional[str]
    payee_province_or_state: Optional[str]
    payee_postal_code: Optional[str]
    payee_phone_number: Optional[str]
    payee_email: str
    currency: str
    discount_percent: Optional[float]
    tax_percent: Optional[float]
    due_amount: float
    total_due: Optional[float] = 0.0
    evidence_file: Optional[str] = None


def fetch_country_data():
    try:
        response = requests.get('https://countriesnow.space/api/v0.1/countries/positions')
        response.raise_for_status()
        countries_data = response.json().get('data', [])
        iso2_to_country = {country['iso2']: country['name'] for country in countries_data}
        return iso2_to_country
    except requests.RequestException as e:
        print(f"Error fetching country data: {e}")
        return {}


def normalize_validate_and_save_to_mongo(file_path: str):
    try:
        
        country_mapping = fetch_country_data()

        data = pd.read_csv(file_path)

        for column in data.columns:
            if column in ["payee_postal_code", "payee_phone_number"]:
                data[column] = data[column].fillna(0).astype(int).astype(str)
            elif column == "payee_added_date_utc":
                data[column] = pd.to_datetime(data[column], unit="s", errors="coerce")
            elif column == "payee_due_date":
                data[column] = pd.to_datetime(data[column], errors="coerce").dt.date
            elif column == "payee_country":
                data[column] = data[column].map(country_mapping).fillna(data[column]).astype(str)



        valid_entries = []
        invalid_entries = []

        for _, row in data.iterrows():
            try:
                row_dict = row.to_dict()
                payment = Payment(**row_dict)

                if isinstance(payment.payee_due_date, datetime.date):
                    payment.payee_due_date = datetime.datetime.combine(payment.payee_due_date, datetime.time.min)

                valid_entries.append(payment.dict())
            except ValidationError as e:
                invalid_entries.append({"row": row.to_dict(), "error": str(e)})

        print(f"Total valid entries: {len(valid_entries)}")
        print(f"Total invalid entries: {len(invalid_entries)}")

        if valid_entries:
            insert_result = payments_collection.insert_many(valid_entries)
            print(f"Inserted {len(insert_result.inserted_ids)} entries into MongoDB.")
            
    except Exception as e:
        print("Error during normalization, validation, or MongoDB insertion:", e)


file_path = "./payment_information.csv"
# normalize_validate_and_save_to_mongo(file_path)