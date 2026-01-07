import customtkinter as ctk

# 1. Import Layout
from app_layout import MainLayout

# 2. Import Logic
from modules.todo.todo_logic import TodoLogic
from modules.notes.notes_logic import NotesLogic
from modules.calendar.calendar_logic import CalendarLogic

# 3. Import AI Logic (Safe Import)
try:
    from modules.ai.ai_logic import AiAssistant
except ImportError:
    AiAssistant = None

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Productivity Dashboard")
        self.geometry("900x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize Base Controllers
        todo_logic = TodoLogic()
        notes_logic = NotesLogic()
        
        # Inicializamos el Calendario (necesita acceso a las tareas)
        calendar_logic = CalendarLogic(todo_controller=todo_logic)
        # Initialize AI Controller safely
        if AiAssistant:
            ai_logic = AiAssistant(todo_logic, notes_logic)
        else:
            ai_logic = None

        # --- CORRECCIÓN CRÍTICA ---
        # Definimos explícitamente la clave 'ai', aunque sea None.
        self.controllers = {
            'todo': todo_logic,
            'notes': notes_logic,
            'ai': ai_logic, # <--- Esto evita el KeyError en app_layout.py
            'calendar': calendar_logic
        }

        # Hand over control to the Layout Manager
        self.layout = MainLayout(self, self.controllers)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = MainApp()
    app.mainloop()