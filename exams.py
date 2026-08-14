"""
gui/exams.py
-------------
Examination module: teachers enter Reading/Writing/Listening/Speaking
marks for a student's exam. Total marks, percentage and grade are
calculated automatically. Saving an exam also writes/updates a
matching document in the `results` collection so the Results module
can show a consolidated view.

Collection: exams  (source of truth for marks entry)
Mirrored into: results (for the Results browsing module)
"""

from backend import config
from frontend.base import CRUDFrame
from backend.database import get_db
from backend.utils.helpers import calculate_grade, calculate_result
from backend.utils.validation import valid_number


class ExaminationFrame(CRUDFrame):
    title = "Examination"
    collection_name = "exams"
    id_field = "exam_entry_id"
    id_prefix = "EXM"
    counter_name = "exam_entry_id"
    auto_id = True

    fields = [
        {"key": "student_id", "label": "Student ID", "type": "entry", "required": True},
        {"key": "student_name", "label": "Student Name", "type": "entry", "required": True},
        {"key": "course", "label": "Course", "type": "entry", "required": True},
        {"key": "exam_name", "label": "Exam Name", "type": "entry", "required": True},
        {"key": "german_level", "label": "German Level", "type": "combobox", "required": True,
         "options": config.GERMAN_LEVELS},
        {"key": "reading_marks", "label": "Reading (0-25)", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Reading Marks", min_value=0, max_value=25)]},
        {"key": "writing_marks", "label": "Writing (0-25)", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Writing Marks", min_value=0, max_value=25)]},
        {"key": "listening_marks", "label": "Listening (0-25)", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Listening Marks", min_value=0, max_value=25)]},
        {"key": "speaking_marks", "label": "Speaking (0-25)", "type": "entry", "required": True,
         "validators": [lambda v: valid_number(v, "Speaking Marks", min_value=0, max_value=25)]},
    ]

    columns = [
        ("exam_entry_id", "Exam ID", 80),
        ("student_id", "Student ID", 90),
        ("exam_name", "Exam", 100),
        ("german_level", "Level", 55),
        ("total_marks", "Total", 60),
        ("percentage", "%", 60),
        ("grade", "Grade", 55),
        ("result", "Result", 60),
    ]

    def build_document(self, values):
        doc = dict(values)
        reading = float(values["reading_marks"])
        writing = float(values["writing_marks"])
        listening = float(values["listening_marks"])
        speaking = float(values["speaking_marks"])

        total = reading + writing + listening + speaking      # out of 100
        percentage = round(total, 2)                           # each skill is out of 25 -> sums to /100
        grade = calculate_grade(percentage)
        result = calculate_result(percentage)

        doc["reading_marks"] = reading
        doc["writing_marks"] = writing
        doc["listening_marks"] = listening
        doc["speaking_marks"] = speaking
        doc["total_marks"] = total
        doc["percentage"] = percentage
        doc["grade"] = grade
        doc["result"] = result
        return doc

    def on_add(self):
        super().on_add()
        self._mirror_latest_to_results()

    def on_update(self):
        super().on_update()
        self._mirror_latest_to_results()

    def _mirror_latest_to_results(self):
        """Keep the `results` collection in sync with the `exams` collection."""
        db = get_db()
        latest = self.collection.find_one(sort=[("_id", -1)])
        if not latest:
            return
        result_doc = {k: v for k, v in latest.items() if k != "_id"}
        result_doc["result_id"] = latest["exam_entry_id"].replace("EXM", "RES")
        db.results.update_one(
            {"exam_entry_id": latest["exam_entry_id"]},
            {"$set": result_doc},
            upsert=True,
        )
