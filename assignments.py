"""
gui/assignments.py
-------------------
Assignment Management module: teachers create assignments for a
course/batch; full CRUD against the `assignments` collection.
"""

from frontend.base import CRUDFrame
from backend.utils.validation import valid_date


class AssignmentManagementFrame(CRUDFrame):
    title = "Assignment Management"
    collection_name = "assignments"
    id_field = "assignment_id"
    id_prefix = "ASG"
    counter_name = "assignment_id"
    auto_id = True

    fields = [
        {"key": "title", "label": "Title", "type": "entry", "required": True},
        {"key": "course", "label": "Course ID", "type": "entry", "required": True},
        {"key": "batch", "label": "Batch ID", "type": "entry", "required": True},
        {"key": "description", "label": "Description", "type": "entry", "required": False},
        {"key": "due_date", "label": "Due Date", "type": "entry", "required": True,
         "validators": [valid_date]},
        {"key": "assigned_by", "label": "Teacher ID", "type": "entry", "required": True},
    ]

    columns = [
        ("assignment_id", "ID", 80),
        ("title", "Title", 150),
        ("course", "Course", 80),
        ("batch", "Batch", 80),
        ("due_date", "Due Date", 90),
        ("assigned_by", "Teacher", 80),
    ]
