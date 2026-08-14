"""
gui/materials.py
-----------------
Study Materials module: teachers/admin add materials (with a file
path reference) for each category and German level.
Full CRUD against the `study_materials` collection.
"""

from frontend.base import CRUDFrame


CATEGORIES = [
    "Vocabulary", "Grammar", "Reading", "Writing", "Listening", "Speaking",
    "A1 Materials", "A2 Materials", "B1 Materials", "B2 Materials",
]


class StudyMaterialFrame(CRUDFrame):
    title = "Study Materials"
    collection_name = "study_materials"
    id_field = "material_id"
    id_prefix = "MAT"
    counter_name = "material_id"
    auto_id = True

    fields = [
        {"key": "title", "label": "Title", "type": "entry", "required": True},
        {"key": "category", "label": "Category", "type": "combobox", "required": True,
         "options": CATEGORIES},
        {"key": "course", "label": "Course ID", "type": "entry", "required": False},
        {"key": "description", "label": "Description", "type": "entry", "required": False},
        {"key": "file_path", "label": "File Path", "type": "entry", "required": True},
        {"key": "uploaded_by", "label": "Uploaded By (ID)", "type": "entry", "required": True},
    ]

    columns = [
        ("material_id", "ID", 80),
        ("title", "Title", 150),
        ("category", "Category", 100),
        ("course", "Course", 70),
        ("file_path", "File Path", 180),
        ("uploaded_by", "Uploaded By", 90),
    ]

    def build_extra_filters(self, parent):
        import tkinter as tk
        from tkinter import ttk
        from backend import config
        wrapper = tk.Frame(parent, bg=config.THEME_COLOR_BG)
        tk.Label(wrapper, text="Category:", bg=config.THEME_COLOR_BG,
                 font=(config.FONT_FAMILY, 9)).pack(side="left")
        self.category_filter = tk.StringVar(value="All")
        combo = ttk.Combobox(wrapper, textvariable=self.category_filter, state="readonly",
                              width=14, values=["All"] + CATEGORIES)
        combo.pack(side="left", padx=4)
        combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        return wrapper

    def get_query(self):
        query = super().get_query()
        cat = getattr(self, "category_filter", None)
        if cat and cat.get() and cat.get() != "All":
            query["category"] = cat.get()
        return query
