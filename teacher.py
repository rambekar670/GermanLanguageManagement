"""
models/teacher.py
------------------
Defines the expected shape of a teacher document, plus small
convenience lookup helpers.
"""

from backend.database import get_db

TEACHER_SCHEMA_EXAMPLE = {
    "teacher_id": "TCH0001",
    "full_name": "Markus Weber",
    "phone": "+4915123456789",
    "email": "markus.weber@example.com",
    "qualification": "M.A. German Studies",
    "specialization": "B2",
    "experience": 6.0,
    "assigned_course": "CRS0002",
    "assigned_batch": "BAT0002",
    "password": b"<bcrypt-hash>",
    "role": "teacher",
}


def get_teacher_by_id(teacher_id: str):
    return get_db().teachers.find_one({"teacher_id": teacher_id})


def list_teachers_by_specialization(level: str):
    return list(get_db().teachers.find({"specialization": level}))
