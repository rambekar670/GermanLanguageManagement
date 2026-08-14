"""
reports/reports.py
--------------------
Reports module: visual summaries built from live MongoDB data using
Matplotlib embedded inside a Tkinter frame:
    * Students per German level (bar chart)
    * Fee status breakdown (pie chart)
    * Pass/Fail ratio (pie chart)
Also has a raw text summary table.
"""

import tkinter as tk
from tkinter import ttk
from collections import Counter

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend import config
from backend.database import get_db
from backend.utils.helpers import show_error


class ReportsFrame(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg=config.THEME_COLOR_BG)
        self.current_user = current_user
        self.db = get_db()
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Reports", font=(config.FONT_FAMILY, 18, "bold"),
                  bg=config.THEME_COLOR_BG, fg=config.THEME_COLOR_PRIMARY).pack(anchor="w", padx=20, pady=(15, 5))

        tk.Button(self, text="Refresh Reports", bg=config.THEME_COLOR_ACCENT, fg="white",
                  relief="flat", command=self.render_charts).pack(anchor="w", padx=20)

        self.charts_container = tk.Frame(self, bg=config.THEME_COLOR_BG)
        self.charts_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.render_charts()

    def render_charts(self):
        for widget in self.charts_container.winfo_children():
            widget.destroy()

        try:
            students = list(self.db.students.find())
            fees = list(self.db.fees.find())
            results = list(self.db.results.find())
        except Exception as exc:
            show_error("Database Error", f"Could not load report data.\n{exc}")
            return

        fig = Figure(figsize=(11, 4), dpi=100)

        # Chart 1: Students per level
        ax1 = fig.add_subplot(131)
        level_counts = Counter(s.get("german_level", "Unknown") for s in students)
        levels = config.GERMAN_LEVELS
        counts = [level_counts.get(lvl, 0) for lvl in levels]
        ax1.bar(levels, counts, color=config.THEME_COLOR_ACCENT)
        ax1.set_title("Students per Level")

        # Chart 2: Fee status breakdown
        ax2 = fig.add_subplot(132)
        status_counts = Counter(f.get("payment_status", "Unknown") for f in fees)
        if status_counts:
            ax2.pie(status_counts.values(), labels=status_counts.keys(), autopct="%1.0f%%",
                    colors=["#27AE60", "#F39C12", "#E74C3C"])
        ax2.set_title("Fee Status")

        # Chart 3: Pass/Fail ratio
        ax3 = fig.add_subplot(133)
        result_counts = Counter(r.get("result", "Unknown") for r in results)
        if result_counts:
            ax3.pie(result_counts.values(), labels=result_counts.keys(), autopct="%1.0f%%",
                    colors=["#27AE60", "#E74C3C"])
        ax3.set_title("Pass / Fail Ratio")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.charts_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # ---- Text summary table ----
        summary_frame = tk.LabelFrame(self.charts_container, text="Summary", bg="white",
                                       font=(config.FONT_FAMILY, 10, "bold"))
        summary_frame.pack(fill="x", pady=10)

        total_fees_due = sum(f.get("remaining_amount", 0) for f in fees)
        pending_count = sum(1 for f in fees if f.get("payment_status") == "Pending")

        lines = [
            f"Total Students: {len(students)}",
            f"Total Fee Records: {len(fees)}   |   Pending Payments: {pending_count}   |   "
            f"Total Amount Due: {total_fees_due:.2f}",
            f"Total Exam Results Recorded: {len(results)}",
        ]
        for line in lines:
            tk.Label(summary_frame, text=line, bg="white", anchor="w",
                     font=(config.FONT_FAMILY, 9)).pack(fill="x", padx=10, pady=2)
