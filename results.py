"""
gui/results.py
----------------
Results module: a read-only, filterable view over the `results`
collection (which is kept in sync automatically whenever a teacher
saves an exam entry in gui/exams.py). Admin/teachers can filter by
German level, course, or Pass/Fail.
"""

import tkinter as tk
from tkinter import ttk

from backend import config
from backend.database import get_db
from backend.utils.helpers import show_error


class ResultsFrame(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg=config.THEME_COLOR_BG)
        self.current_user = current_user
        self.db = get_db()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        tk.Label(self, text="Results", font=(config.FONT_FAMILY, 18, "bold"),
                  bg=config.THEME_COLOR_BG, fg=config.THEME_COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))

        filter_row = tk.Frame(self, bg=config.THEME_COLOR_BG)
        filter_row.pack(fill="x", padx=20, pady=5)

        tk.Label(filter_row, text="Level:", bg=config.THEME_COLOR_BG).pack(side="left")
        self.level_var = tk.StringVar(value="All")
        ttk.Combobox(filter_row, textvariable=self.level_var, state="readonly", width=8,
                     values=["All"] + config.GERMAN_LEVELS).pack(side="left", padx=5)

        tk.Label(filter_row, text="Result:", bg=config.THEME_COLOR_BG).pack(side="left")
        self.result_var = tk.StringVar(value="All")
        ttk.Combobox(filter_row, textvariable=self.result_var, state="readonly", width=8,
                     values=["All", "Pass", "Fail"]).pack(side="left", padx=5)

        tk.Label(filter_row, text="Student ID:", bg=config.THEME_COLOR_BG).pack(side="left")
        self.student_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.student_var, width=14).pack(side="left", padx=5)

        tk.Button(filter_row, text="Apply Filters", bg=config.THEME_COLOR_ACCENT, fg="white",
                  relief="flat", command=self.refresh).pack(side="left", padx=10)

        columns = ("result_id", "student_id", "student_name", "exam_name", "german_level",
                   "total_marks", "percentage", "grade", "result")
        headers = {
            "result_id": "Result ID", "student_id": "Student ID", "student_name": "Name",
            "exam_name": "Exam", "german_level": "Level", "total_marks": "Total",
            "percentage": "%", "grade": "Grade", "result": "Result",
        }
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=110, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.tag_configure("fail", background="#FADBD8")
        self.tree.tag_configure("pass", background="#D5F5E3")

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = {}
        if self.level_var.get() != "All":
            query["german_level"] = self.level_var.get()
        if self.result_var.get() != "All":
            query["result"] = self.result_var.get()
        if self.student_var.get().strip():
            query["student_id"] = self.student_var.get().strip()

        try:
            docs = list(self.db.results.find(query))
        except Exception as exc:
            show_error("Database Error", f"Could not load results.\n{exc}")
            return

        for doc in docs:
            tag = "pass" if doc.get("result") == "Pass" else "fail"
            self.tree.insert("", "end", values=(
                doc.get("result_id", ""), doc.get("student_id", ""), doc.get("student_name", ""),
                doc.get("exam_name", ""), doc.get("german_level", ""), doc.get("total_marks", ""),
                doc.get("percentage", ""), doc.get("grade", ""), doc.get("result", ""),
            ), tags=(tag,))
