"""
database.py
-----------
Handles the MongoDB connection (via PyMongo) for the whole application.
Every GUI module imports `get_db()` from here to talk to MongoDB.

Collections used (all inside the `german_language_management` database):
    users, students, teachers, courses, batches, attendance,
    fees, assignments, exams, results, study_materials, announcements
"""

from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend import config

_client = None
_db = None


def get_client():
    """Return a singleton MongoClient, creating it if needed."""
    global _client
    if _client is None:
        _client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    """Return the application database, verifying the connection first."""
    global _db
    if _db is None:
        client = get_client()
        try:
            # Force a round trip so connection errors surface immediately.
            client.admin.command("ping")
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            raise ConnectionError(
                "Could not connect to MongoDB. Make sure MongoDB is running "
                f"at {config.MONGO_URI}.\nOriginal error: {exc}"
            )
        _db = client[config.DATABASE_NAME]
    return _db


def init_indexes():
    """Create unique indexes so duplicate IDs are rejected by MongoDB itself."""
    db = get_db()
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.students.create_index([("student_id", ASCENDING)], unique=True)
    db.teachers.create_index([("teacher_id", ASCENDING)], unique=True)
    db.courses.create_index([("course_id", ASCENDING)], unique=True)
    db.batches.create_index([("batch_id", ASCENDING)], unique=True)


def seed_admin_user():
    """
    Create a default admin account (username: admin / password: admin123)
    the first time the app is run, so there is always a way to log in.
    """
    from backend.utils.helpers import hash_password

    db = get_db()
    if db.users.count_documents({"username": "admin"}) == 0:
        db.users.insert_one({
            "username": "admin",
            "password": hash_password("admin123"),
            "role": "admin",
            "full_name": "System Administrator",
            "linked_id": None,
        })


def get_next_sequence(counter_name: str) -> int:
    """
    Atomically get the next number for human-friendly IDs
    (e.g. STU0001, TCH0001, CRS0001, BAT0001).
    Uses a `counters` collection so IDs never collide, even with
    simultaneous inserts.
    """
    db = get_db()
    doc = db.counters.find_one_and_update(
        {"_id": counter_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return doc["seq"]
