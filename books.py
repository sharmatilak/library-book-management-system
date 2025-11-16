# books.py
import csv
import os
import sys
from datetime import datetime

# ----- path helpers (works in dev and when packaged with PyInstaller) -----
def base_dir():
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.dirname(os.path.abspath(__file__))
    return base

DATA_DIR = os.path.join(base_dir(), "data")
BOOKS_CSV = os.path.join(DATA_DIR, "books.csv")

# ----- initialization -----
def ensure_books_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BOOKS_CSV):
        with open(BOOKS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["book_id", "title", "author", "year", "isbn"])

# ----- low-level IO -----
def load_books():
    ensure_books_file()
    rows = []
    with open(BOOKS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def save_books(rows):
    ensure_books_file()
    with open(BOOKS_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["book_id", "title", "author", "year", "isbn"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

# ----- helpers -----
def next_book_id():
    rows = load_books()
    max_id = 0
    for r in rows:
        try:
            v = int(r.get("book_id", 0))
            if v > max_id: max_id = v
        except:
            continue
    return str(max_id + 1)

# ----- CRUD operations -----
def add_book(title, author="", year="", isbn=""):
    bid = next_book_id()
    rows = load_books()
    rows.append({
        "book_id": bid,
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn
    })
    save_books(rows)
    return bid

def update_book(book_id, title=None, author=None, year=None, isbn=None):
    rows = load_books()
    updated = False
    for r in rows:
        if r["book_id"] == str(book_id):
            if title is not None: r["title"] = title
            if author is not None: r["author"] = author
            if year is not None: r["year"] = year
            if isbn is not None: r["isbn"] = isbn
            updated = True
            break
    if updated:
        save_books(rows)
    return updated

def delete_book(book_id):
    rows = load_books()
    new_rows = [r for r in rows if r["book_id"] != str(book_id)]
    if len(new_rows) != len(rows):
        save_books(new_rows)
        return True
    return False

def find_book(book_id):
    rows = load_books()
    for r in rows:
        if r["book_id"] == str(book_id):
            return r
    return None

def search_books(query):
    q = (query or "").strip().lower()
    if not q:
        return load_books()
    out = []
    for r in load_books():
        if q in r.get("title","").lower() or q in r.get("author","").lower() or q in r.get("isbn","").lower() or q == r.get("book_id",""):
            out.append(r)
    return out
