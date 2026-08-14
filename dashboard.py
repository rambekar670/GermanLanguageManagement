"""
gui/dashboard.py
------------------
Main application window shown after a successful login. Provides:
    * A sidebar with navigation buttons (role-based: admin sees
      everything, teacher sees a restricted subset)
    * A "Dashboard" home view with live statistic cards
    * A content area that swaps between management modules

This is the central hub that wires every other GUI module together.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date

from backend import config
from backend.database import get_db
from backend.utils.helpers import show_success

from frontend.students import StudentManagementFrame
from frontend.teachers import TeacherManagementFrame
from frontend.courses import CourseManagementFrame
from frontend.batches import BatchManagementFrame
from frontend.attendance import AttendanceFrame
from frontend.fees import FeeManagementFrame
from frontend.assignments import AssignmentManagementFrame
from frontend.exams import ExaminationFrame
from frontend.results import ResultsFrame
from frontend.materials import StudyMaterialFrame
from frontend.announcements import AnnouncementFrame
from frontend.reports import ReportsFrame


class DashboardWindow(tk.Tk):
    def __init__(self, current_user, on_logout):
        super().__init__()
        self.current_user = current_user
        self.on_logout = on_logout
        self.db = get_db()

        self.title(f"{config.APP_NAME} - {current_user.get('role', '').title()} Dashboard")
        self.geometry("1200x720")
        self.minsize(1000, 620)
        self.configure(bg=config.THEME_COLOR_BG)

        self.current_frame = None
        self._build_ui()
        self.show_home()

    # ------------------------------------------------------------ layout
    def _build_ui(self):
        # ---- Sidebar ----
        sidebar = tk.Frame(self, bg=config.THEME_COLOR_PRIMARY, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="🇩🇪 " + config.APP_NAME, bg=config.THEME_COLOR_PRIMARY, fg="white",
            font=(config.FONT_FAMILY, 11, "bold"), wraplength=200, justify="left"
        ).pack(padx=15, pady=(20, 5), anchor="w")

        tk.Label(
            sidebar, text=f"Logged in as: {self.current_user.get('username')}\n"
                          f"Role: {self.current_user.get('role', '').title()}",
            bg=config.THEME_COLOR_PRIMARY, fg="#BDC3C7", font=(config.FONT_FAMILY, 8), justify="left"
        ).pack(padx=15, pady=(0, 15), anchor="w")

        is_admin = self.current_user.get("role") == "admin"

        nav_items = [
            ("Dashboard", self.show_home, True),
            ("Student Management", lambda: self.show_frame(StudentManagementFrame), is_admin),
            ("Teacher Management", lambda: self.show_frame(TeacherManagementFrame), is_admin),
            ("Course Management", lambda: self.show_frame(CourseManagementFrame), is_admin),
            ("Batch Management", lambda: self.show_frame(BatchManagementFrame), is_admin),
            ("Attendance", lambda: self.show_frame(AttendanceFrame), True),
            ("Fee Management", lambda: self.show_frame(FeeManagementFrame), is_admin),
            ("Assignment Management", lambda: self.show_frame(AssignmentManagementFrame), True),
            ("Examination", lambda: self.show_frame(ExaminationFrame), True),
            ("Results", lambda: self.show_frame(ResultsFrame), True),
            ("Study Materials", lambda: self.show_frame(StudyMaterialFrame), True),
            ("Announcements", lambda: self.show_frame(AnnouncementFrame), True),
            ("Reports", lambda: self.show_frame(ReportsFrame), is_admin),
            ("Logout", self._logout, True),
        ]

        for label, command, visible in nav_items:
            if not visible:
                continue
            is_logout = label == "Logout"
            btn = tk.Button(
                sidebar, text=label, anchor="w", bg=config.THEME_COLOR_WARNING if is_logout else config.THEME_COLOR_PRIMARY,
                fg="white", relief="flat", cursor="hand2", font=(config.FONT_FAMILY, 10),
                activebackground=config.THEME_COLOR_ACCENT, activeforeground="white",
                command=command, padx=15, pady=10
            )
            btn.pack(fill="x", pady=(20, 0) if is_logout else 0)
            if not is_logout:
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=config.THEME_COLOR_ACCENT))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=config.THEME_COLOR_PRIMARY))

        # ---- Content area ----
        self.content_area = tk.Frame(self, bg=config.THEME_COLOR_BG)
        self.content_area.pack(side="left", fill="both", expand=True)

    def show_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.content_area, self.current_user)
        self.current_frame.pack(fill="both", expand=True)

    def show_home(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = DashboardHomeFrame(self.content_area, self.current_user, self.db)
        self.current_frame.pack(fill="both", expand=True)

    def _logout(self):
        self.destroy()
        self.on_logout()


class DashboardHomeFrame(tk.Frame):
    """The statistics home page shown when 'Dashboard' is clicked."""

    def __init__(self, parent, current_user, db):
        super().__init__(parent, bg=config.THEME_COLOR_BG)
        self.db = db
        tk.Label(self, text=f"Welcome, {current_user.get('full_name') or current_user.get('username')} 👋",
                 font=(config.FONT_FAMILY, 20, "bold"), bg=config.THEME_COLOR_BG,
                 fg=config.THEME_COLOR_PRIMARY).pack(anchor="w", padx=25, pady=(20, 5))
        tk.Label(self, text=date.today().strftime("%A, %d %B %Y"), bg=config.THEME_COLOR_BG,
                 fg="#7F8C8D", font=(config.FONT_FAMILY, 10)).pack(anchor="w", padx=25, pady=(0, 15))

        self._build_cards()

    def _stat(self, label, query_fn, collection):
        try:
            return query_fn()
        except Exception:
            return "N/A"

    def _build_cards(self):
        today = date.today().isoformat()

        stats = [
            ("Total Students", self.db.students.count_documents({}), config.THEME_COLOR_ACCENT),
            ("Total Teachers", self.db.teachers.count_documents({}), "#8E44AD"),
            ("Total Courses", self.db.courses.count_documents({}), "#16A085"),
            ("Active Batches", self.db.batches.count_documents({"status": "Active"}), "#D35400"),
            ("Today's Attendance Marked", self.db.attendance.count_documents({"date": today}), "#2980B9"),
            ("Pending Fees", self.db.fees.count_documents({"payment_status": "Pending"}), config.THEME_COLOR_WARNING),
            ("Upcoming Exams", self.db.exams.count_documents({}), "#27AE60"),
            ("Announcements", self.db.announcements.count_documents({}), "#7F8C8D"),
        ]

        grid = tk.Frame(self, bg=config.THEME_COLOR_BG)
        grid.pack(fill="x", padx=15)

        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(grid, bg=color, width=260, height=100)
            card.grid(row=i // 4, column=i % 4, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            tk.Label(card, text=str(value), font=(config.FONT_FAMILY, 22, "bold"),
                     bg=color, fg="white").pack(anchor="w", padx=15, pady=(15, 0))
            tk.Label(card, text=label, font=(config.FONT_FAMILY, 10),
                     bg=color, fg="white").pack(anchor="w", padx=15)

        for col in range(4):
            grid.columnconfigure(col, weight=1)

        tk.Label(self, text="Use the sidebar to navigate to each management module.",
                 bg=config.THEME_COLOR_BG, fg="#95A5A6", font=(config.FONT_FAMILY, 9)).pack(
            anchor="w", padx=25, pady=20)
