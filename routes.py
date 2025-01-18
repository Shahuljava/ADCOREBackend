from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Query
from database import payments_collection
from models import Payment
from bson.objectid import ObjectId
from datetime import datetime, date, timezone
import os
from typing import Optional
from fastapi.responses import FileResponse
import mimetypes
router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value

@router.post("/payments/")
def create_payment(payment: Payment):
    payment_dict = payment.dict()
    payment_dict["payee_due_date"] = datetime.combine(payment_dict["payee_due_date"], datetime.min.time())
    discount = payment_dict["due_amount"] * (payment_dict.get("discount_percent", 0) / 100)
    tax = payment_dict["due_amount"] * (payment_dict.get("tax_percent", 0) / 100)
    payment_dict["total_due"] = round(payment_dict["due_amount"] - discount + tax, 2)
    payment_dict["payee_added_date_utc"] = datetime.now(timezone.utc)
    result = payments_collection.insert_one(payment_dict)
    return {"id": str(result.inserted_id)}


@router.get("/payments/")
@router.get("/payments/")
def get_payments(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
):
    query = {}

    # Filter by status
    if status:
        query["payee_payment_status"] = status

    # Search by payee_first_name (case-insensitive)
    if search:
        query["payee_first_name"] = {"$regex": search, "$options": "i"}

    payments_cursor = payments_collection.find(query).skip((page - 1) * size).limit(size)
    payments = list(payments_cursor)

    today = date.today()
    for payment in payments:
        payment_due_date = payment.get("payee_due_date")

        if payment_due_date:
            if isinstance(payment_due_date, str):
                payment_due_date = datetime.strptime(payment_due_date, "%Y-%m-%d").date()
            elif isinstance(payment_due_date, datetime):
                payment_due_date = payment_due_date.date()

            if payment["payee_payment_status"] not in ["completed", "pending"]:
                if payment_due_date < today:
                    payment["payee_payment_status"] = "overdue"
                elif payment_due_date == today:
                    payment["payee_payment_status"] = "due_now"

        payment["_id"] = str(payment["_id"])

        # Calculate total_due dynamically
        discount = payment.get("due_amount", 0) * (payment.get("discount_percent", 0) / 100)
        tax = payment.get("due_amount", 0) * (payment.get("tax_percent", 0) / 100)
        payment["total_due"] = round(payment.get("due_amount", 0) - discount + tax, 2)

    # Count total matching documents for pagination
    total = payments_collection.count_documents(query)
    total_pages = (total + size - 1) // size 

    return {
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "data": payments,
    }


@router.get("/payments/{payment_id}")
def get_payment_by_id(payment_id: str):
    try:
        payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found.")

        payment["_id"] = str(payment["_id"])

        # Calculate total_due dynamically
        discount = payment["due_amount"] * (payment.get("discount_percent", 0) / 100)
        tax = payment["due_amount"] * (payment.get("tax_percent", 0) / 100)
        payment["total_due"] = round(payment["due_amount"] - discount + tax, 2)

        payment_due_date = payment.get("payee_due_date")
        today = date.today()

        if payment_due_date:
            if isinstance(payment_due_date, str):
                payment_due_date = datetime.strptime(payment_due_date, "%Y-%m-%d").date()
            elif isinstance(payment_due_date, datetime):
                payment_due_date = payment_due_date.date()

            if payment["payee_payment_status"] not in ["completed", "pending"]:
                if payment_due_date < today:
                    payment["payee_payment_status"] = "overdue"
                elif payment_due_date == today:
                    payment["payee_payment_status"] = "due_now"
        return payment

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching payment: {str(e)}")

@router.put("/payments/{payment_id}")
def update_payment(payment_id: str, payment: Payment):
    existing_payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
    if not existing_payment:
        raise HTTPException(status_code=404, detail="Payment not found.")
    update_data = payment.dict(exclude_unset=True)
    if "payee_due_date" in update_data and isinstance(update_data["payee_due_date"], date):
        update_data["payee_due_date"] = datetime.combine(update_data["payee_due_date"], datetime.min.time())
    if payment.payee_payment_status == "completed" and not existing_payment.get("evidence_file"):
        raise HTTPException(status_code=400, detail="Evidence file is required to mark payment as completed.")
    result = payments_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return {"message": "Payment updated successfully."}

@router.post("/payments/{payment_id}/upload_evidence/")
async def upload_evidence(payment_id: str, file: UploadFile):
    if not file.filename.endswith(("pdf", "png", "jpg", "jpeg")):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    file_path = os.path.join(UPLOAD_DIR, f"{payment_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    payments_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": {"evidence_file": file_path}})
    return {"message": "Evidence uploaded successfully.", "file_path": file_path}

@router.get("/payments/{payment_id}/download_evidence/")
def download_evidence(payment_id: str):
    payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
    if not payment or "evidence_file" not in payment:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    
    file_path = payment["evidence_file"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on the server.")
    
    # Determine the MIME type based on the file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"  # Default fallback for unknown types

    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type=mime_type)
@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: str):
    result = payments_collection.delete_one({"_id": ObjectId(payment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return {"message": "Payment deleted successfully."}