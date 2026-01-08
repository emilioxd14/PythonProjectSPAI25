import customtkinter as ctk
import calendar
from datetime import datetime

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # State
        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_date = None # "DD.MM.YYYY"
        self.stored_tasks = []

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Grid area expands
        self.grid_rowconfigure(3, weight=1) # Task list area expands
        
        # 1. Header (Month/Year & Navigation)
        self._setup_header()
        
        # 2. Days of Week Header
        self._setup_days_header()
        
        # 3. Calendar Grid Frame
        self.days_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.days_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        # Ensure the grid inside expands evenly
        for i in range(7):
            self.days_frame.grid_columnconfigure(i, weight=1)
        
        # 4. Task List for Selected Date
        self.task_list_frame = ctk.CTkScrollableFrame(self, label_text="Tasks for Selected Date")
        self.task_list_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # Initial Build
        self.build_calendar_grid()

    def _setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1) # Center title

        # Prev Button
        self.btn_prev = ctk.CTkButton(header_frame, text="<", width=30, command=self.prev_month)
        self.btn_prev.grid(row=0, column=0)

        # Title Label
        self.lbl_title = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_title.grid(row=0, column=1)

        # Next Button
        self.btn_next = ctk.CTkButton(header_frame, text=">", width=30, command=self.next_month)
        self.btn_next.grid(row=0, column=2)

    def _setup_days_header(self):
        days_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        days_header_frame.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="ew")
        
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(days):
            days_header_frame.grid_columnconfigure(i, weight=1)
            lbl = ctk.CTkLabel(days_header_frame, text=day, text_color="gray")
            lbl.grid(row=0, column=i, sticky="ew")

    def build_calendar_grid(self):
        # Update Header Title
        month_name = calendar.month_name[self.current_month]
        self.lbl_title.configure(text=f"{month_name} {self.current_year}")

        # Clear existing buttons
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        # Get structure of the month
        # monthrange returns (weekday_of_first_day, number_of_days)
        # weekday: 0=Monday, 6=Sunday
        start_day_idx, num_days = calendar.monthrange(self.current_year, self.current_month)

        # Create Buttons for days
        row_idx = 0
        col_idx = start_day_idx

        for day in range(1, num_days + 1):
            date_str = f"{day:02d}.{self.current_month:02d}.{self.current_year}"
            
            # Determine styling based on state
            is_selected = (date_str == self.selected_date)
            has_task = self._date_has_task(date_str)
            
            # Colors
            fg_color = "#2cc985" if is_selected else "transparent"
            text_color = "white"
            if not is_selected and has_task:
                 text_color = "#ff5555" # Red for tasks if not selected
            
            # Button
            btn = ctk.CTkButton(
                self.days_frame, 
                text=str(day),
                width=40, height=40,
                corner_radius=10,
                fg_color=fg_color,
                text_color=text_color,
                hover_color="gray30",
                command=lambda d=date_str: self.on_day_click(d)
            )
            btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

            col_idx += 1
            if col_idx > 6:
                col_idx = 0
                row_idx += 1

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.build_calendar_grid()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.build_calendar_grid()

    def on_day_click(self, date_str):
        self.selected_date = date_str
        self.build_calendar_grid() # Rebuild to update selection visual
        self._refresh_task_list()

    def load_tasks(self, tasks):
        """Called by main layout to refresh data"""
        self.stored_tasks = tasks
        self.build_calendar_grid() # Rebuild to update markers
        
        # If we have a selection, refresh list. 
        # If not, maybe clear it? For now, refresh if selection exists.
        if self.selected_date:
            self._refresh_task_list()

    def _date_has_task(self, date_str):
        for task in self.stored_tasks:
            if not task.get('completed') and task.get('due_date') == date_str:
                return True
        return False

    def _refresh_task_list(self):
        # Clear list
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
            
        if not self.selected_date:
            return

        # Filter tasks
        found_any = False
        for task in self.stored_tasks:
            # Match date and incomplete status
            if not task.get('completed') and task.get('due_date') == self.selected_date:
                
                display_text = task['text']
                if task.get('due_time'):
                    display_text += f" (@ {task['due_time']})"
                
                label = ctk.CTkLabel(self.task_list_frame, text=f"• {display_text}", anchor="w")
                label.pack(fill="x", padx=10, pady=2)
                found_any = True
        
        if not found_any:
            msg = f"No tasks due on {self.selected_date}."
            label = ctk.CTkLabel(self.task_list_frame, text=msg, text_color="gray")
            label.pack(padx=10, pady=10)
