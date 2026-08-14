"""
utils/validation.py
--------------------
Reusable validation helpers used by every GUI form in the project.
Each function returns (is_valid: bool, message: str).
"""

import re
from datetime import datetime

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")


def not_empty(value: str, field_name: str = "Field"):
    if value is None or str(value).strip() == "":
        return False, f"{field_name} cannot be empty."
    return True, ""


def valid_email(value: str):
    if not value or not EMAIL_REGEX.match(value.strip()):
        return False, "Please enter a valid email address."
    return True, ""


def valid_phone(value: str):
    if not value or not PHONE_REGEX.match(value.strip()):
        return False, "Please enter a valid phone number (7-15 digits)."
    return True, ""


def valid_number(value: str, field_name: str = "Value", allow_float=True, min_value=None, max_value=None):
    try:
        num = float(value) if allow_float else int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number."
    if min_value is not None and num < min_value:
        return False, f"{field_name} must be at least {min_value}."
    if max_value is not None and num > max_value:
        return False, f"{field_name} must be at most {max_value}."
    return True, ""


def valid_date(value: str, fmt: str = "%Y-%m-%d"):
    try:
        datetime.strptime(value, fmt)
    except (ValueError, TypeError):
        return False, "Please enter a valid date (YYYY-MM-DD)."
    return True, ""


def validate_fields(rules):
    """
    rules: list of tuples (value, validator_fn, *extra_args)
    Runs each validator in order and stops at the first failure.
    Returns (True, "") if everything passes, otherwise (False, message).
    """
    for rule in rules:
        value, validator = rule[0], rule[1]
        extra = rule[2:]
        ok, msg = validator(value, *extra)
        if not ok:
            return False, msg
    return True, ""
