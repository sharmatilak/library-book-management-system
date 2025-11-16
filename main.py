# main.py
import tkinter as tk
from gui import LibraryApp

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
