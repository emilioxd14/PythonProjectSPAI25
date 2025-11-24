import customtkinter as ctk

# 1. Import the Layout Manager (The code you just wrote)
# Ensure the file is named 'app_layout.py' inside the 'modules' folder
from app_layout import MainLayout

# 2. Import Logic (The Brains)
from modules.todo.todo_logic import TodoLogic
from modules.notes.notes_logic import NotesLogic

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Productivity Dashboard")
        self.geometry("900x600")

        # --- CRITICAL: GRID CONFIGURATION ---
        # If you miss this, the layout won't stretch!
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize Logic
        self.controllers = {
            'todo': TodoLogic(),
            'notes': NotesLogic()
        }

        # Hand over control to the Layout Manager
        self.layout = MainLayout(self, self.controllers)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = MainApp()
    app.mainloop()