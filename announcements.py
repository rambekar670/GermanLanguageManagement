"""
gui/announcements.py
---------------------
Announcements module: admin/teachers post announcements visible to
everyone. Full CRUD against the `announcements` collection.
"""

from datetime import date
from frontend.base import CRUDFrame


class AnnouncementFrame(CRUDFrame):
    title = "Announcements"
    collection_name = "announcements"
    id_field = "announcement_id"
    id_prefix = "ANN"
    counter_name = "announcement_id"
    auto_id = True

    fields = [
        {"key": "heading", "label": "Heading", "type": "entry", "required": True},
        {"key": "message", "label": "Message", "type": "entry", "required": True},
        {"key": "posted_by", "label": "Posted By", "type": "entry", "required": True},
        {"key": "audience", "label": "Audience", "type": "combobox", "required": True,
         "options": ["All", "Students", "Teachers"]},
    ]

    columns = [
        ("announcement_id", "ID", 80),
        ("heading", "Heading", 150),
        ("message", "Message", 220),
        ("audience", "Audience", 80),
        ("posted_by", "Posted By", 90),
        ("date_posted", "Date", 90),
    ]

    def build_document(self, values):
        doc = dict(values)
        doc["date_posted"] = date.today().isoformat()
        return doc
