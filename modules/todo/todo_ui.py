import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        # 1. Inject Controller (The Brain)
        self.controller = controller

        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=3)  # Active Tasks
        self.grid_rowconfigure(3, weight=1)  # Completed Tasks
        self.grid_rowconfigure(4, weight=0)  # Clear Button

        # Title
        self.title_label = ctk.CTkLabel(self, text="My Tasks", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Input Frame
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Task Input
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Add a new task...")
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_new_task())

        # Date Entry (standard tk widget) -> European Format
        self.date_entry = DateEntry(self.input_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
        self.date_entry.grid(row=0, column=1, padx=(0, 10))

        # Time Input
        self.time_entry = ctk.CTkEntry(self.input_frame, placeholder_text="HH:MM", width=60)
        self.time_entry.grid(row=0, column=2, padx=(0, 10))
        self.time_entry.bind("<KeyRelease>", self.format_time_input)

        # Reminder Checkbox
        self.reminder_var = ctk.BooleanVar(value=False)
        self.reminder_chk = ctk.CTkCheckBox(self.input_frame, text="Alert", variable=self.reminder_var, width=60)
        self.reminder_chk.grid(row=0, column=3, padx=(0, 10))

        # Add Button
        self.add_button = ctk.CTkButton(self.input_frame, text="Add", command=self.add_new_task, width=60)
        self.add_button.grid(row=0, column=4)

        # Active Tasks Frame
        self.active_frame = ctk.CTkScrollableFrame(self, label_text="Active Tasks")
        self.active_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Completed Tasks Frame
        self.completed_frame = ctk.CTkScrollableFrame(self, label_text="Completed Tasks", label_fg_color="gray")
        self.completed_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # Clear Button
        self.clear_button = ctk.CTkButton(self, text="Clear Completed", fg_color="#D32F2F", hover_color="#B71C1C",
                                          command=self.clear_history)
        self.clear_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # 2. Load Data via Controller
        self.refresh_view()

    def format_time_input(self, event):
        """Auto-formats time input to HH:MM"""
        if event.keysym == "BackSpace":
            return
            
        text = self.time_entry.get()
        
        # Auto-insert colon after 2 chars
        if len(text) == 2:
            self.time_entry.delete(0, "end")
            self.time_entry.insert(0, text + ":")
            
        # Limit length to 5 (HH:MM)
        if len(text) > 5:
            self.time_entry.delete(5, "end")

    def add_new_task(self):
        text = self.entry.get()
        if text:
            # Gather extras
            d_date = self.date_entry.get_date() # date object
            try:
                # convert to european string DD.MM.YYYY
                due_date_str = d_date.strftime("%d.%m.%Y")
            except:
                due_date_str = None
                
            due_time_str = self.time_entry.get().strip()
            if not due_time_str: 
                due_time_str = None
            
            reminder = self.reminder_var.get()

            # Send to controller
            self.controller.add_task(text, due_date=due_date_str, due_time=due_time_str, reminder=reminder)
            
            # Reset UI
            self.entry.delete(0, "end")
            self.time_entry.delete(0, "end")
            self.reminder_var.set(False)
            self.refresh_view()

    def toggle_task(self, task_text):
        """User clicked a checkbox. Tell controller to flip the status."""
        self.controller.toggle_task_status(task_text)
        self.refresh_view()

    def clear_history(self):
        """Tell controller to delete all completed items."""
        self.controller.clear_completed_tasks()
        self.refresh_view()

    def refresh_view(self):
        """Clear all lists and redraw them based on Controller data."""
        # 1. Clear current widgets
        for widget in self.active_frame.winfo_children():
            widget.destroy()
        for widget in self.completed_frame.winfo_children():
            widget.destroy()

        # 2. Get fresh data
        tasks = self.controller.get_tasks()

        # 3. Sort into frames
        for task in tasks:
            # Create display text
            display_text = task['text']
            # Append Due Info
            extras = []
            if task.get('due_date'):
                extras.append(task['due_date'])
            if task.get('due_time'):
                extras.append(task['due_time'])
            
            if extras:
                display_text += f" ({' '.join(extras)})"
            
            if task.get('reminder'):
                display_text += " ⏰"

            if task['completed']:
                # Draw in Completed Frame
                chk = ctk.CTkCheckBox(self.completed_frame, text=display_text, text_color="gray")
                chk.select() 
                chk.configure(command=lambda t=task['text']: self.toggle_task(t))
                chk.pack(pady=5, anchor="w", padx=10)
            else:
                # Draw in Active Frame
                chk = ctk.CTkCheckBox(self.active_frame, text=display_text)
                chk.configure(command=lambda t=task['text']: self.toggle_task(t))
                chk.pack(pady=5, anchor="w", padx=10)