# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from books import (
    load_books, add_book, update_book, delete_book, find_book, search_books
)
from students import (
    load_students, add_student, update_student, delete_student, find_student, search_students
)
from borrow import (
    borrow_book, return_book, list_currently_borrowed, list_all_borrowed,
    books_borrowed_by_student, who_borrowed_book
)

# ---------- Utility UI helpers ----------
def center_window(win, w=800, h=600):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

# ---------- Main App ----------
class LibraryApp:
    def __init__(self, root):
        self.root = root
        root.title("Library Management System")
        center_window(root, 1000, 650)

        # Create tabs
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.create_books_tab()
        self.create_students_tab()
        self.create_borrow_tab()
        self.create_reports_tab()

    # ---------------- Books Tab ----------------
    def create_books_tab(self):
        self.books_tab = ttk.Frame(self.nb)
        self.nb.add(self.books_tab, text="Books")

        # Top controls
        ctrl = ttk.Frame(self.books_tab)
        ctrl.pack(fill="x", pady=6)

        ttk.Button(ctrl, text="Add Book", command=self.open_add_book).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Edit Selected", command=self.open_edit_book).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Delete Selected", command=self.delete_selected_book).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_books).pack(side="left", padx=4)

        ttk.Label(ctrl, text="Search:").pack(side="left", padx=(12,4))
        self.book_search_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.book_search_var, width=30).pack(side="left")
        ttk.Button(ctrl, text="Go", command=self.search_books_action).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Show All", command=self.refresh_books).pack(side="left", padx=4)

        # Treeview
        cols = ("ID", "Title", "Author", "Year", "ISBN", "Status")
        self.book_tree = ttk.Treeview(self.books_tab, columns=cols, show="headings")
        widths = [60, 320, 180, 80, 140, 90]
        for c, w in zip(cols, widths):
            self.book_tree.heading(c, text=c)
            self.book_tree.column(c, width=w, anchor="w")
        self.book_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.refresh_books()

    def refresh_books(self):
        # Build status by checking borrowed records
        borrowed_now = {r["book_id"] for r in list_currently_borrowed()}
        for r in self.book_tree.get_children():
            self.book_tree.delete(r)
        for b in load_books():
            status = "Borrowed" if b["book_id"] in borrowed_now else "Available"
            self.book_tree.insert("", "end", values=(b["book_id"], b["title"], b["author"], b["year"], b["isbn"], status))

    def open_add_book(self):
        win = tk.Toplevel(self.root)
        win.title("Add Book")
        center_window(win, 420, 260)

        labels = ["Title", "Author", "Year", "ISBN"]
        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=40)
            e.grid(row=i, column=1, padx=8, pady=8)
            entries[lab.lower()] = e

        def on_add():
            title = entries["title"].get().strip()
            if not title:
                messagebox.showerror("Error", "Title required")
                return
            author = entries["author"].get().strip()
            year = entries["year"].get().strip()
            isbn = entries["isbn"].get().strip()
            bid = add_book(title, author, year, isbn)
            messagebox.showinfo("Added", f"Book added with ID {bid}")
            win.destroy()
            self.refresh_books()

        ttk.Button(win, text="Add Book", command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=12)

    def open_edit_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a book to edit")
            return
        vals = self.book_tree.item(sel[0])["values"]
        bid = vals[0]
        book = find_book(bid)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        win = tk.Toplevel(self.root)
        win.title("Edit Book")
        center_window(win, 420, 260)

        labels = [("Title","title"),("Author","author"),("Year","year"),("ISBN","isbn")]
        entries = {}
        for i,(lab,key) in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=40)
            e.grid(row=i, column=1, padx=8, pady=8)
            e.insert(0, book.get(key,""))
            entries[key] = e

        def on_save():
            title = entries["title"].get().strip()
            author = entries["author"].get().strip()
            year = entries["year"].get().strip()
            isbn = entries["isbn"].get().strip()
            update_book(bid, title=title, author=author, year=year, isbn=isbn)
            messagebox.showinfo("Saved", "Book updated")
            win.destroy()
            self.refresh_books()

        ttk.Button(win, text="Save Changes", command=on_save).grid(row=len(labels), column=0, columnspan=2, pady=12)

    def delete_selected_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a book to delete")
            return
        vals = self.book_tree.item(sel[0])["values"]
        bid = vals[0]
        # prevent delete if currently borrowed
        active = list_currently_borrowed()
        if any(r["book_id"] == str(bid) for r in active):
            messagebox.showerror("Error", "Book is currently borrowed. Can't delete.")
            return
        if messagebox.askyesno("Confirm", "Delete selected book?"):
            delete_book(bid)
            self.refresh_books()

    def search_books_action(self):
        q = self.book_search_var.get().strip()
        res = search_books(q)
        borrowed_now = {r["book_id"] for r in list_currently_borrowed()}
        for r in self.book_tree.get_children():
            self.book_tree.delete(r)
        for b in res:
            status = "Borrowed" if b["book_id"] in borrowed_now else "Available"
            self.book_tree.insert("", "end", values=(b["book_id"], b["title"], b["author"], b["year"], b["isbn"], status))

    # ---------------- Students Tab ----------------
    def create_students_tab(self):
        self.students_tab = ttk.Frame(self.nb)
        self.nb.add(self.students_tab, text="Students")

        ctrl = ttk.Frame(self.students_tab)
        ctrl.pack(fill="x", pady=6)

        ttk.Button(ctrl, text="Add Student", command=self.open_add_student).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Edit Selected", command=self.open_edit_student).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Delete Selected", command=self.delete_selected_student).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_students).pack(side="left", padx=4)

        ttk.Label(ctrl, text="Search:").pack(side="left", padx=(12,4))
        self.student_search_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.student_search_var, width=30).pack(side="left")
        ttk.Button(ctrl, text="Go", command=self.search_students_action).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Show All", command=self.refresh_students).pack(side="left", padx=4)

        cols = ("ID", "Name", "Semester", "Phone")
        self.student_tree = ttk.Treeview(self.students_tab, columns=cols, show="headings")
        widths = [80, 360, 120, 140]
        for c,w in zip(cols,widths):
            self.student_tree.heading(c, text=c)
            self.student_tree.column(c, width=w, anchor="w")
        self.student_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.refresh_students()

    def refresh_students(self):
        for r in self.student_tree.get_children():
            self.student_tree.delete(r)
        for s in load_students():
            self.student_tree.insert("", "end", values=(s["student_id"], s["name"], s.get("semester",""), s.get("phone","")))

    def open_add_student(self):
        win = tk.Toplevel(self.root)
        win.title("Add Student")
        center_window(win, 420, 220)

        labels = ["Name", "Semester", "Phone"]
        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=40)
            e.grid(row=i, column=1, padx=8, pady=8)
            entries[lab.lower()] = e

        def on_add():
            name = entries["name"].get().strip()
            if not name:
                messagebox.showerror("Error", "Name required.")
                return
            cls = entries["semester"].get().strip()
            phone = entries["phone"].get().strip()
            sid = add_student(name, cls, phone)
            messagebox.showinfo("Added", f"Student added with ID {sid}")
            win.destroy()
            self.refresh_students()

        ttk.Button(win, text="Add Student", command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def open_edit_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a student to edit")
            return
        vals = self.student_tree.item(sel[0])["values"]
        sid = vals[0]
        s = find_student(sid)
        if not s:
            messagebox.showerror("Error", "Student not found")
            return

        win = tk.Toplevel(self.root)
        win.title("Edit Student")
        center_window(win, 420, 220)

        labels = [("Name","name"),("Semester","semester"),("Phone","phone")]
        entries = {}
        for i,(lab,key) in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=40)
            e.grid(row=i, column=1, padx=8, pady=8)
            e.insert(0, s.get(key,""))
            entries[key] = e

        def on_save():
            name = entries["name"].get().strip()
            cls = entries["semester"].get().strip()
            phone = entries["phone"].get().strip()
            update_student(sid, name=name, cls=cls, phone=phone)
            messagebox.showinfo("Saved", "Student updated")
            win.destroy()
            self.refresh_students()

        ttk.Button(win, text="Save Changes", command=on_save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_selected_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a student to delete")
            return
        vals = self.student_tree.item(sel[0])["values"]
        sid = vals[0]
        # prevent delete if student has active borrow
        active = list_currently_borrowed()
        if any(r["student_id"] == str(sid) for r in active):
            messagebox.showerror("Error", "Student has currently borrowed books. Can't delete.")
            return
        if messagebox.askyesno("Confirm", "Delete selected student?"):
            delete_student(sid)
            self.refresh_students()

    def search_students_action(self):
        q = self.student_search_var.get().strip()
        res = search_students(q)
        for r in self.student_tree.get_children():
            self.student_tree.delete(r)
        for s in res:
            self.student_tree.insert("", "end", values=(s["student_id"], s["name"], s.get("semester",""), s.get("phone","")))

    # ---------------- Borrow Tab ----------------
    def create_borrow_tab(self):
        self.borrow_tab = ttk.Frame(self.nb)
        self.nb.add(self.borrow_tab, text="Borrow / Return")

        ctrl = ttk.Frame(self.borrow_tab)
        ctrl.pack(fill="x", pady=6)

        ttk.Label(ctrl, text="Student ID:").pack(side="left", padx=(4,6))
        self.borrow_student_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.borrow_student_var, width=12).pack(side="left")

        ttk.Label(ctrl, text="Book ID:").pack(side="left", padx=(8,6))
        self.borrow_book_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.borrow_book_var, width=12).pack(side="left")

        ttk.Button(ctrl, text="Borrow", command=self.borrow_action).pack(side="left", padx=8)
        ttk.Button(ctrl, text="Return (by IDs)", command=self.return_action).pack(side="left", padx=8)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_borrow_tree).pack(side="left", padx=8)

        # Borrow listing
        cols = ("BorrowID", "StudentID", "StudentName", "BookID", "BookTitle", "BorrowDate", "ReturnDate")
        self.borrow_tree = ttk.Treeview(self.borrow_tab, columns=cols, show="headings")
        widths = [80, 90, 220, 90, 220, 100, 100]
        for c,w in zip(cols,widths):
            self.borrow_tree.heading(c, text=c)
            self.borrow_tree.column(c, width=w, anchor="w")
        self.borrow_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.refresh_borrow_tree()

    def borrow_action(self):
        sid = self.borrow_student_var.get().strip()
        bid = self.borrow_book_var.get().strip()
        if not sid or not bid:
            messagebox.showerror("Error", "Student ID and Book ID required")
            return
        ok, msg = borrow_book(sid, bid)
        if ok:
            messagebox.showinfo("Success", msg)
            self.refresh_borrow_tree()
            self.refresh_books()
            self.refresh_students()
        else:
            messagebox.showerror("Error", msg)

    def return_action(self):
        sid = self.borrow_student_var.get().strip()
        bid = self.borrow_book_var.get().strip()
        if not sid or not bid:
            messagebox.showerror("Error", "Student ID and Book ID required")
            return
        ok, msg = return_book(student_id=sid, book_id=bid)
        if ok:
            messagebox.showinfo("Success", msg)
            self.refresh_borrow_tree()
            self.refresh_books()
        else:
            messagebox.showerror("Error", msg)

    def refresh_borrow_tree(self):
        for r in self.borrow_tree.get_children():
            self.borrow_tree.delete(r)
        for br in list_all_borrowed():
            s = find_student(br["student_id"]) or {}
            b = find_book(br["book_id"]) or {}
            self.borrow_tree.insert("", "end", values=(
                br.get("borrow_id",""),
                br.get("student_id",""),
                s.get("name",""),
                br.get("book_id",""),
                b.get("title",""),
                br.get("borrow_date",""),
                br.get("return_date","")
            ))

    # ---------------- Reports Tab ----------------
    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.nb)
        self.nb.add(self.reports_tab, text="Reports")

        ctrl = ttk.Frame(self.reports_tab)
        ctrl.pack(fill="x", pady=6)

        ttk.Button(ctrl, text="Show Currently Borrowed", command=self.show_currently_borrowed).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Show Available Books", command=self.show_available_books).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Show Students and Their Borrowed Books", command=self.show_students_borrows).pack(side="left", padx=6)

        # Output box
        self.report_box = tk.Text(self.reports_tab, wrap="none")
        self.report_box.pack(fill="both", expand=True, padx=8, pady=8)

    def show_currently_borrowed(self):
        self.report_box.delete("1.0", "end")
        lines = []
        for r in list_currently_borrowed():
            s = find_student(r["student_id"]) or {}
            b = find_book(r["book_id"]) or {}
            lines.append(f'{s.get("name","Unknown")} (ID {r["student_id"]}) -> {b.get("title","Unknown")} (ID {r["book_id"]}) on {r.get("borrow_date","")}')
        if not lines:
            self.report_box.insert("1.0", "No currently borrowed books.\n")
        else:
            self.report_box.insert("1.0", "\n".join(lines))

    def show_available_books(self):
        self.report_box.delete("1.0", "end")
        borrowed_ids = {r["book_id"] for r in list_currently_borrowed()}
        lines = []
        for b in load_books():
            if b["book_id"] not in borrowed_ids:
                lines.append(f'{b["book_id"]} - {b.get("title","")} by {b.get("author","")}')
        if not lines:
            self.report_box.insert("1.0", "No available books.\n")
        else:
            self.report_box.insert("1.0", "\n".join(lines))

    def show_students_borrows(self):
        self.report_box.delete("1.0", "end")
        students = load_students()
        lines = []
        for s in students:
            borrows = books_borrowed_by_student(s["student_id"])
            if borrows:
                lines.append(f'{s["student_id"]} - {s["name"]}:')
                for br in borrows:
                    b = find_book(br["book_id"]) or {}
                    status = "Returned" if br.get("return_date") else "Not returned"
                    lines.append(f'   {br["book_id"]} - {b.get("title","Unknown")} (Borrowed: {br.get("borrow_date","")}) - {status}')
        if not lines:
            self.report_box.insert("1.0", "No borrow records.\n")
        else:
            self.report_box.insert("1.0", "\n".join(lines))
