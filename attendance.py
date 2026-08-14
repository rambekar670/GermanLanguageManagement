"""
gui/attendance.py
------------------
Attendance Management module.

Teacher/admin selects a course, batch and date, then marks each
enrolled student Present/Absent. The module automatically computes
each student's overall attendance percentage:

    Attendance % = (Present Days / Total Classes) * 100

and highlights (in red) any student whose percentage falls below
config.ATTENDANCE_WARNING_THRESHOLD (75%).

Collection: attendance
Document shape:
    {
        "course": "CRS0001", "batch": "BAT0001", "date": "2026-08-14",
        "student_id": "STU0001", "status": "Present" | "Absent",
        "marked_by": "TCH0001"
    }
"""

import tkinter as tk
from tkinter import ttk
from datetime import date

from backend import config
from backend.database import get_db
from backend.utils.helpers import show_error, show_success, show_warning, calculate_attendance_percentage


class AttendanceFrame(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg=config.THEME_COLOR_BG)
        self.current_user = current_user
        self.db = get_db()
        self.status_vars = {}  # student_id -> StringVar("Present"/"Absent")
        self._build_ui()

    # ------------------------------------------------------------ UI
    def _build_ui(self):
        tk.Label(self, text="Attendance Management", font=(config.FONT_FAMILY, 18, "bold"),
                  bg=config.THEME_COLOR_BG, fg=config.THEME_COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        mark_tab = tk.Frame(notebook, bg=config.THEME_COLOR_BG)
        report_tab = tk.Frame(notebook, bg=config.THEME_COLOR_BG)
        notebook.add(mark_tab, text="Mark Attendance")
        notebook.add(report_tab, text="Attendance Report")

        self._build_mark_tab(mark_tab)
        self._build_report_tab(report_tab)

    # -------------------------------------------------- mark attendance
    def _build_mark_tab(self, parent):
        filter_row = tk.Frame(parent, bg=config.THEME_COLOR_BG)
        filter_row.pack(fill="x", pady=10)

        tk.Label(filter_row, text="Course ID:", bg=config.THEME_COLOR_BG).pack(side="left")
        self.course_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.course_var, width=12).pack(side="left", padx=5)

        tk.Label(filter_row, text="Batch ID:", bg=config.THEME_COLOR_BG).pack(side="left")
        self.batch_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.batch_var, width=12).pack(side="left", padx=5)

        tk.Label(filter_row, text="Date (YYYY-MM-DD):", bg=config.THEME_COLOR_BG).pack(side="left")
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(filter_row, textvariable=self.date_var, width=14).pack(side="left", padx=5)

        tk.Button(filter_row, text="Load Students", bg=config.THEME_COLOR_ACCENT, fg="white",
                  relief="flat", command=self._load_students_for_batch).pack(side="left", padx=10)

        self.list_container = tk.Frame(parent, bg="white")
        self.list_container.pack(fill="both", expand=True, pady=10)

        tk.Button(parent, text="Save Attendance", bg=config.THEME_COLOR_SUCCESS, fg="white",
                  font=(config.FONT_FAMILY, 10, "bold"), relief="flat",
                  command=self._save_attendance).pack(pady=5)

    def _load_students_for_batch(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()
        self.status_vars.clear()

        batch = self.batch_var.get().strip()
        course = self.course_var.get().strip()
        if not batch:
            show_warning("Missing Batch", "Please enter a Batch ID to load students.")
            return

        query = {"batch": batch}
        if course:
            query["course"] = course
        students = list(self.db.students.find(query).sort("student_id", 1))

        if not students:
            tk.Label(self.list_container, text="No students found for this batch.",
                     bg="white", fg="#888888").pack(pady=20)
            return

        header = tk.Frame(self.list_container, bg="#ECF0F1")
        header.pack(fill="x")
        tk.Label(header, text="Student ID", width=15, bg="#ECF0F1", anchor="w",
                 font=(config.FONT_FAMILY, 9, "bold")).pack(side="left", padx=5, pady=4)
        tk.Label(header, text="Name", width=25, bg="#ECF0F1", anchor="w",
                 font=(config.FONT_FAMILY, 9, "bold")).pack(side="left")
        tk.Label(header, text="Status", width=15, bg="#ECF0F1", anchor="w",
                 font=(config.FONT_FAMILY, 9, "bold")).pack(side="left")

        for student in students:
            row = tk.Frame(self.list_container, bg="white")
            row.pack(fill="x")
            tk.Label(row, text=student["student_id"], width=15, bg="white", anchor="w").pack(side="left", padx=5, pady=3)
            tk.Label(row, text=student.get("full_name", ""), width=25, bg="white", anchor="w").pack(side="left")

            var = tk.StringVar(value="Present")
            combo = ttk.Combobox(row, textvariable=var, values=["Present", "Absent"],
                                  state="readonly", width=12)
            combo.pack(side="left")
            self.status_vars[student["student_id"]] = var

    def _save_attendance(self):
        batch = self.batch_var.get().strip()
        course = self.course_var.get().strip()
        att_date = self.date_var.get().strip()

        if not (batch and course and att_date):
            show_warning("Missing Information", "Course, Batch and Date are required.")
            return
        if not self.status_vars:
            show_warning("Nothing to Save", "Load students for a batch first.")
            return

        try:
            for student_id, var in self.status_vars.items():
                self.db.attendance.update_one(
                    {"course": course, "batch": batch, "date": att_date, "student_id": student_id},
                    {"$set": {
                        "course": course, "batch": batch, "date": att_date,
                        "student_id": student_id, "status": var.get(),
                        "marked_by": self.current_user.get("username", "system"),
                    }},
                    upsert=True,
                )
        except Exception as exc:
            show_error("Database Error", f"Could not save attendance.\n{exc}")
            return

        show_success("Saved", f"Attendance saved for {len(self.status_vars)} students on {att_date}.")

    # -------------------------------------------------- report
    def _build_report_tab(self, parent):
        filter_row = tk.Frame(parent, bg=config.THEME_COLOR_BG)
        filter_row.pack(fill="x", pady=10)

        tk.Label(filter_row, text="Batch ID (optional):", bg=config.THEME_COLOR_BG).pack(side="left")
        self.report_batch_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.report_batch_var, width=14).pack(side="left", padx=5)

        tk.Button(filter_row, text="Generate Report", bg=config.THEME_COLOR_ACCENT, fg="white",
                  relief="flat", command=self._generate_report).pack(side="left", padx=10)

        columns = ("student_id", "full_name", "present", "total", "percentage")
        self.report_tree = ttk.Treeview(parent, columns=columns, show="headings")
        headers = {"student_id": "Student ID", "full_name": "Name", "present": "Present",
                   "total": "Total Classes", "percentage": "Attendance %"}
        for col in columns:
            self.report_tree.heading(col, text=headers[col])
            self.report_tree.column(col, width=130, anchor="w")
        self.report_tree.pack(fill="both", expand=True, pady=10)
        self.report_tree.tag_configure("warning", background="#FADBD8")

    def _generate_report(self):
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)

        batch = self.report_batch_var.get().strip()
        student_query = {"batch": batch} if batch else {}
        students = list(self.db.students.find(student_query))

        for student in students:
            att_query = {"student_id": student["student_id"]}
            if batch:
                att_query["batch"] = batch
            records = list(self.db.attendance.find(att_query))
            total = len(records)
            present = sum(1 for r in records if r.get("status") == "Present")
            pct = calculate_attendance_percentage(present, total)

            tags = ("warning",) if pct < config.ATTENDANCE_WARNING_THRESHOLD and total > 0 else ()
            self.report_tree.insert("", "end", values=(
                student["student_id"], student.get("full_name", ""), present, total, f"{pct}%"
            ), tags=tags)
