import customtkinter as ctk

# --- CHANGED IMPORTS TO MATCH YOUR FOLDER STRUCTURE ---
# Instead of 'from ui import TodoFrame', we dig into the folder:
from modules.todo.todo_ui import TodoFrame
from modules.notes.notes_ui import StickyNotesFrame

class MainApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("Productivity Dashboard")
        self.geometry("900x600")

        # Grid Layout: 2 Columns
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 2. Create Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="My Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # 3. Sidebar Buttons
        self.btn_todo = ctk.CTkButton(self.sidebar, text="To-Do List", command=self.show_todo)
        self.btn_todo.grid(row=1, column=0, padx=20, pady=10)

        self.btn_notes = ctk.CTkButton(self.sidebar, text="Sticky Notes", command=self.show_notes)
        self.btn_notes.grid(row=2, column=0, padx=20, pady=10)

        # 4. Initialize the Frames (Views)
        # We pass 'self' as the master, so they sit inside the MainApp window
        self.todo_view = TodoFrame(master=self)
        self.notes_view = StickyNotesFrame(master=self)

        # 5. Show Default View
        self.show_todo()

    def show_todo(self):
        """Hides notes, shows todo"""
        self.notes_view.grid_forget()
        self.todo_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Update button colors (Visual Feedback)
        self.btn_todo.configure(fg_color=("gray75", "gray25"))
        self.btn_notes.configure(fg_color="transparent")

    def show_notes(self):
        """Hides todo, shows notes"""
        self.todo_view.grid_forget()
        self.notes_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Update button colors
        self.btn_notes.configure(fg_color=("gray75", "gray25"))
        self.btn_todo.configure(fg_color="transparent")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()