
import customtkinter as ctk
import datetime
import calendar

class DateTimePickerDialog(ctk.CTkToplevel):
    def __init__(self, master, on_confirm=None, initial_date=None, initial_time=None):
        super().__init__(master)
        
        self.on_confirm = on_confirm
        self.title("Pick Date & Time")
        self.geometry("380x500")
        self.resizable(False, False)
        
        # Modal
        self.transient(master)
        self.grab_set()
        
        # State
        now = datetime.datetime.now()
        
        # Handle initial date string "YYYY-MM-DD"
        if initial_date:
            try:
                d = datetime.datetime.strptime(initial_date, "%Y-%m-%d").date()
                self.selected_year = d.year
                self.selected_month = d.month
                self.selected_day = d.day
            except ValueError:
                self.selected_year = now.year
                self.selected_month = now.month
                self.selected_day = None
        else:
            self.selected_year = now.year
            self.selected_month = now.month
            self.selected_day = None # No day selected initially? Or today? Let's say None or Today. Let's pick None to force selection, or Today. Let's stick effectively to "current month view" and selection is None until clicked.
            
        # Handle initial time string "HH:MM"
        if initial_time:
            try:
                t = datetime.datetime.strptime(initial_time, "%H:%M").time()
                self.selected_hour = f"{t.hour:02d}"
                self.selected_minute = f"{t.minute:02d}"
            except ValueError:
                self.selected_hour = "09"
                self.selected_minute = "00"
        else:
            self.selected_hour = "09" # Default morning
            self.selected_minute = "00"

        # --- UI LAYOUT ---
        # 1. Header (Month/Year Nav)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        self.prev_btn = ctk.CTkButton(self.header_frame, text="<", width=30, command=self.prev_month)
        self.prev_btn.pack(side="left")
        
        self.month_label = ctk.CTkLabel(self.header_frame, text="Month Year", font=ctk.CTkFont(size=16, weight="bold"), width=140)
        self.month_label.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(self.header_frame, text=">", width=30, command=self.next_month)
        self.next_btn.pack(side="left")
        
        # Year Selector
        years = [str(y) for y in range(now.year - 5, now.year + 6)]
        self.year_menu = ctk.CTkOptionMenu(self.header_frame, values=years, width=80, command=self.on_year_change)
        self.year_menu.set(str(self.selected_year))
        self.year_menu.pack(side="right")
        
        # 2. Calendar Grid
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 3. Time Selection
        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.time_frame, text="Time:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5))
        
        hours = [f"{h:02d}" for h in range(24)]
        self.hour_menu = ctk.CTkOptionMenu(self.time_frame, values=hours, width=70)
        self.hour_menu.set(self.selected_hour)
        self.hour_menu.pack(side="left", padx=2)
        
        ctk.CTkLabel(self.time_frame, text=":").pack(side="left")
        
        minutes = [f"{m:02d}" for m in range(0, 60, 5)] # Step 5 is cleaner
        self.minute_menu = ctk.CTkOptionMenu(self.time_frame, values=minutes, width=70)
        self.minute_menu.set(self.selected_minute)
        self.minute_menu.pack(side="left", padx=2)
        
        # 4. Footer (Buttons)
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=10, pady=10)
        
        self.confirm_btn = ctk.CTkButton(self.footer_frame, text="Confirm Schedule", fg_color="#2CC985", hover_color="#26A66B", command=self.confirm_selection)
        self.confirm_btn.pack(side="right", padx=10)
        
        ctk.CTkButton(self.footer_frame, text="Cancel", fg_color="transparent", border_width=1, command=self.destroy).pack(side="right")

        # Initial Render
        self.render_calendar()

    def render_calendar(self):
        # Update Header
        month_name = calendar.month_name[self.selected_month]
        self.month_label.configure(text=f"{month_name} {self.selected_year}")
        self.year_menu.set(str(self.selected_year))
        
        # Clear Grid
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        # Headers (Mon, Tue...)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(self.calendar_frame, text=day, text_color="gray").grid(row=0, column=i, pady=(5, 5))
            
        # Days
        cal = calendar.monthcalendar(self.selected_year, self.selected_month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                
                # Check if this day is selected
                is_selected = (day == self.selected_day)
                
                fg_color = "#3B8ED0" if is_selected else "transparent"
                hover_color = "#36719F" if is_selected else ("gray85", "gray25")
                text_color = "white" if is_selected else ("black", "white")
                
                btn = ctk.CTkButton(self.calendar_frame, text=str(day), width=30, height=30, corner_radius=5,
                                    fg_color=fg_color, hover_color=hover_color, text_color=text_color,
                                    command=lambda d=day: self.select_day(d))
                btn.grid(row=r+1, column=c, padx=2, pady=2)

    def select_day(self, day):
        self.selected_day = day
        self.render_calendar() # Re-render to see highlight

    def prev_month(self):
        self.selected_month -= 1
        if self.selected_month < 1:
            self.selected_month = 12
            self.selected_year -= 1
        self.selected_day = None # Reset day on month change? Or keep? Reset is safer UI.
        self.render_calendar()

    def next_month(self):
        self.selected_month += 1
        if self.selected_month > 12:
            self.selected_month = 1
            self.selected_year += 1
        self.selected_day = None
        self.render_calendar()
        
    def on_year_change(self, value):
        self.selected_year = int(value)
        self.selected_day = None
        self.render_calendar()

    def confirm_selection(self):
        if not self.selected_day:
            return # Should probably show error, but silent ignore is ok for now
            
        date_str = f"{self.selected_year:04d}-{self.selected_month:02d}-{self.selected_day:02d}"
        time_str = f"{self.hour_menu.get()}:{self.minute_menu.get()}"
        
        if self.on_confirm:
            self.on_confirm(date_str, time_str)
        
        self.destroy()
