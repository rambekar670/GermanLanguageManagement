"""
gui/batches.py
---------------
Batch Management module: full CRUD against the `batches` collection.
A batch groups students of a course into a timetabled class group.
"""

from backend import config
from frontend.base import CRUDFrame
from backend.utils.validation import valid_number, valid_date


class BatchManagementFrame(CRUDFrame):
    title = "Batch Management"
    collection_name = "batches"
    id_field = "batch_id"
    id_prefix = "BAT"
    counter_name = "batch_id"
    auto_id = True

    fields = [
        {"key": "batch_name", "label": "Batch Name", "type": "entry", "required": True},
        {"key": "course", "label": "Course ID", "type": "entry", "required": True},
        {"key": "level", "label": "Level", "type": "combobox", "required": True,
         "options": config.GERMAN_LEVELS},
        {"key": "teacher", "label": "Teacher ID", "type": "entry", "required": True},
        {"key": "timing", "label": "Timing (e.g. Mon-Fri 6PM)", "type": "entry", "required": True},
        {"key": "start_date", "label": "Start Date", "type": "entry", "required": True,
         "validators": [valid_date]},
        {"key": "capacity", "label": "Capacity", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Capacity", allow_float=False, min_value=1)]},
        {"key": "status", "label": "Status", "type": "combobox", "required": True,
         "options": ["Active", "Completed", "Upcoming"]},
    ]

    columns = [
        ("batch_id", "Batch ID", 90),
        ("batch_name", "Batch Name", 130),
        ("course", "Course", 80),
        ("level", "Level", 50),
        ("teacher", "Teacher", 80),
        ("timing", "Timing", 130),
        ("capacity", "Capacity", 70),
        ("status", "Status", 80),
    ]

    def build_document(self, values):
        doc = dict(values)
        doc["capacity"] = int(values["capacity"])
        return doc
