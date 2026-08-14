"""
gui/students.py
----------------
Student Management module: full CRUD against the `students` collection,
plus search and filter-by-German-level.

Flow: Tkinter Form -> Python (this file) -> PyMongo -> MongoDB
"""

import tkinter as tk
from tkinter import ttk

from backend import config
from frontend.base import CRUDFrame
from backend.utils.helpers import hash_password
from backend.utils.validation import valid_email, valid_phone, valid_date, valid_number


class StudentManagementFrame(CRUDFrame):
    title = "Student Management"
    collection_name = "students"
    id_field = "student_id"
    id_prefix = "STU"
    counter_name = "student_id"
    auto_id = True

    fields = [
        {"key": "full_name", "label": "Full Name", "type": "entry", "required": True},
        {"key": "dob", "label": "Date of Birth", "type": "entry", "required": True,
         "validators": [valid_date]},
        {"key": "gender", "label": "Gender", "type": "combobox", "required": True,
         "options": ["Male", "Female", "Other"]},
        {"key": "phone", "label": "Phone", "type": "entry", "required": True,
         "validators": [valid_phone]},
        {"key": "email", "label": "Email", "type": "entry", "required": True,
         "validators": [valid_email]},
        {"key": "address", "label": "Address", "type": "entry", "required": False},
        {"key": "german_level", "label": "German Level", "type": "combobox", "required": True,
         "options": config.GERMAN_LEVELS},
        {"key": "course", "label": "Course ID", "type": "entry", "required": True},
        {"key": "batch", "label": "Batch ID", "type": "entry", "required": True},
        {"key": "admission_date", "label": "Admission Date", "type": "entry", "required": True,
         "validators": [valid_date]},
        {"key": "fees", "label": "Fees", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Fees", min_value=0)]},
        {"key": "password", "label": "Password", "type": "password", "required": True},
    ]

    columns = [
        ("student_id", "Student ID", 90),
        ("full_name", "Full Name", 140),
        ("german_level", "Level", 60),
        ("course", "Course", 80),
        ("batch", "Batch", 80),
        ("phone", "Phone", 110),
        ("email", "Email", 160),
        ("fees", "Fees", 70),
    ]

    def build_extra_filters(self, parent):
        wrapper = tk.Frame(parent, bg=config.THEME_COLOR_BG)
        tk.Label(wrapper, text="Level:", bg=config.THEME_COLOR_BG,
                 font=(config.FONT_FAMILY, 9)).pack(side="left")
        self.level_filter = tk.StringVar(value="All")
        combo = ttk.Combobox(wrapper, textvariable=self.level_filter, state="readonly",
                              width=8, values=["All"] + config.GERMAN_LEVELS)
        combo.pack(side="left", padx=4)
        combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        return wrapper

    def get_query(self):
        query = super().get_query()
        level = getattr(self, "level_filter", None)
        if level and level.get() and level.get() != "All":
            query["german_level"] = level.get()
        return query

    def build_document(self, values):
        doc = dict(values)
        # Only re-hash the password if it looks like it was typed fresh
        # (on update, if the admin left it blank we keep the old hash).
        if doc.get("password"):
            doc["password"] = hash_password(doc["password"])
        else:
            doc.pop("password", None)
        doc["fees"] = float(values["fees"])
        doc["role"] = "student"
        return doc

    def set_form_values(self, doc):
        super().set_form_values(doc)
        # Never show the password hash back in the form.
        self.entries["password"]["var"].set("")
