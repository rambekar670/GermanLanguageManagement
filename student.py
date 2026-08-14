"""
models/student.py
------------------
Defines the expected shape of a student document, and small
helper functions for working with student records directly
(useful for scripts, tests, or other modules that need student
data without going through the GUI).
"""

from backend.database import get_db

STUDENT_SCHEMA_EXAMPLE = {
    "student_id": "STU0001",
    "full_name": "Anjali Sharma",
    "dob": "2001-05-14",
    "gender": "Female",
    "phone": "+919812345678",
    "email": "anjali.sharma@example.com",
    "address": "12 MG Road, Pune",
    "german_level": "A1",
    "course": "CRS0001",
    "batch": "BAT0001",
    "admission_date": "2026-01-10",
    "fees": 15000.0,
    "password": b"<bcrypt-hash>",
    "role": "student",
}


def get_student_by_id(student_id: str):
    return get_db().students.find_one({"student_id": student_id})


def list_students_by_level(level: str):
    return list(get_db().students.find({"german_level": level}))


def list_students_by_batch(batch_id: str):
    return list(get_db().students.find({"batch": batch_id}))
