import customtkinter as ctk

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

        # Input Area
        self.entry = ctk.CTkEntry(self, placeholder_text="Add a new task...")
        self.entry.grid(row=1, column=0, padx=(20, 120), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_new_task())

        self.add_button = ctk.CTkButton(self, text="Add Task", command=self.add_new_task, width=100)
        self.add_button.grid(row=1, column=0, padx=(0, 20), pady=10, sticky="e")

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

    def add_new_task(self):
        text = self.entry.get()
        if text:
            # Send to controller
            self.controller.add_task(text)
            self.entry.delete(0, "end")
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
        # Data format: [{'text': 'Buy Milk', 'completed': False}, ...]
        tasks = self.controller.get_tasks()

        # 3. Sort into frames
        for task in tasks:
            if task['completed']:
                # Draw in Completed Frame
                chk = ctk.CTkCheckBox(self.completed_frame, text=task['text'], text_color="gray")
                chk.select() # Visually show as checked
                chk.configure(command=lambda t=task['text']: self.toggle_task(t))
                chk.pack(pady=5, anchor="w", padx=10)
            else:
                # Draw in Active Frame
                chk = ctk.CTkCheckBox(self.active_frame, text=task['text'])
                chk.configure(command=lambda t=task['text']: self.toggle_task(t))
                chk.pack(pady=5, anchor="w", padx=10)