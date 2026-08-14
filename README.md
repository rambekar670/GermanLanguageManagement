# German Language Class Management System
Python (Tkinter) + MongoDB (PyMongo) — Desktop GUI Application

A complete desktop application for managing a German language institute:
students, teachers, courses, batches, attendance, fees, exams, results,
study materials, announcements, and reports — all backed by a real
MongoDB database (no web browser, no Flask/Django).

The project is split into a clear **backend** (data + business logic)
and **frontend** (Tkinter GUI) so the two concerns stay independent —
you could swap the frontend for a different GUI toolkit later without
touching the backend at all.

---

## 1. Project Structure

```
GermanLanguageManagement/
│
├── main.py                    # Entry point — run this file
├── requirements.txt
├── README.md
│
├── backend/                    # ---- Data & business logic (no GUI code) ----
│   ├── __init__.py
│   ├── config.py                 # Central settings (Mongo URI, theme constants, grading rules)
│   ├── database.py               # MongoDB connection, indexes, ID counters, admin seeding
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py              # Student schema + lookup helpers
│   │   ├── teacher.py              # Teacher schema + lookup helpers
│   │   └── course.py               # Course schema + lookup helpers
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validation.py           # Field validators (email, phone, dates, numbers)
│       └── helpers.py              # Password hashing, ID generation, grading, fee/attendance math
│
└── frontend/                   # ---- Tkinter GUI (talks to backend only) ----
    ├── __init__.py
    ├── login_window.py           # Login window (calls backend for auth)
    ├── base.py                   # Reusable CRUD frame (Add/Update/Delete/Search/Table)
    ├── dashboard.py               # Main window: sidebar + stat cards
    ├── students.py                # Student Management (CRUD)
    ├── teachers.py                # Teacher Management (CRUD)
    ├── courses.py                 # Course Management (CRUD)
    ├── batches.py                 # Batch Management (CRUD)
    ├── attendance.py              # Mark attendance + % report
    ├── fees.py                    # Fee Management (auto remaining/status)
    ├── exams.py                   # Examination entry (auto total/%/grade)
    ├── results.py                 # Results browser (filter by level/result)
    ├── assignments.py             # Assignment Management (CRUD)
    ├── materials.py               # Study Materials (CRUD, by category)
    ├── announcements.py           # Announcements (CRUD)
    └── reports.py                 # Matplotlib charts + summary (Reports module)
```

**Rule of thumb used throughout the code:** `frontend/` only imports
from `backend/` (never the other way around), and `frontend/` never
touches PyMongo directly except through `backend.database.get_db()`.
Every frontend file's imports look like:

```python
from backend import config
from backend.database import get_db
from backend.utils.helpers import ...
from backend.utils.validation import ...
from frontend.base import CRUDFrame   # for CRUD modules that build on the shared frame
```

---

## 2. Step 1 — Install Python Libraries

You need **Python 3.9+**. From the project root:

```bash
pip install -r requirements.txt
```

This installs: `pymongo`, `bcrypt`, `matplotlib`, `ttkbootstrap`, `tkcalendar`.
(Tkinter itself ships with standard Python on Windows/macOS; on Linux install
it separately if needed: `sudo apt install python3-tk`.)

---

## 3. Step 2 — MongoDB Setup

