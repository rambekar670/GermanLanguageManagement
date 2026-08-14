"""
gui/fees.py
------------
Fee Management module: full CRUD against the `fees` collection.
Automatically calculates:
    Remaining Amount = Total Fees - Paid Amount
    Payment Status   = Paid / Partially Paid / Pending
"""

from frontend.base import CRUDFrame
from backend.utils.helpers import calculate_fee_status
from backend.utils.validation import valid_number, valid_date


class FeeManagementFrame(CRUDFrame):
    title = "Fee Management"
    collection_name = "fees"
    id_field = "fee_id"
    id_prefix = "FEE"
    counter_name = "fee_id"
    auto_id = True

    fields = [
        {"key": "student_id", "label": "Student ID", "type": "entry", "required": True},
        {"key": "student_name", "label": "Student Name", "type": "entry", "required": True},
        {"key": "course", "label": "Course", "type": "entry", "required": True},
        {"key": "total_fees", "label": "Total Fees", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Total Fees", min_value=0)]},
        {"key": "paid_amount", "label": "Paid Amount", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Paid Amount", min_value=0)]},
        {"key": "payment_date", "label": "Payment Date", "type": "entry", "required": True,
         "validators": [valid_date]},
    ]

    columns = [
        ("fee_id", "Fee ID", 80),
        ("student_id", "Student ID", 90),
        ("student_name", "Name", 130),
        ("course", "Course", 80),
        ("total_fees", "Total", 70),
        ("paid_amount", "Paid", 70),
        ("remaining_amount", "Remaining", 80),
        ("payment_status", "Status", 100),
    ]

    def build_document(self, values):
        doc = dict(values)
        total = float(values["total_fees"])
        paid = float(values["paid_amount"])
        doc["total_fees"] = total
        doc["paid_amount"] = paid
        doc["remaining_amount"] = round(total - paid, 2)
        doc["payment_status"] = calculate_fee_status(total, paid)
        return doc

    def row_tags(self, doc):
        return ("warning",) if doc.get("payment_status") == "Pending" else ()
