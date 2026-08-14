"""
gui/teachers.py
----------------
Teacher Management module: full CRUD against the `teachers` collection.
"""

import tkinter as tk
from backend import config
from frontend.base import CRUDFrame
from backend.utils.helpers import hash_password
from backend.utils.validation import valid_email, valid_phone, valid_number


class TeacherManagementFrame(CRUDFrame):
    title = "Teacher Management"
    collection_name = "teachers"
    id_field = "teacher_id"
    id_prefix = "TCH"
    counter_name = "teacher_id"
    auto_id = True

    fields = [
        {"key": "full_name", "label": "Name", "type": "entry", "required": True},
        {"key": "phone", "label": "Phone", "type": "entry", "required": True,
         "validators": [valid_phone]},
        {"key": "email", "label": "Email", "type": "entry", "required": True,
         "validators": [valid_email]},
        {"key": "qualification", "label": "Qualification", "type": "entry", "required": True},
        {"key": "specialization", "label": "German Specialization", "type": "combobox",
         "required": True, "options": config.GERMAN_LEVELS + ["General"]},
        {"key": "experience", "label": "Experience (yrs)", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Experience", min_value=0)]},
        {"key": "assigned_course", "label": "Assigned Course", "type": "entry", "required": False},
        {"key": "assigned_batch", "label": "Assigned Batch", "type": "entry", "required": False},
        {"key": "password", "label": "Login Password", "type": "password", "required": True},
    ]

    columns = [
        ("teacher_id", "Teacher ID", 90),
        ("full_name", "Name", 140),
        ("specialization", "Specialization", 100),
        ("experience", "Experience", 80),
        ("assigned_course", "Course", 80),
        ("assigned_batch", "Batch", 80),
        ("phone", "Phone", 110),
    ]

    def build_document(self, values):
        doc = dict(values)
        if doc.get("password"):
            doc["password"] = hash_password(doc["password"])
        else:
            doc.pop("password", None)
        doc["experience"] = float(values["experience"])
        doc["role"] = "teacher"
        return doc

    def set_form_values(self, doc):
        super().set_form_values(doc)
        self.entries["password"]["var"].set("")