Install MongoDB Community Server:
- Windows/macOS: https://www.mongodb.com/try/download/community
- Linux: `sudo apt install mongodb` (or follow MongoDB's official repo instructions)

Start the MongoDB service:
```bash
# Windows: MongoDB usually runs as a service automatically after install
# macOS (Homebrew):
brew services start mongodb-community
# Linux:
sudo systemctl start mongod
```

Verify it's running on the default port `27017` (matches
`backend/config.py`'s `MONGO_URI`). No manual database/collection
creation is needed — PyMongo creates the database and collections
automatically the first time a document is inserted.

If you use MongoDB Atlas (cloud) instead, replace `MONGO_URI` in
`backend/config.py` with your Atlas connection string.

---

## 4. Step 3 — Run the Application

From the project root (so `backend` and `frontend` are importable as packages):

```bash
python main.py
```

A login window opens. **Default admin account** (created automatically
on first run):

```
Username: admin
Password: admin123
```

Log in, then use the sidebar to navigate to each module.

### Creating Teacher Login Accounts

Note: `Teacher Management` stores teacher records (with a hashed
password field) in the `teachers` collection, but for a teacher to
actually **log in**, an entry must also exist in `users` linking to
that teacher. As a quick way to enable this for your project demo,
insert a document like this into `users` (via `mongosh` or a Python
one-off script), using the same password you set for the teacher:

```javascript
db.users.insertOne({
  username: "tch0001",              // pick any login username
  password: <same-bcrypt-hash-as-teacher-doc>,
  role: "teacher",
  full_name: "Markus Weber",
  linked_id: "TCH0001"
})
```

(This mirrors real institute practice: HR/admin issues login credentials
separately from the teacher's HR profile.)

---

## 5. MongoDB Database & Collections

**Database name:** `german_language_management`

| Collection | Purpose |
|---|---|
| `users` | Login credentials (admin/teacher), bcrypt-hashed passwords |
| `students` | Student profiles |
| `teachers` | Teacher profiles |
| `courses` | German courses (A1–B2) |
| `batches` | Timetabled class groups |
| `attendance` | Daily present/absent records per student |
| `fees` | Fee records, auto remaining/status |
| `assignments` | Assignments per course/batch |
| `exams` | Raw exam marks entry (auto total/%/grade) |
| `results` | Consolidated results (auto-synced from `exams`) |
| `study_materials` | Learning material references (by category/level) |
| `announcements` | Institute-wide announcements |

### Sample documents

```javascript
// users
{
  username: "admin", password: "<bcrypt-hash>", role: "admin",
  full_name: "System Administrator", linked_id: null
}

// students
{
  student_id: "STU0001", full_name: "Anjali Sharma", dob: "2001-05-14",
  gender: "Female", phone: "+919812345678", email: "anjali@example.com",
  address: "12 MG Road, Pune", german_level: "A1", course: "CRS0001",
  batch: "BAT0001", admission_date: "2026-01-10", fees: 15000,
  password: "<bcrypt-hash>", role: "student"
}

// teachers
{
  teacher_id: "TCH0001", full_name: "Markus Weber", phone: "+4915123456789",
  email: "markus@example.com", qualification: "M.A. German Studies",
  specialization: "B2", experience: 6, assigned_course: "CRS0002",
  assigned_batch: "BAT0002", password: "<bcrypt-hash>", role: "teacher"
}

// courses
{
  course_id: "CRS0001", course_name: "German A1 - Beginner", level: "A1",
  duration: 8, fees: 12000, teacher: "TCH0001", batch: "BAT0001",
  start_date: "2026-02-01", end_date: "2026-03-28", max_students: 20
}

// batches
{
  batch_id: "BAT0001", batch_name: "Morning A1", course: "CRS0001",
  level: "A1", teacher: "TCH0001", timing: "Mon-Fri 9AM",
  start_date: "2026-02-01", capacity: 20, status: "Active"
}

// attendance
{
  course: "CRS0001", batch: "BAT0001", date: "2026-08-14",
  student_id: "STU0001", status: "Present", marked_by: "admin"
}

// fees
{
  fee_id: "FEE0001", student_id: "STU0001", student_name: "Anjali Sharma",
  course: "CRS0001", total_fees: 15000, paid_amount: 9000,
  remaining_amount: 6000, payment_status: "Partially Paid",
  payment_date: "2026-03-01"
}

// assignments
{
  assignment_id: "ASG0001", title: "Vocabulary Worksheet 1",
  course: "CRS0001", batch: "BAT0001", description: "Chapter 1 words",
  due_date: "2026-08-20", assigned_by: "TCH0001"
}

// exams
{
  exam_entry_id: "EXM0001", student_id: "STU0001", student_name: "Anjali Sharma",
  course: "CRS0001", exam_name: "A1 Midterm", german_level: "A1",
  reading_marks: 20, writing_marks: 18, listening_marks: 22, speaking_marks: 19,
  total_marks: 79, percentage: 79, grade: "B", result: "Pass"
}

// results (auto-synced from exams)
{
  result_id: "RES0001", exam_entry_id: "EXM0001", student_id: "STU0001",
  student_name: "Anjali Sharma", exam_name: "A1 Midterm", german_level: "A1",
  total_marks: 79, percentage: 79, grade: "B", result: "Pass"
}

// study_materials
{
  material_id: "MAT0001", title: "A1 Grammar Basics", category: "Grammar",
  course: "CRS0001", description: "Articles, cases, verb conjugation",
  file_path: "C:/materials/a1_grammar_basics.pdf", uploaded_by: "TCH0001"
}

// announcements
{
  announcement_id: "ANN0001", heading: "Exam Schedule Released",
  message: "A1 Midterm exams begin next Monday.", posted_by: "admin",
  audience: "All", date_posted: "2026-08-14"
}
```

---

## 6. Feature Summary

- **Backend/Frontend separation**: `backend/` holds config, the MongoDB
  connection layer, models, validation, and helper logic; `frontend/`
  holds every Tkinter window/frame and only ever calls into `backend/`.
- **Role-based access**: Admin sees all 13 modules; Teacher sees a
  restricted subset (Attendance, Assignments, Examination, Results,
  Study Materials, Announcements).
- **Full CRUD everywhere**: every module talks directly to MongoDB via
  PyMongo (through `backend/database.py`) — Add / Update / Delete /
  Search all hit the live database.
- **Auto-generated IDs**: `STU0001`, `TCH0001`, `CRS0001`, `BAT0001`, etc.,
  generated atomically via a `counters` collection (no collisions).
- **Validation**: required fields, email/phone format, numeric ranges,
  duplicate ID prevention (MongoDB unique index + explicit check),
  invalid login handling — all shown via clear message boxes.
- **Security**: bcrypt password hashing (never plain text), login
  authentication, role-based navigation, MongoDB error handling with
  friendly messages if the DB is unreachable.
- **Automatic calculations**:
  - Attendance % = Present / Total Classes × 100 (rows <75% highlighted red)
  - Remaining Fees = Total − Paid, with status Paid/Partially Paid/Pending
  - Exam Total/Percentage/Grade (A+ to Fail) computed on save
- **Dashboard**: live stat cards (students, teachers, courses, active
  batches, today's attendance, pending fees, upcoming exams, announcements)
- **Reports**: Matplotlib bar/pie charts (students per level, fee status,
  pass/fail ratio) embedded directly in the Tkinter window.

---

## 7. How to Run — Quick Checklist

1. `pip install -r requirements.txt`
2. Make sure MongoDB is running (`mongod` service active on port 27017)
3. `python main.py` (run from the project root)
4. Log in with `admin` / `admin123`
5. Add a Course → Add a Batch → Add a Teacher → Add Students →
   Mark Attendance → Add Fees → Enter Exam Marks → check Results & Reports

---

## 8. Common Errors & Solutions

| Error | Cause | Solution |
|---|---|---|
| `Could not connect to MongoDB...` popup on launch | MongoDB service isn't running | Start MongoDB (`mongod` / `brew services start mongodb-community` / `systemctl start mongod`) |
| `ModuleNotFoundError: No module named 'backend'` (or `frontend`) | App wasn't launched from the project root | Always run `python main.py` from inside the top-level `GermanLanguageManagement/` folder |
| `ModuleNotFoundError: No module named 'pymongo'` (or `bcrypt`, `matplotlib`) | Dependencies not installed | Run `pip install -r requirements.txt` |
| `_tkinter.TclError: no display name...` | Running on a headless server with no display | Run on a machine with a desktop GUI (Windows/macOS/Linux desktop), not a headless server/SSH session |
| "Duplicate Entry" when adding a student/teacher/course/batch | The generated/entered ID already exists | This shouldn't normally happen since IDs are auto-generated — if it does, check the `counters` collection wasn't reset while data still exists |
| Login fails with correct-looking credentials | Password wasn't hashed consistently, or user doesn't exist in `users` collection | Remember: `students`/`teachers` collections store profile+password, but **login** checks the `users` collection — see "Creating Teacher Login Accounts" above |
| Attendance "Load Students" shows nothing | No students have that exact Batch ID | Check the Batch ID matches exactly (case-sensitive) what you set in Student Management |
| Charts don't appear in Reports | `matplotlib` not installed, or no data yet in `students`/`fees`/`results` | Install matplotlib; add at least a few records so charts have data to plot |

---

## 9. Notes for Extending the Project

- This project uses a shared `CRUDFrame` base class (`frontend/base.py`)
  so most modules (Students, Teachers, Courses, Batches, Assignments,
  Study Materials, Announcements) are thin subclasses that just declare
  their fields/columns — new modules can be added the same way in a
  few dozen lines.
- Attendance, Fees, Examination/Results, Reports and the Dashboard have
  custom logic (calculations, charts, multi-collection sync) and are
  written as standalone frames in `frontend/`.
- Any new business logic (new calculations, new lookups, new validation
  rules) should go in `backend/` so the frontend stays purely
  presentation-focused.
- All monetary/date values are stored as plain numbers/ISO strings in
  MongoDB for simplicity and portability.
