"""
config.py
---------
Central configuration for the German Language Class Management System.
Edit MONGO_URI if your MongoDB server is not running on localhost,
or if you are using MongoDB Atlas (cloud).
"""

# ---- MongoDB connection settings ----
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "german_language_management"

# ---- Application settings ----
APP_NAME = "German Language Class Management System"
APP_VERSION = "1.0.0"

# ---- Theme / GUI settings ----
THEME_COLOR_PRIMARY = "#2C3E50"      # dark slate (sidebar)
THEME_COLOR_ACCENT = "#2980B9"       # blue (buttons/highlights)
THEME_COLOR_SUCCESS = "#27AE60"      # green
THEME_COLOR_WARNING = "#E74C3C"      # red
THEME_COLOR_BG = "#F4F6F7"           # light background
FONT_FAMILY = "Segoe UI"

# ---- Business rules ----
ATTENDANCE_WARNING_THRESHOLD = 75.0  # % below which a student is flagged
GERMAN_LEVELS = ["A1", "A2", "B1", "B2"]

GRADE_TABLE = [
    (90, 101, "A+"),
    (80, 90, "A"),
    (70, 80, "B"),
    (60, 70, "C"),
    (50, 60, "D"),
    (0, 50, "Fail"),
]
