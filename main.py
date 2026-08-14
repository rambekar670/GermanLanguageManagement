"""
main.py
-------
Entry point for the German Language Class Management System.

Run with:
    python main.py

Flow:
    1. Connect to MongoDB, create indexes, seed the default admin user.
    2. Show the Login window.
    3. On successful login, open the Dashboard window for that user's role.
    4. On logout, return to the Login window (loop until the app is closed).
"""

import sys
import tkinter as tk
from tkinter import messagebox

from backend.database import get_db, init_indexes, seed_admin_user
from frontend.login_window import LoginWindow
from frontend.dashboard import DashboardWindow


def start_app():
    try:
        get_db()
        init_indexes()
        seed_admin_user()
    except ConnectionError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Database Connection Failed", str(exc))
        root.destroy()
        sys.exit(1)

    open_login()


def open_login():
    def on_success(user_doc):
        open_dashboard(user_doc)

    login_window = LoginWindow(on_success)
    login_window.mainloop()


def open_dashboard(user_doc):
    def on_logout():
        open_login()

    dashboard = DashboardWindow(user_doc, on_logout)
    dashboard.mainloop()


if __name__ == "__main__":
    start_app()
