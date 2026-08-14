"""
auth/login.py
--------------
Login window for the German Language Class Management System.
Authenticates against the `users` collection in MongoDB. Passwords
are verified with bcrypt (never stored or compared as plain text).
"""

import tkinter as tk
from tkinter import ttk

from backend import config
from backend.database import get_db
from backend.utils.helpers import check_password, show_error, show_warning


class LoginWindow(tk.Tk):
    """
    On successful login, calls `on_success(user_doc)` and destroys itself.
    `on_success` is provided by main.py and is responsible for opening
    the dashboard for the correct role (admin / teacher).
    """

    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        self.title(f"{config.APP_NAME} - Login")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg=config.THEME_COLOR_BG)
        self.eval('tk::PlaceWindow . center')

        self._build_ui()

    # ------------------------------------------------------------ UI
    def _build_ui(self):
        header = tk.Frame(self, bg=config.THEME_COLOR_PRIMARY, height=120)
        header.pack(fill="x")
        tk.Label(
            header, text="🇩🇪", font=(config.FONT_FAMILY, 36),
            bg=config.THEME_COLOR_PRIMARY, fg="white"
        ).pack(pady=(15, 0))
        tk.Label(
            header, text=config.APP_NAME, font=(config.FONT_FAMILY, 13, "bold"),
            bg=config.THEME_COLOR_PRIMARY, fg="white", wraplength=380, justify="center"
        ).pack(pady=(0, 10))

        form = tk.Frame(self, bg=config.THEME_COLOR_BG, padx=40, pady=30)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Username", bg=config.THEME_COLOR_BG,
                 font=(config.FONT_FAMILY, 10)).pack(anchor="w")
        self.username_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.username_var, font=(config.FONT_FAMILY, 11)).pack(
            fill="x", pady=(2, 15))

        tk.Label(form, text="Password", bg=config.THEME_COLOR_BG,
                 font=(config.FONT_FAMILY, 10)).pack(anchor="w")
        self.password_var = tk.StringVar()
        pw_entry = ttk.Entry(form, textvariable=self.password_var, show="*",
                              font=(config.FONT_FAMILY, 11))
        pw_entry.pack(fill="x", pady=(2, 5))

        self.show_pw_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form, text="Show password", variable=self.show_pw_var,
            command=lambda: pw_entry.config(show="" if self.show_pw_var.get() else "*")
        ).pack(anchor="w", pady=(0, 20))

        login_btn = tk.Button(
            form, text="Login", bg=config.THEME_COLOR_ACCENT, fg="white",
            font=(config.FONT_FAMILY, 11, "bold"), relief="flat", cursor="hand2",
            command=self._attempt_login
        )
        login_btn.pack(fill="x", ipady=8)

        tk.Label(
            form, text="Default admin login: admin / admin123",
            bg=config.THEME_COLOR_BG, fg="#888888", font=(config.FONT_FAMILY, 8)
        ).pack(pady=(15, 0))

        self.bind("<Return>", lambda e: self._attempt_login())
        pw_entry.focus_set()

    # ------------------------------------------------------------ logic
    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            show_warning("Missing information", "Please enter both username and password.")
            return

        try:
            db = get_db()
        except ConnectionError as exc:
            show_error("Database Error", str(exc))
            return

        user = db.users.find_one({"username": username})
        if not user or not check_password(password, user["password"]):
            show_error("Invalid Login", "Incorrect username or password.")
            return

        self.destroy()
        self.on_success(user)
