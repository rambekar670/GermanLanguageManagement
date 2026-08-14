"""
utils/helpers.py
-----------------
Small utility functions shared across the app: password hashing,
ID generation, grade calculation, and Tkinter message-box shortcuts.
"""

import bcrypt
from tkinter import messagebox
from backend import config
from backend.database import get_next_sequence


# ---------------------------------------------------------------- passwords
def hash_password(plain_password: str) -> bytes:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())


def check_password(plain_password: str, hashed: bytes) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------- IDs
def generate_id(prefix: str, counter_name: str) -> str:
    """e.g. generate_id('STU', 'student_id') -> 'STU0007'"""
    seq = get_next_sequence(counter_name)
    return f"{prefix}{seq:04d}"


# ---------------------------------------------------------------- grading
def calculate_grade(percentage: float) -> str:
    for low, high, grade in config.GRADE_TABLE:
        if low <= percentage < high:
            return grade
    return "Fail"


def calculate_result(percentage: float) -> str:
    return "Pass" if percentage >= 50 else "Fail"


# ---------------------------------------------------------------- fees
def calculate_fee_status(total_fees: float, paid_amount: float) -> str:
    if paid_amount <= 0:
        return "Pending"
    if paid_amount >= total_fees:
        return "Paid"
    return "Partially Paid"


# ---------------------------------------------------------------- attendance
def calculate_attendance_percentage(present_days: int, total_classes: int) -> float:
    if total_classes <= 0:
        return 0.0
    return round((present_days / total_classes) * 100, 2)


# ---------------------------------------------------------------- messages
def show_error(title: str, message: str):
    messagebox.showerror(title, message)


def show_success(title: str, message: str):
    messagebox.showinfo(title, message)


def show_warning(title: str, message: str):
    messagebox.showwarning(title, message)


def confirm(title: str, message: str) -> bool:
    return messagebox.askyesno(title, message)
