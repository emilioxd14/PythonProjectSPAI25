import customtkinter as ctk

class TodoFrame(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        # 1. Inject Controller (The Brain)
        self.controller = controller

        # Layout Configuration
        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # Input area
        self.grid_rowconfigure(2, weight=0) # Toggle button (Should NOT expand)
        self.grid_rowconfigure(3, weight=1) # Main content area (Task List) - THIS SHOULD EXPAND

        # Title
        self.title_label = ctk.CTkLabel(self, text="My Tasks", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Add a new task...")
        self.entry.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_new_task())

        # NEW: Schedule Button (Replaces Date/Time Entries)
        self.schedule_btn = ctk.CTkButton(self.input_frame, text="📅 Schedule", width=100, 
                                          fg_color=("gray85", "gray25"), text_color=("black", "white"),
                                          command=self.open_date_picker)
        self.schedule_btn.grid(row=0, column=1, padx=(0, 10), pady=0)
        
        # Hidden vars to store selection
        self.selected_date = None
        self.selected_time = None
        # ----------------

        self.priority_menu = ctk.CTkOptionMenu(self.input_frame, values=["High", "Medium", "Low"], width=100)
        self.priority_menu.set("Medium")
        self.priority_menu.grid(row=0, column=3, padx=(0, 10), pady=0)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add", command=self.add_new_task, width=60)
        self.add_button.grid(row=0, column=4, padx=0, pady=0)

        # View Toggle (Segmented Button)
        self.view_toggle = ctk.CTkSegmentedButton(self, values=["Active Tasks", "History"],
                                                  command=self._switch_view)
        self.view_toggle.set("Active Tasks")
        self.view_toggle.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="n") # Top of content area

        # Active Tasks Frame
        self.active_frame = ctk.CTkScrollableFrame(self, label_text="")
        # self.active_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew") # Setup dynamically

        # Completed Tasks Frame
        self.completed_frame = ctk.CTkScrollableFrame(self, label_text="")
        # self.completed_frame.grid(...) # Setup dynamically

        # Clear Button
        self.clear_button = ctk.CTkButton(self, text="Clear Completed", fg_color="#D32F2F", hover_color="#B71C1C",
                                          command=self.clear_history)
        
        # Initial View Setup
        self._switch_view("Active Tasks")
        self.refresh_view()

    def open_date_picker(self):
        from .date_time_dialog import DateTimePickerDialog
        DateTimePickerDialog(self, on_confirm=self.set_schedule, 
                             initial_date=self.selected_date, initial_time=self.selected_time)

    def set_schedule(self, date_str, time_str):
        self.selected_date = date_str
        self.selected_time = time_str
        # Visual Feedback
        self.schedule_btn.configure(text=f"{date_str} {time_str}", fg_color="#2CC985") # Green indicates set

    def _switch_view(self, value):
        """Toggles between Active and History views."""
        if value == "Active Tasks":
            self.completed_frame.grid_forget()
            self.clear_button.grid_forget()
            
            # Place Active Frame
            self.active_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
            self.grid_rowconfigure(3, weight=1)
            
        else:
            self.active_frame.grid_forget()
            
            # Place Completed Frame
            self.completed_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
            self.grid_rowconfigure(3, weight=1)
            
            # Show Clear Button only in History view
            self.clear_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")


    def add_new_task(self):
        text = self.entry.get()
        priority = self.priority_menu.get()
        
        if text:
            # Send to controller
            self.controller.add_task(text, priority=priority, due_date=self.selected_date, due_time=self.selected_time)
            self.entry.delete(0, "end")
            
            # Reset Schedule
            self.selected_date = None
            self.selected_time = None
            self.schedule_btn.configure(text="📅 Schedule", fg_color=("gray85", "gray25"))
            
            self.refresh_view()

    def toggle_task(self, task_text):
        """User clicked a checkbox. Tell controller to flip the status."""
        self.controller.toggle_task_status(task_text)
        self.refresh_view()

    def clear_history(self):
        """Tell controller to delete all completed items."""
        self.controller.clear_completed_tasks()
        self.refresh_view()

    def start_edit(self, task, container):
        """Convierte la tarjeta en un formulario de edición completo."""
        for widget in container.winfo_children():
            widget.destroy()
        
        # 1. Campo de Texto
        edit_entry = ctk.CTkEntry(container, width=140)
        edit_entry.insert(0, task['text'])
        edit_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # 2. Schedule Button (Replaces Date/Time Entries in Edit Mode)
        # Storing temporary state for the edit is tricky in lambda. 
        # Helper class or closure is cleaner. Let's use a small helper mechanism or just a button that updates itself.
        # Ideally we open the same dialog.
        
        current_date = task.get('due_date')
        current_time = task.get('due_time')
        
        btn_text = f"{current_date} {current_time}" if current_date else "📅 Schedule"
        
        # We need a mutable container for the dialog callback to write to
        state = {"date": current_date, "time": current_time}
        
        def on_edit_confirm(d, t):
            state['date'] = d
            state['time'] = t
            sched_btn.configure(text=f"{d} {t}", fg_color="#2CC985")

        def open_edit_picker():
             from .date_time_dialog import DateTimePickerDialog
             DateTimePickerDialog(self, on_confirm=on_edit_confirm, 
                                  initial_date=state['date'], initial_time=state['time'])

        sched_btn = ctk.CTkButton(container, text=btn_text, width=100, 
                                  fg_color="#2CC985" if current_date else ("gray85", "gray25"),
                                  text_color=("black", "white"),
                                  command=open_edit_picker)
        sched_btn.pack(side="left", padx=(0, 5))

        # 4. Selector de Prioridad
        current_prio = task.get('priority', 'Medium')
        prio_var = ctk.StringVar(value=current_prio)
        prio_menu = ctk.CTkOptionMenu(container, values=["High", "Medium", "Low"], 
                                      variable=prio_var, width=80)
        prio_menu.pack(side="left", padx=(0, 5))
        
        # 5. Botón Guardar
        save_btn = ctk.CTkButton(container, text="Save", width=50, fg_color="#2CC985", hover_color="#26A66B",
                                 command=lambda: self.save_edit(
                                     task['text'],       
                                     edit_entry.get(),   
                                     prio_var.get(),     
                                     state['date'],
                                     state['time']
                                 ))
        save_btn.pack(side="right")

    def save_edit(self, old_text, new_text, new_priority, new_date, new_time):
        """Recibe los datos del formulario y llama al controlador."""
        if new_text and new_text.strip():
            self.controller.update_task(old_text, new_text, new_priority, new_date, new_time)
        
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

        # 3. Empty State (Active Only)
        active_tasks = [t for t in tasks if not t.get('completed')]
        if not active_tasks:
            empty_label = ctk.CTkLabel(self.active_frame, text="No active tasks! Relax or add a new one.", 
                                       text_color="gray", font=ctk.CTkFont(slant="italic"))
            empty_label.pack(pady=20, expand=True)

        # 4. Draw Tasks (Cards)
        for task in tasks:
            target_frame = self.completed_frame if task.get('completed') else self.active_frame
            
            # Card Style
            card = ctk.CTkFrame(target_frame, corner_radius=10, border_width=1, border_color="gray40", 
                                fg_color=("white", "#2B2B2B"))
            card.pack(pady=5, fill="x", padx=5)

            # Priority Indicator
            prio = task.get('priority', 'Medium')
            color = {"High": "#FF5252", "Medium": "#FFB142", "Low": "#33D9B2"}.get(prio, "#FFB142")
            prio_tag = ctk.CTkFrame(card, width=12, height=12, fg_color=color, corner_radius=6)
            prio_tag.pack(side="left", padx=(10, 5))

            # Inner Container for Text/Check
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(side="left", fill="x", expand=True)

            # Checkbox
            chk = ctk.CTkCheckBox(content_frame, text=task['text'], 
                                   command=lambda t=task['text']: self.toggle_task(t),
                                   font=ctk.CTkFont(size=14))
            if task.get('completed'):
                chk.select()
                chk.configure(text_color="gray")
            chk.pack(side="left", fill="x", expand=True, pady=10)

            # Date & Time Display
            date_str = task.get('due_date')
            time_str = task.get('due_time')
            
            full_date_text = ""
            if date_str:
                full_date_text += f"📅 {date_str}"
            if time_str:
                full_date_text += f" 🕒 {time_str}"
                
            if full_date_text:
               date_lbl = ctk.CTkLabel(card, text=full_date_text, text_color="gray", font=ctk.CTkFont(size=12))
               date_lbl.pack(side="right", padx=(5, 10))

            # Edit Button (Active Only)
            if not task.get('completed'):
                edit_btn = ctk.CTkButton(card, text="✎", width=30, height=30, 
                                         fg_color="transparent", hover_color=("gray85", "gray30"),
                                         text_color=("black", "white"),
                                         command=lambda t=task, c=content_frame: self.start_edit(t, c))
                edit_btn.pack(side="right", padx=10)
