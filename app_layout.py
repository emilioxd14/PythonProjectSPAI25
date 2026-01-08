import customtkinter as ctk
from modules.todo.todo_ui import TodoFrame
from modules.notes.notes_ui import StickyNotesFrame
from modules.calendar.calendar_ui import CalendarFrame


class MainLayout:
    def __init__(self, master, controllers):
        self.master = master
        self.controllers = controllers

        # 1. Setup Sidebar
        self._setup_sidebar()

        # 2. Setup Views
        self.todo_view = TodoFrame(master=master, controller=controllers['todo'])
        self.notes_view = StickyNotesFrame(master=master, controller=controllers['notes'])
        self.calendar_view = CalendarFrame(master=master)

        # 3. Show Default
        self.show_todo()

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.master, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # This pushes the "Logo" (if you add one) or empty space to fill the height
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.btn_todo = ctk.CTkButton(self.sidebar, text="To-Do", command=self.show_todo)
        self.btn_todo.grid(row=1, column=0, padx=20, pady=10)

        self.btn_notes = ctk.CTkButton(self.sidebar, text="Notes", command=self.show_notes)
        self.btn_notes.grid(row=2, column=0, padx=20, pady=10)

        self.btn_calendar = ctk.CTkButton(self.sidebar, text="Calendar", command=self.show_calendar)
        self.btn_calendar.grid(row=3, column=0, padx=20, pady=10)

    def show_todo(self):
        self.notes_view.grid_forget()
        self.calendar_view.grid_forget()
        self.todo_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- RESTORED VISUAL FEEDBACK ---
        self.btn_todo.configure(fg_color=("gray75", "gray25"))
        self.btn_notes.configure(fg_color="transparent")
        self.btn_calendar.configure(fg_color="transparent")

    def show_notes(self):
        self.todo_view.grid_forget()
        self.calendar_view.grid_forget()
        self.notes_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- RESTORED VISUAL FEEDBACK ---
        self.btn_notes.configure(fg_color=("gray75", "gray25"))
        self.btn_todo.configure(fg_color="transparent")
        self.btn_calendar.configure(fg_color="transparent")

    def show_calendar(self):
        self.todo_view.grid_forget()
        self.notes_view.grid_forget()
        
        # Refresh Data from Controller
        tasks = self.controllers['todo'].get_tasks()
        self.calendar_view.load_tasks(tasks)

        self.calendar_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- RESTORED VISUAL FEEDBACK ---
        self.btn_calendar.configure(fg_color=("gray75", "gray25"))
        self.btn_todo.configure(fg_color="transparent")
        self.btn_notes.configure(fg_color="transparent")