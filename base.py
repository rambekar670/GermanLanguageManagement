"""
gui/base.py
-----------
A reusable CRUD frame used as the base class for most management
modules (Students, Teachers, Courses, Batches, Assignments,
Study Materials, Announcements). It provides:

    * A form (left) built from a field specification
    * A Treeview table (right) showing all records
    * Add / Update / Delete / Clear / Search buttons
    * Automatic MongoDB CRUD via PyMongo
    * Automatic human-readable ID generation

Each concrete module (e.g. gui/students.py) subclasses `CRUDFrame`
and only needs to describe its fields - it does not need to
re-implement Add/Update/Delete/Search logic.
"""

import tkinter as tk
from tkinter import ttk

from backend import config
from backend.database import get_db
from backend.utils.helpers import generate_id, show_error, show_success, show_warning, confirm
from backend.utils.validation import validate_fields, not_empty


class CRUDFrame(tk.Frame):
    """
    Subclasses must set these class attributes:
        title            : str  - heading shown at the top
        collection_name  : str  - MongoDB collection to use
        id_field         : str  - the field that uniquely identifies a record
        id_prefix        : str  - prefix for auto-generated IDs, e.g. "STU"
        counter_name     : str  - name of the counter sequence, e.g. "student_id"
        auto_id          : bool - if True, the ID field is generated automatically
        fields           : list of dicts describing each form field:
            {"key": "full_name", "label": "Full Name", "type": "entry",
             "required": True, "validators": [...]}
            type can be "entry", "combobox", "date", "password", "readonly"
        columns          : list of (key, header, width) shown in the Treeview

    Subclasses may override:
        build_document(values) -> dict     to add computed fields
        on_row_selected(doc)                to react to selection
    """

    title = "Management"
    collection_name = None
    id_field = "id"
    id_prefix = "REC"
    counter_name = "generic"
    auto_id = True
    fields = []
    columns = []

    def __init__(self, parent, current_user):
        super().__init__(parent, bg=config.THEME_COLOR_BG)
        self.current_user = current_user
        self.db = get_db()
        self.collection = self.db[self.collection_name]
        self.entries = {}
        self.selected_doc_id = None  # ObjectId of currently selected row (for update/delete)

        self._build_ui()
        self.refresh_table()

    # ------------------------------------------------------------ UI
    def _build_ui(self):
        tk.Label(
            self, text=self.title, font=(config.FONT_FAMILY, 18, "bold"),
            bg=config.THEME_COLOR_BG, fg=config.THEME_COLOR_PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 5))

        body = tk.Frame(self, bg=config.THEME_COLOR_BG)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # ---- Left: form ----
        form_container = tk.LabelFrame(
            body, text="Details", bg="white", fg=config.THEME_COLOR_PRIMARY,
            font=(config.FONT_FAMILY, 10, "bold"), padx=15, pady=15
        )
        form_container.pack(side="left", fill="y", padx=(0, 15))

        for field in self.fields:
            row = tk.Frame(form_container, bg="white")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=field["label"], width=16, anchor="w",
                     bg="white", font=(config.FONT_FAMILY, 9)).pack(side="left")

            ftype = field.get("type", "entry")
            if ftype == "combobox":
                var = tk.StringVar()
                widget = ttk.Combobox(row, textvariable=var, values=field.get("options", []),
                                       state="readonly", width=22)
                widget.pack(side="left")
            elif ftype == "password":
                var = tk.StringVar()
                widget = ttk.Entry(row, textvariable=var, width=24, show="*")
                widget.pack(side="left")
            elif ftype == "readonly":
                var = tk.StringVar()
                widget = ttk.Entry(row, textvariable=var, width=24, state="readonly")
                widget.pack(side="left")
            else:  # plain entry / date (date typed as free text YYYY-MM-DD to avoid extra deps)
                var = tk.StringVar()
                widget = ttk.Entry(row, textvariable=var, width=24)
                widget.pack(side="left")

            self.entries[field["key"]] = {"var": var, "widget": widget, "spec": field}

        btn_row = tk.Frame(form_container, bg="white")
        btn_row.pack(fill="x", pady=(15, 0))

        self._make_button(btn_row, "Add", config.THEME_COLOR_ACCENT, self.on_add).pack(fill="x", pady=2)
        self._make_button(btn_row, "Update", "#8E44AD", self.on_update).pack(fill="x", pady=2)
        self._make_button(btn_row, "Delete", config.THEME_COLOR_WARNING, self.on_delete).pack(fill="x", pady=2)
        self._make_button(btn_row, "Clear Form", "#7F8C8D", self.clear_form).pack(fill="x", pady=2)

        # ---- Right: search + table ----
        right = tk.Frame(body, bg=config.THEME_COLOR_BG)
        right.pack(side="left", fill="both", expand=True)

        search_row = tk.Frame(right, bg=config.THEME_COLOR_BG)
        search_row.pack(fill="x", pady=(0, 8))
        tk.Label(search_row, text="Search:", bg=config.THEME_COLOR_BG,
                 font=(config.FONT_FAMILY, 9)).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=6)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())
        self._make_button(search_row, "Refresh", config.THEME_COLOR_ACCENT,
                           self.refresh_table, small=True).pack(side="left", padx=4)

        extra = self.build_extra_filters(search_row)
        if extra:
            extra.pack(side="left", padx=10)

        table_frame = tk.Frame(right, bg=config.THEME_COLOR_BG)
        table_frame.pack(fill="both", expand=True)

        col_keys = [c[0] for c in self.columns]
        self.tree = ttk.Treeview(table_frame, columns=col_keys, show="headings", selectmode="browse")
        for key, header, width in self.columns:
            self.tree.heading(key, text=header)
            self.tree.column(key, width=width, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.tag_configure("warning", background="#FADBD8")

    def _make_button(self, parent, text, color, command, small=False):
        return tk.Button(
            parent, text=text, bg=color, fg="white", relief="flat", cursor="hand2",
            font=(config.FONT_FAMILY, 9 if small else 10, "bold"), command=command,
            padx=8, pady=4 if small else 6
        )

    def build_extra_filters(self, parent):
        """Subclasses may override to add extra filter widgets next to Search."""
        return None

    # ------------------------------------------------------------ data helpers
    def get_form_values(self):
        return {key: data["var"].get().strip() for key, data in self.entries.items()}

    def set_form_values(self, doc):
        for key, data in self.entries.items():
            data["var"].set(str(doc.get(key, "")))

    def clear_form(self, *_):
        for data in self.entries.values():
            data["var"].set("")
        self.selected_doc_id = None
        self.tree.selection_remove(self.tree.selection())

    def validate_form(self, values):
        rules = []
        for field in self.fields:
            if field.get("required"):
                rules.append((values.get(field["key"], ""), not_empty, field["label"]))
            for extra_validator in field.get("validators", []):
                rules.append((values.get(field["key"], ""), extra_validator))
        return validate_fields(rules)

    def build_document(self, values):
        """Override in subclasses to add computed / derived fields."""
        return dict(values)

    def on_row_selected(self, doc):
        """Override in subclasses to react when a row is selected."""
        pass

    # ------------------------------------------------------------ CRUD actions
    def on_add(self):
        values = self.get_form_values()

        if self.auto_id:
            values[self.id_field] = generate_id(self.id_prefix, self.counter_name)

        ok, msg = self.validate_form(values)
        if not ok:
            show_warning("Validation Error", msg)
            return

        if self.collection.find_one({self.id_field: values[self.id_field]}):
            show_error("Duplicate Entry", f"{self.id_field} '{values[self.id_field]}' already exists.")
            return

        document = self.build_document(values)
        try:
            self.collection.insert_one(document)
        except Exception as exc:
            show_error("Database Error", f"Could not save record.\n{exc}")
            return

        show_success("Success", f"{self.title[:-11] if self.title.endswith('Management') else self.title} record added.")
        self.clear_form()
        self.refresh_table()

    def on_update(self):
        if not self.selected_doc_id:
            show_warning("No Selection", "Please select a record from the table to update.")
            return

        values = self.get_form_values()
        ok, msg = self.validate_form(values)
        if not ok:
            show_warning("Validation Error", msg)
            return

        document = self.build_document(values)
        document.pop(self.id_field, None)  # never change the primary ID on update
        try:
            self.collection.update_one({"_id": self.selected_doc_id}, {"$set": document})
        except Exception as exc:
            show_error("Database Error", f"Could not update record.\n{exc}")
            return

        show_success("Success", "Record updated successfully.")
        self.clear_form()
        self.refresh_table()

    def on_delete(self):
        if not self.selected_doc_id:
            show_warning("No Selection", "Please select a record from the table to delete.")
            return
        if not confirm("Confirm Delete", "Are you sure you want to delete this record?"):
            return
        try:
            self.collection.delete_one({"_id": self.selected_doc_id})
        except Exception as exc:
            show_error("Database Error", f"Could not delete record.\n{exc}")
            return
        show_success("Deleted", "Record deleted successfully.")
        self.clear_form()
        self.refresh_table()

    def _on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        doc_id = item["tags"][-1] if item["tags"] else None
        # last tag is always the hex string of the ObjectId (see refresh_table)
        from bson import ObjectId
        doc = self.collection.find_one({"_id": ObjectId(doc_id)})
        if not doc:
            return
        self.selected_doc_id = doc["_id"]
        self.set_form_values(doc)
        self.on_row_selected(doc)

    def get_query(self):
        """Override to change the base Mongo query (e.g. filter by teacher)."""
        search_term = self.search_var.get().strip()
        if not search_term:
            return {}
        or_clauses = []
        for field in self.fields:
            or_clauses.append({field["key"]: {"$regex": search_term, "$options": "i"}})
        return {"$or": or_clauses} if or_clauses else {}

    def row_values(self, doc):
        return [doc.get(c[0], "") for c in self.columns]

    def row_tags(self, doc):
        return []

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            docs = list(self.collection.find(self.get_query()))
        except Exception as exc:
            show_error("Database Error", f"Could not load records.\n{exc}")
            return
        for doc in docs:
            tags = list(self.row_tags(doc)) + [str(doc["_id"])]
            self.tree.insert("", "end", values=self.row_values(doc), tags=tags)
