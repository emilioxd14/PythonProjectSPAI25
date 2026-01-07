import customtkinter as ctk
import datetime
import calendar

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master, calendar_logic, **kwargs):
        super().__init__(master, **kwargs)
        self.logic = calendar_logic
        self.current_date = datetime.date.today()
        self.view_mode = "Month" 

        # --- Cyber Colors ---
        self.bg_color = "black"
        self.grid_border = "#113311"
        self.text_neon = "#00FF41"
        self.text_cyan = "#00FFFF"
        self.current_day_fill = "#00FF41"
        
        self.configure(fg_color=self.bg_color)

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self.header_frame.grid_columnconfigure(2, weight=1) 

        # Navigation
        self.prev_btn = ctk.CTkButton(self.header_frame, text="[ PREV ]", width=80, 
                                      font=("Consolas", 12, "bold"), fg_color="transparent",
                                      border_width=1, border_color=self.text_neon, 
                                      text_color=self.text_neon, hover_color="#002200", corner_radius=0,
                                      command=self.go_prev)
        self.prev_btn.pack(side="left", padx=(0, 10))
        
        self.next_btn = ctk.CTkButton(self.header_frame, text="[ NEXT ]", width=80, 
                                      font=("Consolas", 12, "bold"), fg_color="transparent",
                                      border_width=1, border_color=self.text_neon,
                                      text_color=self.text_neon, hover_color="#002200", corner_radius=0,
                                      command=self.go_next)
        self.next_btn.pack(side="left", padx=(0, 20))

        # Current Date Label
        self.date_label = ctk.CTkLabel(self.header_frame, text="", 
                                       font=("Consolas", 20, "bold"), text_color=self.text_cyan)
        self.date_label.pack(side="left")

        # View Switcher
        self.view_switcher = ctk.CTkSegmentedButton(self.header_frame, 
                                                    values=["Month", "Week", "Day"],
                                                    font=("Consolas", 12),
                                                    selected_color=self.text_neon,
                                                    selected_hover_color="#00CC33",
                                                    unselected_color="black",
                                                    unselected_hover_color="#111",
                                                    text_color=("white", "black"), # Black text when selected (Neon bg)
                                                    corner_radius=0,
                                                    command=self.switch_view)
        self.view_switcher.set("Month")
        self.view_switcher.pack(side="right")

        # 2. Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Initial Render
        self.render()

    def switch_view(self, mode):
        self.view_mode = mode
        self.render()

    def go_prev(self):
        if self.view_mode == "Month":
            first = self.current_date.replace(day=1)
            prev_month = first - datetime.timedelta(days=1)
            self.current_date = prev_month.replace(day=1)
        elif self.view_mode == "Week":
            self.current_date -= datetime.timedelta(days=7)
        else: # Day View
            self.current_date -= datetime.timedelta(days=1)
        self.render()

    def go_next(self):
        if self.view_mode == "Month":
            next_month = self.get_next_month_start(self.current_date)
            self.current_date = next_month
        elif self.view_mode == "Week":
            self.current_date += datetime.timedelta(days=7)
        else: # Day View
            self.current_date += datetime.timedelta(days=1)
        self.render()

    def get_next_month_start(self, date):
        days_in_month = calendar.monthrange(date.year, date.month)[1]
        next_month = date.replace(day=28) + datetime.timedelta(days=4)
        return next_month.replace(day=1)

    def render(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if self.view_mode == "Month":
            self._render_month_view()
        elif self.view_mode == "Week":
            self._render_week_view()
        elif self.view_mode == "Day":
            self._render_day_view()

    # --- VIEWS ---

    def _render_month_view(self):
        self.date_label.configure(text=f"> ORBIT: {self.current_date.strftime('%B %Y').upper()}")

        matrix = self.logic.get_month_matrix(self.current_date.year, self.current_date.month)
        
        # Weekday Headers
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for i, day in enumerate(days):
            self.content_frame.grid_columnconfigure(i, weight=1)
            lbl = ctk.CTkLabel(self.content_frame, text=day, font=("Consolas", 12), text_color="gray50")
            lbl.grid(row=0, column=i, pady=(0, 5))

        # Days
        for r, week in enumerate(matrix):
            self.content_frame.grid_rowconfigure(r+1, weight=1)
            for c, day in enumerate(week):
                if day == 0:
                    # Empty grid cell for alignment visuals
                    empty = ctk.CTkFrame(self.content_frame, fg_color="#050505", corner_radius=0, border_width=1, border_color="#111")
                    empty.grid(row=r+1, column=c, sticky="nsew", padx=0, pady=0)
                    continue
                
                date_obj = datetime.date(self.current_date.year, self.current_date.month, day)
                events = self.logic.get_events(date_obj, date_obj)
                
                # Style
                bg = "black"
                border_col = self.grid_border
                border_wid = 1
                text_col = "white"
                
                today = datetime.date.today()
                
                # Day Card
                day_card = ctk.CTkFrame(self.content_frame, fg_color=bg, corner_radius=0, 
                                        border_width=border_wid, border_color=border_col)
                day_card.grid(row=r+1, column=c, padx=0, pady=0, sticky="nsew")
                
                # Highlighting Today
                if date_obj == today:
                    # Solid fill for Today as per instructions
                    day_card.configure(fg_color=self.current_day_fill) 
                    text_col = "black" 
                
                # Interactive Bindings
                day_card.bind("<Enter>", lambda e, ev=events: self.on_day_hover(ev))
                day_card.bind("<Leave>", lambda e: self.on_day_leave())
                day_card.bind("<Button-1>", lambda e, d=date_obj: self.on_day_click(d))
                
                # Day Number
                num_lbl = ctk.CTkLabel(day_card, text=str(day), font=("Consolas", 10, "bold"), text_color=text_col)
                num_lbl.place(relx=0.05, rely=0.05, anchor="nw")
                num_lbl.bind("<Button-1>", lambda e, d=date_obj: self.on_day_click(d)) 
                
                # Event Markers (Text Symbols)
                if events:
                    count = len(events)
                    marker_text = f"[!{count}]" if count < 10 else "[!!]"
                    marker_col = self.text_cyan if date_obj != today else "black"
                    
                    marker = ctk.CTkLabel(day_card, text=marker_text, font=("Consolas", 10), text_color=marker_col)
                    marker.place(relx=0.5, rely=0.5, anchor="center")
                    marker.bind("<Button-1>", lambda e, d=date_obj: self.on_day_click(d))

        # Preview Panel
        self.preview_panel = ctk.CTkLabel(self.content_frame, text="> AWAITING TARGET SELECTION...", 
                                          height=30, fg_color="black", text_color=self.text_neon,
                                          font=("Consolas", 12), anchor="w")
        self.preview_panel.grid(row=len(matrix)+1, column=0, columnspan=7, sticky="ew", pady=(10, 0))

    def on_day_hover(self, events):
        if not events:
            self.preview_panel.configure(text="> SECTOR CLEAR")
            return
        
        count = len(events)
        preview_text = f"> DETECTED {count} TASKS: " + " // ".join([t['text'] for t in events[:3]])
        if count > 3:
            preview_text += "..."
        self.preview_panel.configure(text=preview_text)

    def on_day_leave(self):
        self.preview_panel.configure(text="> AWAITING TARGET SELECTION...")

    def on_day_click(self, date_obj):
        self.current_date = date_obj
        self.view_switcher.set("Day")
        self.switch_view("Day")

    def _render_week_view(self):
        week_dates = self.logic.get_week_dates(self.current_date)
        start_str = week_dates[0].strftime("%b%d").upper()
        end_str = week_dates[-1].strftime("%b%d").upper()
        self.date_label.configure(text=f"> CYCLE: {start_str} - {end_str}")

        self.content_frame.grid_rowconfigure(0, weight=3)
        self.content_frame.grid_rowconfigure(1, weight=2)

        # Work Week
        weekdays = week_dates[:5]
        for i, date_obj in enumerate(weekdays):
            self.content_frame.grid_columnconfigure(i, weight=1)
            
            # Highlight Today
            fg = "black"
            border = self.text_neon if date_obj == datetime.date.today() else "#222"
            
            col_frame = ctk.CTkFrame(self.content_frame, corner_radius=0, fg_color=fg, border_width=1, border_color=border)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=1, pady=(0, 5))
            
            # Header
            header_text = date_obj.strftime("%a\n%d").upper()
            ctk.CTkLabel(col_frame, text=header_text, font=("Consolas", 12, "bold"), text_color="white").pack(pady=5)
            
            events = self.logic.get_events(date_obj, date_obj)
            
            for e in events:
                txt = f"> {e['text']}"
                if len(txt) > 20: txt = txt[:17] + ".."
                ctk.CTkLabel(col_frame, text=txt, font=("Consolas", 10), text_color="gray70", anchor="w").pack(fill="x", padx=2)

        # Weekend
        weekend = week_dates[5:]
        weekend_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        weekend_container.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=(5, 0))
        weekend_container.grid_columnconfigure(0, weight=1)
        weekend_container.grid_columnconfigure(1, weight=1)
        weekend_container.grid_rowconfigure(0, weight=1)

        for i, date_obj in enumerate(weekend):
            border = self.text_neon if date_obj == datetime.date.today() else "#222"
            col_frame = ctk.CTkFrame(weekend_container, corner_radius=0, fg_color="black", border_width=1, border_color=border)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=1)

            header_text = date_obj.strftime("%A %d").upper()
            ctk.CTkLabel(col_frame, text=header_text, font=("Consolas", 12, "bold"), text_color="gray50").pack(pady=5)

            events = self.logic.get_events(date_obj, date_obj)
            for e in events:
                ctk.CTkLabel(col_frame, text=f"> {e['text']}", font=("Consolas", 10), text_color="gray70").pack(fill="x")

    def _render_day_view(self):
        current_day = self.current_date
        self.date_label.configure(text=f"> TARGET: {current_day.strftime('%A, %b %d').upper()}")
        
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        for r in range(1, 10):
            self.content_frame.grid_rowconfigure(r, weight=0)

        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="black", corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew")
        
        events = self.logic.get_events(current_day, current_day)
        events.sort(key=lambda x: x.get('due_time') or "00:00")
        
        if not events:
            ctk.CTkLabel(scroll, text="> NO OBJECTIVES DETECTED.", font=("Consolas", 14), text_color="gray50").pack(pady=20)
            return
            
        for e in events:
            # Card
            card = ctk.CTkFrame(scroll, fg_color="#050505", corner_radius=0, border_width=1, border_color="#333")
            card.pack(fill="x", pady=2, padx=10, expand=False)
            
            prio = e.get('priority', 'Medium')
            # Neon accents based on priority
            color = {"High": "#FF0055", "Medium": "#FFAA00", "Low": "#00FF41"}.get(prio, "#FFAA00")
            
            # Colored Strip
            ctk.CTkFrame(card, width=3, fg_color=color, corner_radius=0).pack(side="left", fill="y", padx=(0, 5))
            
            # Info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, pady=2)
            
            title = ctk.CTkLabel(info_frame, text=e['text'], font=("Consolas", 14, "bold"), text_color="white", anchor="w")
            title.pack(side="left", padx=(0, 10))
            
            time_val = e.get('due_time', 'All Day')
            meta_lbl = ctk.CTkLabel(info_frame, text=f"// T-MIN: {time_val}", text_color="gray", font=("Consolas", 12))
            meta_lbl.pack(side="left", anchor="w")
