# ========================================
#      Library Book Management System
#      Author: Tilak
#      Semester: VII
#      Branch: AI/DS
# ========================================

class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.issued = False

class Library:
    def __init__(self):
        self.books = []

    def add_book(self):
        title = input("Enter book title: ").strip()
        author = input("Enter author name: ").strip()
        isbn = input("Enter ISBN: ").strip()

        # check duplicate ISBN
        for b in self.books:
            if b.isbn == isbn:
                print("❌ A book with this ISBN already exists.\n")
                return

        new_book = Book(title, author, isbn)
        self.books.append(new_book)
        print(f"✅ '{title}' added successfully!\n")

    def remove_book(self):
        isbn = input("Enter ISBN of the book to remove: ").strip()
        for b in self.books:
            if b.isbn == isbn:
                self.books.remove(b)
                print(f"🗑️ '{b.title}' removed successfully!\n")
                return
        print("❌ Book not found.\n")

    def search_books(self):
        keyword = input("Enter title or author keyword: ").strip().lower()
        found = [b for b in self.books if keyword in b.title.lower() or keyword in b.author.lower()]
        if not found:
            print("❌ No matching books found.\n")
            return
        print("\n🔎 Search Results:")
        for b in found:
            status = "Issued" if b.issued else "Available"
            print(f"ISBN: {b.isbn} | Title: {b.title} | Author: {b.author} | Status: {status}")
        print()

    def issue_book(self):
        isbn = input("Enter ISBN to issue: ").strip()
        for b in self.books:
            if b.isbn == isbn:
                if not b.issued:
                    b.issued = True
                    print(f"📕 '{b.title}' has been issued.\n")
                    return
                else:
                    print("❌ This book is already issued.\n")
                    return
        print("❌ Book not found.\n")

    def return_book(self):
        isbn = input("Enter ISBN to return: ").strip()
        for b in self.books:
            if b.isbn == isbn:
                if b.issued:
                    b.issued = False
                    print(f"🔁 '{b.title}' has been returned.\n")
                    return
                else:
                    print("❌ This book was not issued.\n")
                    return
        print("❌ Book not found.\n")

    def list_all_books(self):
        if not self.books:
            print("📚 No books in library.\n")
            return
        print("\n------ All Books ------")
        for b in self.books:
            status = "Issued" if b.issued else "Available"
            print(f"ISBN: {b.isbn} | Title: {b.title} | Author: {b.author} | Status: {status}")
        print("-----------------------\n")

    def list_available_books(self):
        available = [b for b in self.books if not b.issued]
        if not available:
            print("❌ No available books.\n")
            return
        print("\n✅ Available Books:")
        for b in available:
            print(f"ISBN: {b.isbn} | Title: {b.title} | Author: {b.author}")
        print()

    def list_issued_books(self):
        issued = [b for b in self.books if b.issued]
        if not issued:
            print("❌ No books are currently issued.\n")
            return
        print("\n📕 Issued Books:")
        for b in issued:
            print(f"ISBN: {b.isbn} | Title: {b.title} | Author: {b.author}")
        print()

    def show_book_details(self):
        isbn = input("Enter ISBN to view details: ").strip()
        for b in self.books:
            if b.isbn == isbn:
                print("\n📖 Book Details:")
                print(f"Title   : {b.title}")
                print(f"Author  : {b.author}")
                print(f"ISBN    : {b.isbn}")
                print(f"Status  : {'Issued' if b.issued else 'Available'}\n")
                return
        print("❌ Book not found.\n")

# ========================================
#              MAIN MENU
# ========================================
def main():
    lib = Library()

    while True:
        print("========== Library Menu ==========")
        print("1) Add book")
        print("2) Remove book")
        print("3) Search books")
        print("4) Issue book")
        print("5) Return book")
        print("6) List all books")
        print("7) List available books")
        print("8) List issued books")
        print("9) Show book details (by ISBN)")
        print("0) Exit")
        print("==================================")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            lib.add_book()
        elif choice == '2':
            lib.remove_book()
        elif choice == '3':
            lib.search_books()
        elif choice == '4':
            lib.issue_book()
        elif choice == '5':
            lib.return_book()
        elif choice == '6':
            lib.list_all_books()
        elif choice == '7':
            lib.list_available_books()
        elif choice == '8':
            lib.list_issued_books()
        elif choice == '9':
            lib.show_book_details()
        elif choice == '0':
            print("👋 Exiting Library System. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
