import tkinter as tk
from gui import BookManagementSystem

if __name__ == "__main__":
    root = tk.Tk()
    app = BookManagementSystem(root)
    root.mainloop()