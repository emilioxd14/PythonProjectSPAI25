import customtkinter as ctk
import datetime
import calendar

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, master, calendar_logic, **kwargs):
        super().__init__(master, **kwargs)
        self.logic = calendar_logic
        self.current_date = datetime.date.today()
        self.view_mode = "Month" # Month, Week, Agenda
        self.last_view_mode = None
        self.week_widgets = [] # Stores references to static week view widgets

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self.header_frame.grid_columnconfigure(2, weight=1) # Spacer

        # Navigation
        self.prev_btn = ctk.CTkButton(self.header_frame, text="<", width=40, command=self.go_prev)
        self.prev_btn.pack(side="left", padx=(0, 10))
        
        self.next_btn = ctk.CTkButton(self.header_frame, text=">", width=40, command=self.go_next)
        self.next_btn.pack(side="left", padx=(0, 20))

        # Current Date Label
        self.date_label = ctk.CTkLabel(self.header_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.date_label.pack(side="left")

        # View Switcher
        self.view_switcher = ctk.CTkSegmentedButton(self.header_frame, 
                                                    values=["Month", "Week", "Day"],
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
        # Only destroy if the view mode has actually changed
        if self.view_mode != self.last_view_mode:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.last_view_mode = self.view_mode
            
            # Reset week widgets cache if we left week view (optional, but cleaner ensures we don't hold stale refs)
            if self.view_mode != "Week":
                self.week_widgets = []

        if self.view_mode == "Month":
            # Month view is not optimized for persistence yet, so we clear it explicitly if we are just navigating (mode didn't change)
            if self.content_frame.winfo_children():
                 for widget in self.content_frame.winfo_children(): widget.destroy()
            self._render_month_view()
        elif self.view_mode == "Week":
            self._render_week_view()
        elif self.view_mode == "Day":
            # Day view is not optimized for persistence yet
            if self.content_frame.winfo_children():
                 for widget in self.content_frame.winfo_children(): widget.destroy()
            self._render_day_view()

    # --- HELPER FOR MODULARITY ---
    def _create_task_card(self, parent, event, compact=False):
        """
        Creates a standardized task card. 
        Modify this method to change the look of tasks everywhere.
        """
        # Determine Color
        prio = event.get('priority', 'Medium')
        color = {"High": "#FF5252", "Medium": "#FFB142", "Low": "#33D9B2"}.get(prio, "#FFB142")
        
        if compact:
            # Simple Label for Week View
            txt = event['text']
            if len(txt) > 20: txt = txt[:18] + "..."
            lbl = ctk.CTkLabel(parent, text=txt, anchor="w", fg_color=("white", "gray20"), corner_radius=5)
            lbl.pack(fill="x", pady=2)
            return lbl
        else:
            # Detailed Card for Day View
            card = ctk.CTkFrame(parent, fg_color=("white", "#2B2B2B"), corner_radius=5, height=50)
            card.pack_propagate(False)
            card.pack(fill="x", pady=5, padx=10, anchor="n")
            
            # Color Strip
            ctk.CTkFrame(card, width=5, fg_color=color).pack(side="left", fill="y", padx=(0, 5))
            
            # Content
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, pady=2)
            
            title = ctk.CTkLabel(info_frame, text=event['text'], font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
            title.pack(side="left", padx=(0, 10))
            
            time_val = event.get('due_time', 'All Day')
            ctk.CTkLabel(info_frame, text=f"| 🕒 {time_val}", text_color="gray", font=ctk.CTkFont(size=12)).pack(side="left")
            return card

    # --- VIEWS ---

    def _render_month_view(self):
        # 1. Reset columns
        for i in range(10): 
            self.content_frame.grid_columnconfigure(i, weight=0)
        
        self.content_frame.grid_columnconfigure(0, weight=4)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.date_label.configure(text=self.current_date.strftime("%B %Y"))

        # --- OPTIMIZATION: Fetch Data Once ---
        days_in_month = calendar.monthrange(self.current_date.year, self.current_date.month)[1]
        start_date = datetime.date(self.current_date.year, self.current_date.month, 1)
        end_date = datetime.date(self.current_date.year, self.current_date.month, days_in_month)
        events_map = self.logic.get_events_dict(start_date, end_date)
        # -------------------------------------

        # Calendar Grid
        cal_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cal_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            cal_container.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(cal_container, text=day, text_color="gray").grid(row=0, column=i, pady=(0, 5))

        matrix = self.logic.get_month_matrix(self.current_date.year, self.current_date.month)
        
        for r, week in enumerate(matrix):
            cal_container.grid_rowconfigure(r+1, weight=1)
            for c, day in enumerate(week):
                if day == 0:
                    continue
                
                date_obj = datetime.date(self.current_date.year, self.current_date.month, day)
                # Lookup events from map (Instant)
                events = events_map.get(date_obj, [])
                
                bg_color = ("white", "#2B2B2B")
                if date_obj == datetime.date.today():
                    bg_color = ("#E3F2FD", "#1E3A8A")
                
                day_card = ctk.CTkFrame(cal_container, fg_color=bg_color, corner_radius=10, border_width=1, border_color="gray40")
                day_card.grid(row=r+1, column=c, padx=2, pady=2, sticky="nsew")
                
                # Bindings
                day_card.bind("<Enter>", lambda e, ev=events: self.on_day_hover(ev))
                day_card.bind("<Leave>", lambda e: self.on_day_leave())
                day_card.bind("<Button-1>", lambda e, d=date_obj: self.on_day_click(d))
                
                num_lbl = ctk.CTkLabel(day_card, text=str(day), font=ctk.CTkFont(weight="bold"))
                num_lbl.place(relx=0.9, rely=0.1, anchor="ne")
                num_lbl.bind("<Button-1>", lambda e, d=date_obj: self.on_day_click(d))

                if events:
                    dot = ctk.CTkFrame(day_card, width=8, height=8, corner_radius=4, fg_color="#3B8ED0")
                    dot.place(relx=0.5, rely=0.7, anchor="center")

        # Sidebar
        sidebar = ctk.CTkFrame(self.content_frame, fg_color=("gray90", "gray20"), corner_radius=10)
        sidebar.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        ctk.CTkLabel(sidebar, text="Activity Preview", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.preview_panel = ctk.CTkLabel(sidebar, text="Hover over a day...", 
                                          text_color="gray", anchor="n", justify="left", wraplength=140)
        self.preview_panel.pack(padx=10, pady=10, fill="both", expand=True)

    def on_day_hover(self, events):
        if not events:
            self.preview_panel.configure(text="No tasks")
            return
        count = len(events)
        preview_text = f"{count} Tasks: " + ", ".join([t['text'] for t in events[:2]])
        if count > 2: preview_text += "..."
        self.preview_panel.configure(text=preview_text)

    def on_day_leave(self):
        self.preview_panel.configure(text="Hover over a day to see tasks...")

    def on_day_click(self, date_obj):
        self.current_date = date_obj
        self.view_switcher.set("Day")
        self.switch_view("Day")

    def _setup_week_view_structure(self):
        """
        Constructs the static layout for the week view ONCE.
        Creates 5 columns for Mon-Fri and a container for Sat-Sun.
        Populates self.week_widgets with references.
        """
        print("!!! ESTOY CARGANDO EL CÓDIGO NUEVO !!!")  # <--- Agrega esto
                
        self.content_frame.grid_rowconfigure(0, weight=2)
        self.content_frame.grid_rowconfigure(1, weight=1)
        
        # 1. Mon-Fri Columns
        for i in range(5):
            self.content_frame.grid_columnconfigure(i, weight=1)
            
            col_frame = ctk.CTkFrame(self.content_frame, corner_radius=5)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=2, pady=(0, 5))
            
            # Header
            header = ctk.CTkLabel(col_frame, text="", font=ctk.CTkFont(weight="bold"))
            header.pack(pady=5)
            
            # Events area
            scroll = ctk.CTkScrollableFrame(col_frame, label_text="", fg_color="transparent")
            scroll.pack(expand=True, fill="both", padx=2, pady=2)
            
            self.week_widgets.append({
                'col': col_frame,
                'header': header,
                'scroll': scroll
            })
            
        # 2. Weekend Container
        weekend_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        weekend_container.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=(5, 0))
        weekend_container.grid_columnconfigure(0, weight=1)
        weekend_container.grid_columnconfigure(1, weight=1)
        weekend_container.grid_rowconfigure(0, weight=1)
        
        # Sat-Sun Columns (Indices 5 and 6)
        for i in range(2):
            col_frame = ctk.CTkFrame(weekend_container, corner_radius=5)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=2)
            
            header = ctk.CTkLabel(col_frame, text="", font=ctk.CTkFont(weight="bold"))
            header.pack(pady=5)
            
            scroll = ctk.CTkScrollableFrame(col_frame, label_text="", fg_color="transparent")
            scroll.pack(expand=True, fill="both", padx=2, pady=2)
            
            self.week_widgets.append({
                'col': col_frame,
                'header': header,
                'scroll': scroll
            })

    def _render_week_view(self):
        week_dates = self.logic.get_week_dates(self.current_date)
        
        # Create structure if it doesn't exist
        if not self.week_widgets:
            self._setup_week_view_structure()
        
        # Fetch Data Once
        events_map = self.logic.get_events_dict(week_dates[0], week_dates[-1])

        start_str = week_dates[0].strftime("%b %d")
        end_str = week_dates[-1].strftime("%b %d")
        self.date_label.configure(text=f"{start_str} - {end_str}")

        # Update each column
        for i, widget_dict in enumerate(self.week_widgets):
            date_obj = week_dates[i]
            col_frame = widget_dict['col']
            header = widget_dict['header']
            scroll = widget_dict['scroll']
            
            # Update Header
            header.configure(text=date_obj.strftime("%a\n%d" if i < 5 else "%A %d"))
            
            # Update Highlight
            if date_obj == datetime.date.today():
                col_frame.configure(fg_color=("#E3F2FD", "#1E3A8A"))
            else:
                col_frame.configure(fg_color=("white", "gray17") if i >= 5 else "transparent") # Slightly different weekend bg or transparent? 
                # Original logic: 
                # Mon-Fri: transparent
                # Weekend: transparent
                # But inside weekend container:
                # col_frame was transparent.
                # Let's keep it consistent with original:
                if i < 5:
                    col_frame.configure(fg_color="transparent")
                else:
                    col_frame.configure(fg_color="transparent")

            # Update Events (Destroy ONLY task cards)
            for child in scroll.winfo_children():
                child.destroy()
                
            events = events_map.get(date_obj, [])
            for e in events:
                self._create_task_card(scroll, e, compact=True)

    def _render_day_view(self):
        current_day = self.current_date
        self.date_label.configure(text=f"Schedule for {current_day.strftime('%A, %b %d')}")
        
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        for r in range(1, 10):
            self.content_frame.grid_rowconfigure(r, weight=0)

        scroll = ctk.CTkScrollableFrame(self.content_frame)
        scroll.grid(row=0, column=0, columnspan=7, sticky="nsew")
        
        # Single day fetch is fast enough, but we could use the new method too
        events_map = self.logic.get_events_dict(current_day, current_day)
        events = events_map.get(current_day, [])
        
        if not events:
            ctk.CTkLabel(scroll, text="No events scheduled for this day.", text_color="gray").pack(pady=20)
            return
            
        for e in events:
            self._create_task_card(scroll, e, compact=False)