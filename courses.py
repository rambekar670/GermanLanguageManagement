"""
gui/courses.py
---------------
Course Management module: full CRUD against the `courses` collection.
Levels: A1, A2, B1, B2 (see config.GERMAN_LEVELS).
"""

from backend import config
from frontend.base import CRUDFrame
from backend.utils.validation import valid_number, valid_date


class CourseManagementFrame(CRUDFrame):
    title = "Course Management"
    collection_name = "courses"
    id_field = "course_id"
    id_prefix = "CRS"
    counter_name = "course_id"
    auto_id = True

    fields = [
        {"key": "course_name", "label": "Course Name", "type": "entry", "required": True},
        {"key": "level", "label": "Level", "type": "combobox", "required": True,
         "options": config.GERMAN_LEVELS},
        {"key": "duration", "label": "Duration (weeks)", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Duration", allow_float=False, min_value=1)]},
        {"key": "fees", "label": "Fees", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Fees", min_value=0)]},
        {"key": "teacher", "label": "Teacher ID", "type": "entry", "required": True},
        {"key": "batch", "label": "Batch ID", "type": "entry", "required": False},
        {"key": "start_date", "label": "Start Date", "type": "entry", "required": True,
         "validators": [valid_date]},
        {"key": "end_date", "label": "End Date", "type": "entry", "required": True,
         "validators": [valid_date]},
        {"key": "max_students", "label": "Max Students", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Max Students", allow_float=False, min_value=1)]},
    ]

    columns = [
        ("course_id", "Course ID", 90),
        ("course_name", "Course Name", 140),
        ("level", "Level", 50),
        ("duration", "Duration", 80),
        ("fees", "Fees", 70),
        ("teacher", "Teacher", 80),
        ("start_date", "Start", 90),
        ("end_date", "End", 90),
        ("max_students", "Max", 50),
    ]

    def build_document(self, values):
        doc = dict(values)
        doc["duration"] = int(values["duration"])
        doc["fees"] = float(values["fees"])
        doc["max_students"] = int(values["max_students"])
        return doc
