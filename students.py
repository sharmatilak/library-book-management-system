# students.py
import csv
import os
import sys

# ----- path helpers -----
def base_dir():
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.dirname(os.path.abspath(__file__))
    return base

DATA_DIR = os.path.join(base_dir(), "data")
STUDENTS_CSV = os.path.join(DATA_DIR, "students.csv")

# ----- initialization -----
def ensure_students_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STUDENTS_CSV):
        with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "name", "class", "phone"])

# ----- IO -----
def load_students():
    ensure_students_file()
    rows = []
    with open(STUDENTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def save_students(rows):
    ensure_students_file()
    with open(STUDENTS_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["student_id", "name", "semester", "phone"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

# ----- helpers -----
def next_student_id():
    rows = load_students()
    max_id = 0
    for r in rows:
        try:
            v = int(r.get("student_id", 0))
            if v > max_id: max_id = v
        except:
            continue
    return str(max_id + 1)

# ----- CRUD -----
def add_student(name, cls="", phone=""):
    sid = next_student_id()
    rows = load_students()
    rows.append({"student_id": sid, "name": name, "semester": cls, "phone": phone})
    save_students(rows)
    return sid

def update_student(student_id, name=None, cls=None, phone=None):
    rows = load_students()
    updated = False
    for r in rows:
        if r["student_id"] == str(student_id):
            if name is not None: r["name"] = name
            if cls is not None: r["semester"] = cls
            if phone is not None: r["phone"] = phone
            updated = True
            break
    if updated:
        save_students(rows)
    return updated

def delete_student(student_id):
    rows = load_students()
    new_rows = [r for r in rows if r["student_id"] != str(student_id)]
    if len(new_rows) != len(rows):
        save_students(new_rows)
        return True
    return False

def find_student(student_id):
    for r in load_students():
        if r["student_id"] == str(student_id):
            return r
    return None

def search_students(query):
    q = (query or "").strip().lower()
    if not q:
        return load_students()
    out = []
    for r in load_students():
        if q in r.get("name","").lower() or q == r.get("student_id","") or q in r.get("semester","").lower() or q in r.get("phone",""):
            out.append(r)
    return out
