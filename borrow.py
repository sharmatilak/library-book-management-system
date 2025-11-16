# borrow.py
import csv
import os
import sys
from datetime import datetime

# ----- path helpers -----
def base_dir():
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.dirname(os.path.abspath(__file__))
    return base

DATA_DIR = os.path.join(base_dir(), "data")
BORROW_CSV = os.path.join(DATA_DIR, "borrow.csv")

# We'll import the other modules for checks (books / students)
from books import find_book, load_books
from students import find_student, load_students

# ----- initialization -----
def ensure_borrow_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BORROW_CSV):
        with open(BORROW_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # borrow_id helps tracking; return_date empty when not returned
            writer.writerow(["borrow_id", "student_id", "book_id", "borrow_date", "return_date"])

# ----- IO -----
def load_borrowed():
    ensure_borrow_file()
    rows = []
    with open(BORROW_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def save_borrowed(rows):
    ensure_borrow_file()
    with open(BORROW_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["borrow_id", "student_id", "book_id", "borrow_date", "return_date"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

# ----- helpers -----
def next_borrow_id():
    rows = load_borrowed()
    max_id = 0
    for r in rows:
        try:
            v = int(r.get("borrow_id", 0))
            if v > max_id: max_id = v
        except:
            continue
    return str(max_id + 1)

def is_book_currently_borrowed(book_id):
    for r in load_borrowed():
        if r["book_id"] == str(book_id) and not r.get("return_date"):
            return True
    return False

# ----- borrow / return operations -----
def borrow_book(student_id, book_id):
    ensure_borrow_file()
    # basic validations
    if not find_student(student_id):
        return False, "Student not found."
    if not find_book(book_id):
        return False, "Book not found."
    if is_book_currently_borrowed(book_id):
        return False, "Book already borrowed."

    bid = next_borrow_id()
    now = datetime.now().strftime("%Y-%m-%d")
    rows = load_borrowed()
    rows.append({
        "borrow_id": bid,
        "student_id": str(student_id),
        "book_id": str(book_id),
        "borrow_date": now,
        "return_date": ""
    })
    save_borrowed(rows)
    return True, "Borrow recorded."

def return_book(borrow_id=None, student_id=None, book_id=None):
    """
    You can return by borrow_id OR by student_id+book_id.
    """
    rows = load_borrowed()
    changed = False
    now = datetime.now().strftime("%Y-%m-%d")

    for r in rows:
        match = False
        if borrow_id and r["borrow_id"] == str(borrow_id):
            match = True
        elif student_id and book_id and r["student_id"] == str(student_id) and r["book_id"] == str(book_id):
            match = True

        if match:
            if not r.get("return_date"):
                r["return_date"] = now
                changed = True

    if changed:
        save_borrowed(rows)
        return True, "Return recorded."
    return False, "No matching active borrow record found."

# ----- queries -----
def list_currently_borrowed():
    """Return borrow rows where return_date is empty"""
    return [r for r in load_borrowed() if not r.get("return_date")]

def list_all_borrowed():
    """All borrow records (history)"""
    return load_borrowed()

def books_borrowed_by_student(student_id):
    out = []
    for r in load_borrowed():
        if r["student_id"] == str(student_id):
            out.append(r)
    return out

def who_borrowed_book(book_id):
    out = []
    for r in load_borrowed():
        if r["book_id"] == str(book_id):
            out.append(r)
    return out
