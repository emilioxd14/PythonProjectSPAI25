import customtkinter as ctk
import datetime

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller

        # --- Zen Design Tokens ---
        self.font_main = ctk.CTkFont(family="Roboto", size=14)
        self.font_bold = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.font_title = ctk.CTkFont(family="Roboto", size=28, weight="bold")
        self.font_sub = ctk.CTkFont(family="Roboto", size=12)
        
        self.color_accent = "#667EEA" # Soft Indigo
        self.color_danger = "#E57373" # Soft Red
        self.color_card_light = "white"
        self.color_card_dark = "#2B2B2B"
        
        self.radius_large = 20
        self.radius_small = 10

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Content Area

        # 1. Header (Airy & Clean)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="My Tasks", font=self.font_title)
        self.title_label.pack(side="left")

        # View Switcher (Pill Style)
        self.view_toggle = ctk.CTkSegmentedButton(self.header_frame, 
                                                  values=["Active", "History"],
                                                  command=self._switch_view,
                                                  font=self.font_bold,
                                                  corner_radius=self.radius_large,
                                                  fg_color=("gray90", "gray20"),
                                                  selected_color=self.color_accent,
                                                  selected_hover_color=self.color_accent)
        self.view_toggle.set("Active")
        self.view_toggle.pack(side="right")

        # 2. Input Area (Floating Pill)
        self.input_frame = ctk.CTkFrame(self, fg_color=("white", "gray17"), corner_radius=self.radius_large)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Entry
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="What needs to be done?", 
                                  font=self.font_main, border_width=0, fg_color="transparent")
        self.entry.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_new_task())

        # Controls Container (Right side of input)
        self.controls_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=1, padx=(0, 10))

        # Date/Time Picker
        self.selected_date = None
        self.selected_time = None
        self.schedule_btn = ctk.CTkButton(self.controls_frame, text="Schedule", width=90, height=32,
                                          font=self.font_sub,
                                          fg_color=("gray95", "gray25"), 
                                          text_color=("gray40", "gray80"),
                                          hover_color=("gray90", "gray30"),
                                          corner_radius=self.radius_large,
                                          command=self.open_date_picker)
        self.schedule_btn.pack(side="left", padx=5)

        # Priority
        self.priority_menu = ctk.CTkOptionMenu(self.controls_frame, values=["High", "Medium", "Low"], 
                                               width=90, height=32,
                                               font=self.font_sub,
                                               fg_color=("gray95", "gray25"),
                                               button_color=("gray90", "gray30"),
                                               text_color=("gray40", "gray80"),
                                               corner_radius=self.radius_large)
        self.priority_menu.set("Medium")
        self.priority_menu.pack(side="left", padx=5)

        # Add Button (Circle/Icon style or Pill)
        self.add_button = ctk.CTkButton(self.controls_frame, text="+", width=40, height=32,
                                        font=ctk.CTkFont(size=20, weight="bold"),
                                        fg_color=self.color_accent, hover_color="#5A67D8",
                                        corner_radius=self.radius_large,
                                        command=self.add_new_task)
        self.add_button.pack(side="left", padx=(5, 10))

        # 3. Content Area
        self.active_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="")
        # self.active_frame.grid(...) # Dynamic

        self.completed_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="")
        # self.completed_frame.grid(...) # Dynamic

        # Clear Button (Floating at bottom right or just at bottom)
        self.clear_button = ctk.CTkButton(self, text="Clear History", 
                                          fg_color="transparent", 
                                          text_color=self.color_danger,
                                          hover_color=("gray95", "gray20"),
                                          font=self.font_sub,
                                          command=self.clear_history)

        # Initial Load
        self._switch_view("Active")
        self.refresh_view()

    # --- Logic Methods (Contract Implementation) ---

    def open_date_picker(self):
        from .date_time_dialog import DateTimePickerDialog
        DateTimePickerDialog(self, on_confirm=self.set_schedule, 
                             initial_date=self.selected_date, initial_time=self.selected_time)

    def set_schedule(self, date_str, time_str):
        self.selected_date = date_str
        self.selected_time = time_str
        self.schedule_btn.configure(text=f"{date_str}", fg_color=self.color_accent, text_color="white")

    def _switch_view(self, value):
        if value == "Active":
            self.completed_frame.grid_forget()
            self.clear_button.grid_forget()
            self.active_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        else:
            self.active_frame.grid_forget()
            self.completed_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
            self.clear_button.grid(row=3, column=0, pady=10)

    def add_new_task(self):
        text = self.entry.get()
        priority = self.priority_menu.get()
        if text:
            self.controller.add_task(text, priority=priority, due_date=self.selected_date, due_time=self.selected_time)
            self.entry.delete(0, "end")
            
            # Reset
            self.selected_date = None
            self.selected_time = None
            self.schedule_btn.configure(text="Schedule", fg_color=("gray95", "gray25"), text_color=("gray40", "gray80"))
            
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
        
        entry = ctk.CTkEntry(container, font=self.font_main, height=35)
        entry.insert(0, task['text'])
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Save Action
        save_icon = ctk.CTkButton(container, text="Save", width=60, height=35,
                                  fg_color=self.color_accent, corner_radius=self.radius_small,
                                  command=lambda: self.save_edit(
                                      task['text'], 
                                      entry.get(), 
                                      task.get('priority'), 
                                      task.get('due_date'), 
                                      task.get('due_time')
                                  ))
        save_icon.pack(side="right")

    def save_edit(self, old_text, new_text, new_prio, new_date, new_time):
        if new_text and new_text.strip():
            self.controller.update_task(old_text, new_text, new_prio, new_date, new_time)
        self.refresh_view()

    def refresh_view(self):
        # Clear
        for widget in self.active_frame.winfo_children(): widget.destroy()
        for widget in self.completed_frame.winfo_children(): widget.destroy()

        tasks = self.controller.get_tasks()
        
        # Empty State
        active = [t for t in tasks if not t.get('completed')]
        if not active:
             ctk.CTkLabel(self.active_frame, text="All caught up! Time to relax.", 
                          font=ctk.CTkFont(family="Roboto", size=16, slant="italic"),
                          text_color="gray").pack(pady=40)

        for task in tasks:
            target = self.completed_frame if task.get('completed') else self.active_frame
            self._draw_task_card(target, task)

    def _draw_task_card(self, parent, task):
        # Zen Card
        card = ctk.CTkFrame(parent, fg_color=(self.color_card_light, self.color_card_dark), 
                            corner_radius=self.radius_small)
        card.pack(pady=8, padx=10, fill="x") # More Breathable

        # Priority Strip
        prio = task.get('priority', 'Medium')
        prio_color = {"High": self.color_danger, "Medium": "#F6AD55", "Low": "#68D391"}.get(prio, "#F6AD55")
        
        ctk.CTkFrame(card, width=6, height=45, fg_color=prio_color, corner_radius=3).pack(side="left", padx=10, pady=10)

        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True, pady=10)

        # Check & Text
        # Custom Checkbox Style?
        is_done = task.get('completed')
        chk = ctk.CTkCheckBox(content, text=task['text'], 
                              font=self.font_main if not is_done else ctk.CTkFont(family="Roboto", size=14, slant="italic", overstrike=True),
                              text_color="gray" if is_done else ("black", "white"),
                              checkbox_width=22, checkbox_height=22, corner_radius=11, # Round checkbox
                              fg_color=self.color_accent, hover_color=self.color_accent,
                              command=lambda t=task['text']: self.toggle_task(t))
        if is_done: chk.select()
        chk.pack(side="left", fill="x", expand=True)

        # Metadata (Right aligned)
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.pack(side="right", padx=15)

        if task.get('due_date'):
            d = task['due_date']
            t = task.get('due_time', '')
            lbl = ctk.CTkLabel(meta_frame, text=f"{d} {t}", font=self.font_sub, text_color="gray")
            lbl.pack(anchor="e")
        
        # Edit Icon (Only if active)
        if not is_done:
            edit_btn = ctk.CTkButton(meta_frame, text="✎", width=30, height=30,
                                     fg_color="transparent", text_color="gray", hover_color=("gray90", "gray30"),
                                     font=ctk.CTkFont(size=16),
                                     command=lambda t=task, c=content: self.start_edit(t, c))
            edit_btn.pack(anchor="e")
