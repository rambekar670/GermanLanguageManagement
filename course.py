"""
models/course.py
-----------------
Defines the expected shape of a course document, plus small
convenience lookup helpers.
"""

from backend.database import get_db

COURSE_SCHEMA_EXAMPLE = {
    "course_id": "CRS0001",
    "course_name": "German A1 - Beginner",
    "level": "A1",
    "duration": 8,          # weeks
    "fees": 12000.0,
    "teacher": "TCH0001",
    "batch": "BAT0001",
    "start_date": "2026-02-01",
    "end_date": "2026-03-28",
    "max_students": 20,
}


def get_course_by_id(course_id: str):
    return get_db().courses.find_one({"course_id": course_id})


def list_courses_by_level(level: str):
    return list(get_db().courses.find({"level": level}))
