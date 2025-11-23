import customtkinter as ctk
# This assumes storage.py is in the main project folder (ProjectRoot/storage.py)
from storage import TodoStorage


class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Initialize the Storage Engine
        self.storage = TodoStorage()

        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=3)  # Active Tasks
        self.grid_rowconfigure(3, weight=1)  # Completed Tasks
        self.grid_rowconfigure(4, weight=0)  # Clear Button

        # 1. Title Label
        self.title_label = ctk.CTkLabel(self, text="My Tasks", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 2. Input Area
        self.entry = ctk.CTkEntry(self, placeholder_text="Add a new task...")
        self.entry.grid(row=1, column=0, padx=(20, 120), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_new_task())

        self.add_button = ctk.CTkButton(self, text="Add Task", command=self.add_new_task, width=100)
        self.add_button.grid(row=1, column=0, padx=(0, 20), pady=10, sticky="e")

        # 3. Active Tasks Frame
        self.active_frame = ctk.CTkScrollableFrame(self, label_text="Active Tasks")
        self.active_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # 4. Completed Tasks Frame
        self.completed_frame = ctk.CTkScrollableFrame(self, label_text="Completed Tasks", label_fg_color="gray")
        self.completed_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # 5. Clear Button
        self.clear_button = ctk.CTkButton(self, text="Clear Completed", fg_color="#D32F2F", hover_color="#B71C1C",
                                          command=self.clear_history)
        self.clear_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # Lists to keep track of widgets
        self.active_widgets = []
        self.completed_widgets = []

        # 6. Load Data immediately
        self.load_tasks_from_storage()

    def add_new_task(self):
        text = self.entry.get()
        if text:
            self.create_active_task(text)
            self.entry.delete(0, "end")
            self.update_storage()

    def create_active_task(self, text):
        checkbox = ctk.CTkCheckBox(self.active_frame, text=text)
        checkbox.configure(command=lambda: self.move_to_completed(checkbox))
        checkbox.pack(pady=5, anchor="w", padx=10)
        self.active_widgets.append(checkbox)

    def create_completed_task(self, text):
        checkbox = ctk.CTkCheckBox(self.completed_frame, text=text, text_color="gray")
        checkbox.select()
        checkbox.configure(command=lambda: self.move_to_active(checkbox))
        checkbox.pack(pady=5, anchor="w", padx=10)
        self.completed_widgets.append(checkbox)

    def move_to_completed(self, widget):
        text = widget.cget("text")
        if widget in self.active_widgets:
            self.active_widgets.remove(widget)
        widget.destroy()
        self.create_completed_task(text)
        self.update_storage()

    def move_to_active(self, widget):
        text = widget.cget("text")
        if widget in self.completed_widgets:
            self.completed_widgets.remove(widget)
        widget.destroy()
        self.create_active_task(text)
        self.update_storage()

    def clear_history(self):
        for widget in self.completed_widgets:
            widget.destroy()
        self.completed_widgets.clear()
        self.update_storage()

    def update_storage(self):
        data = []
        for widget in self.active_widgets:
            data.append({"text": widget.cget("text"), "completed": False})
        for widget in self.completed_widgets:
            data.append({"text": widget.cget("text"), "completed": True})

        self.storage.save_data(data)

    def load_tasks_from_storage(self):
        data = self.storage.load_data()
        for item in data:
            if item["completed"]:
                self.create_completed_task(item["text"])
            else:
                self.create_active_task(item["text"])