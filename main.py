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
        
        # Start Reminder Polling
        self.check_reminders()

    def check_reminders(self):
        """Polls for overdue tasks every minute."""
        overdue = self.controllers['todo'].check_due_tasks()
        
        # Avoid opening multiple windows if one is already open
        if overdue and (not hasattr(self, 'reminder_window') or not self.reminder_window.winfo_exists()):
            self.reminder_window = ctk.CTkToplevel(self)
            self.reminder_window.title("Task Reminder")
            self.reminder_window.geometry("350x250")
            self.reminder_window.attributes("-topmost", True)
            
            ctk.CTkLabel(self.reminder_window, text="⏰ Overdue Tasks!", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
            
            scroll = ctk.CTkScrollableFrame(self.reminder_window, height=150)
            scroll.pack(fill="x", padx=10, pady=5)
            
            for task in overdue:
                lbl = ctk.CTkLabel(scroll, text=f"• {task['text']}", anchor="w")
                lbl.pack(fill="x", padx=5)
            
            ctk.CTkButton(self.reminder_window, text="Dismiss", command=self.reminder_window.destroy).pack(pady=10)

        # Check again in 60 seconds
        self.after(60000, self.check_reminders)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = MainApp()
    app.mainloop()