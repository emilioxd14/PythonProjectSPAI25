import customtkinter as ctk
import datetime

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        # --- Cyber Design Tokens ---
        self.font_mono = ctk.CTkFont(family="Consolas", size=14)
        self.font_big_mono = ctk.CTkFont(family="Consolas", size=24, weight="bold")
        self.font_small_mono = ctk.CTkFont(family="Consolas", size=12)
        
        self.color_bg = "black"
        self.color_neon_green = "#00FF41" # Matrix Green
        self.color_neon_cyan = "#00FFFF"
        self.color_neon_pink = "#FF00FF"
        self.color_dim_red = "#550000"
        self.color_text = self.color_neon_green

        self.configure(fg_color=self.color_bg)

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header (System Status)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="> SYSTEM.TASKS.INIT()", 
                                        text_color=self.color_neon_cyan, font=self.font_big_mono)
        self.title_label.pack(side="left")

        # View Toggle (Terminal Tabs)
        self.view_toggle = ctk.CTkSegmentedButton(self.header_frame, 
                                                  values=["ACTV", "HIST"],
                                                  command=self._switch_view,
                                                  font=self.font_mono,
                                                  corner_radius=0,
                                                  fg_color=self.color_bg,
                                                  selected_color=self.color_neon_green,
                                                  selected_hover_color=self.color_neon_green,
                                                  unselected_color=self.color_bg,
                                                  unselected_hover_color="#111111",
                                                  text_color=("white", "black")) # Black text when selected (Green bg)
        self.view_toggle.set("ACTV")
        self.view_toggle.pack(side="right")
        
        # Border for toggle
        self.view_toggle.configure(border_width=1, border_color=self.color_neon_green)

        # 2. Command Input
        self.input_frame = ctk.CTkFrame(self, fg_color=self.color_bg, corner_radius=0, 
                                        border_width=2, border_color=self.color_neon_green)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.input_frame, text=">", font=self.font_mono, text_color=self.color_neon_green).grid(row=0, column=0, padx=(10,0))

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="ENTER_MISSION_OBJECTIVE...", 
                                  font=self.font_mono, border_width=0, fg_color="transparent",
                                  placeholder_text_color="#005500", text_color=self.color_neon_green)
        self.entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_new_task())

        # Controls
        self.controls_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=2, padx=(0, 10))

        # Schedule
        self.selected_date = None
        self.selected_time = None
        self.schedule_btn = ctk.CTkButton(self.controls_frame, text="[T-MINUS]", width=90,
                                          font=self.font_mono,
                                          fg_color="transparent", hover_color="#111111",
                                          border_width=1, border_color=self.color_neon_cyan,
                                          text_color=self.color_neon_cyan,
                                          corner_radius=0,
                                          command=self.open_date_picker)
        self.schedule_btn.pack(side="left", padx=5)

        # Priority
        self.priority_menu = ctk.CTkOptionMenu(self.controls_frame, values=["High", "Medium", "Low"], 
                                               width=90,
                                               font=self.font_mono,
                                               fg_color="transparent",
                                               button_color="#111111",
                                               button_hover_color="#222222",
                                               text_color=self.color_neon_pink,
                                               dropdown_font=self.font_mono,
                                               dropdown_fg_color="black",
                                               dropdown_text_color=self.color_neon_pink,
                                               corner_radius=0)
        self.priority_menu.set("Medium")  # We'll stick to text values, maybe color code text
        self.priority_menu.pack(side="left", padx=5)
        
        # Border hack for OptionMenu
        # CustomTKinter OptionMenu borders are tricky, assume valid simple look

        # Add Button
        self.add_button = ctk.CTkButton(self.controls_frame, text="[EXEC]", width=60,
                                        font=self.font_mono,
                                        fg_color=self.color_neon_green, hover_color="#00CC33",
                                        text_color="black",
                                        corner_radius=0,
                                        command=self.add_new_task)
        self.add_button.pack(side="left", padx=(5, 0))

        # 3. Main Display (Terminal Output)
        
        # ACTIVE
        self.active_frame = ctk.CTkScrollableFrame(self, fg_color="black", label_text="", corner_radius=0,
                                                   border_width=2, border_color=self.color_neon_green)
        # self.active_frame.grid(...)

        # COMPLETED
        self.completed_frame = ctk.CTkScrollableFrame(self, fg_color="#050505", label_text="", corner_radius=0,
                                                       border_width=2, border_color="gray30")
        
        # Clear Button
        self.clear_button = ctk.CTkButton(self, text="[PURGE_LOGS]", 
                                          fg_color="transparent", border_width=1, border_color=self.color_neon_pink,
                                          text_color=self.color_neon_pink, hover_color="#220000",
                                          font=self.font_mono, corner_radius=0,
                                          command=self.clear_history)

        self._switch_view("ACTV")
        self.refresh_view()

    # --- Logic ---

    def open_date_picker(self):
        from .date_time_dialog import DateTimePickerDialog
        # Ideally we'd have a Cyberpunk Dialog too, but we reuse for now
        DateTimePickerDialog(self, on_confirm=self.set_schedule, 
                             initial_date=self.selected_date, initial_time=self.selected_time)

    def set_schedule(self, date_str, time_str):
        self.selected_date = date_str
        self.selected_time = time_str
        self.schedule_btn.configure(text=f"[{date_str}]", fg_color=self.color_neon_cyan, text_color="black")

    def _switch_view(self, value):
        if value == "ACTV":
            self.completed_frame.grid_forget()
            self.clear_button.grid_forget()
            self.active_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
            self.active_frame.configure(border_color=self.color_neon_green)
        else:
            self.active_frame.grid_forget()
            self.completed_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
            self.clear_button.grid(row=3, column=0, pady=10)

    def add_new_task(self):
        text = self.entry.get()
        prio = self.priority_menu.get()
        if text:
            self.controller.add_task(text, priority=prio, due_date=self.selected_date, due_time=self.selected_time)
            self.entry.delete(0, "end")
            self.selected_date = None
            self.selected_time = None
            self.schedule_btn.configure(text="[T-MINUS]", fg_color="transparent", text_color=self.color_neon_cyan)
            self.refresh_view()

    def toggle_task(self, task_text):
        self.controller.toggle_task_status(task_text)
        self.refresh_view()

    def clear_history(self):
        self.controller.clear_completed_tasks()
        self.refresh_view()
        
    def start_edit(self, task, container):
         # inline edit logic
        for widget in container.winfo_children():
            widget.destroy()
            
        lbl = ctk.CTkLabel(container, text="> REWRITING:", font=self.font_small_mono, text_color=self.color_neon_green)
        lbl.pack(side="left")
        
        entry = ctk.CTkEntry(container, font=self.font_mono, height=28, 
                             fg_color="black", text_color=self.color_neon_green,
                             border_width=1, border_color=self.color_neon_green, corner_radius=0)
        entry.insert(0, task['text'])
        entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

        save_btn = ctk.CTkButton(container, text="[SAVE]", width=50, height=28,
                                  fg_color=self.color_neon_green, text_color="black", corner_radius=0,
                                  font=self.font_mono,
                                  command=lambda: self.save_edit(
                                      task['text'], 
                                      entry.get(), 
                                      task.get('priority'), 
                                      task.get('due_date'), 
                                      task.get('due_time')
                                  ))
        save_btn.pack(side="right")

    def save_edit(self, old_text, new_text, new_prio, new_date, new_time):
        if new_text and new_text.strip():
            self.controller.update_task(old_text, new_text, new_prio, new_date, new_time)
        self.refresh_view()

    def refresh_view(self):
        for w in self.active_frame.winfo_children(): w.destroy()
        for w in self.completed_frame.winfo_children(): w.destroy()

        tasks = self.controller.get_tasks()
        
        # Empty State
        active = [t for t in tasks if not t.get('completed')]
        if not active:
             ctk.CTkLabel(self.active_frame, text="> ALL SYSTEMS NORMAL.\n> NO THREATS DETECTED.", 
                          font=self.font_mono, justify="center",
                          text_color="#005500").pack(pady=40)

        for task in tasks:
            target = self.completed_frame if task.get('completed') else self.active_frame
            self._draw_task_card(target, task)

    def _draw_task_card(self, parent, task):
        is_done = task.get('completed')
        
        # Styling
        border_col = self.color_neon_green 
        text_col = self.color_neon_green
        bg_col = "transparent"
        
        prio = task.get('priority', 'Medium')
        
        if is_done:
            border_col = "gray30"
            text_col = "gray50"
        elif prio == "High":
            border_col = self.color_neon_pink
        elif prio == "Low":
            border_col = self.color_neon_cyan

        card = ctk.CTkFrame(parent, fg_color=bg_col, corner_radius=0, 
                            border_width=1, border_color=border_col)
        card.pack(pady=2, padx=5, fill="x")

        # Layout
        # [ ] Task Text ........... [Due] [Edit]
        
        # Checkbox replacement: A button [X] or [ ]
        # let's use a button that looks like a checkbox in terminal
        check_text = "[X]" if is_done else "[ ]"
        check_fg = "transparent"
        check_hover = "#222222"
        check_text_col = text_col
        
        check_btn = ctk.CTkButton(card, text=check_text, width=40, height=30,
                                  font=self.font_mono,
                                  fg_color=check_fg, hover_color=check_hover, text_color=check_text_col,
                                  corner_radius=0,
                                  command=lambda t=task['text']: self.toggle_task(t))
        check_btn.pack(side="left", padx=(5, 0))

        # Text Frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True, pady=5)
        
        # Task Text
        txt_font = self.font_mono
        if is_done:
            # No strikethrough in ctk, stick to color dimming
            pass
            
        lbl = ctk.CTkLabel(content, text=task['text'], font=txt_font, text_color=text_col, anchor="w")
        lbl.pack(fill="x")
        
        # Metadata
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.pack(side="right", padx=10)
        
        if task.get('due_date'):
            d = task['due_date']
            t = task.get('due_time', '')
            # T: 2023-10-20
            ctk.CTkLabel(meta_frame, text=f"T:{d} {t}", font=self.font_small_mono, text_color=border_col).pack(side="left", padx=5)

        if not is_done:
            edit_btn = ctk.CTkButton(meta_frame, text="[EDIT]", width=50, height=20,
                                     font=self.font_small_mono,
                                     fg_color="transparent", hover_color="#222222", text_color=self.color_neon_cyan,
                                     corner_radius=0,
                                     command=lambda t=task, c=content: self.start_edit(t, c))
            edit_btn.pack(side="left")
