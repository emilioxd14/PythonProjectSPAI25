import customtkinter as ctk

# --- UI THEME SELECTION ---
# Options: "standard", "zen", "cyber"
UI_THEME = "standard" 

if UI_THEME == "zen":
    from modules.todo.todo_ui_zen import TodoFrame
elif UI_THEME == "cyber":
    from modules.todo.todo_ui_cyber import TodoFrame
else:
    from modules.todo.todo_ui import TodoFrame
# ---------------------------

if UI_THEME == "cyber":
    from modules.notes.notes_ui_cyber import StickyNotesFrame
    from modules.ai.ai_ui_cyber import AiChatFrame
    from modules.calendar.calendar_ui_cyber import CalendarFrame
else:
    from modules.notes.notes_ui import StickyNotesFrame
    from modules.ai.ai_ui import AiChatFrame
    from modules.calendar.calendar_ui import CalendarFrame



class MainLayout:
    def __init__(self, master, controllers):
        self.master = master
        self.controllers = controllers

        # Define Theme Colors
        self.is_cyber = (UI_THEME == "cyber")
        if self.is_cyber:
            self.colors = {
                "sidebar_bg": "#000000",
                "sidebar_radius": 0,
                "btn_text_color": "#00FF41", # Neon Green
                "btn_font": ("Consolas", 14),
                "indicator_color": "#FF00FF", # Neon Pink
                "hover_color": "#111111",
                "border_color": "#00FF41",
                "active_bg": "transparent", # Transparent for cyber
                "text_active": "#00FF41"
            }
        else:
             self.colors = {
                "sidebar_bg": None, # Default
                "sidebar_radius": 0, # Kept same as before but could be None
                "btn_text_color": ("gray10", "gray90"), # Standard text
                "btn_font": ("Roboto", 14), # Standard font
                "indicator_color": "#3B8ED0", # Twitter Blue
                "hover_color": ("gray70", "gray30"),
                "border_color": None, # No border
                "active_bg": ("#3B8ED0", "#1F6AA5"),
                "text_active": ("white", "white")
            }

        # 1. Setup Sidebar
        self._setup_sidebar()

        # 2. Setup Views
        self.todo_view = TodoFrame(master=master, controller=controllers['todo'])
        self.notes_view = StickyNotesFrame(master=master, controller=controllers['notes'])
        self.ai_view = AiChatFrame(master=master, ai_assistant=controllers['ai'])
        self.calendar_view = CalendarFrame(master=master, calendar_logic=controllers['calendar'])

        # 3. Show Default
        self.show_todo()

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.master, width=200, corner_radius=self.colors["sidebar_radius"], 
                                    fg_color=self.colors["sidebar_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # This pushes elements to fill height (Empuja los botones hacia arriba)
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Helper to create nav button
        def create_nav_btn(text, cmd):
            container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            
            indicator = ctk.CTkFrame(container, width=4, height=30, fg_color="transparent") # Start hidden
            indicator.pack(side="left")
            
            border_width = 1 if self.is_cyber else 0
            
            btn = ctk.CTkButton(container, text=text, command=cmd, 
                                fg_color="transparent", 
                                text_color=self.colors["btn_text_color"],
                                font=ctk.CTkFont(family=self.colors["btn_font"][0], size=self.colors["btn_font"][1]),
                                hover_color=self.colors["hover_color"],
                                corner_radius=0 if self.is_cyber else 8,
                                border_width=0, # Border applied on selection/hover logic if needed, simplify to 0 for now or dynamic
                                border_color=self.colors["border_color"])
            btn.pack(side="left", fill="x", expand=True, padx=5)
            
            return container, indicator, btn

        # --- BOTÓN 1: To-Do ---
        self.todo_container, self.todo_indicator, self.btn_todo = create_nav_btn("To-Do", self.show_todo)
        self.todo_container.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- BOTÓN 2: Notes ---
        self.notes_container, self.notes_indicator, self.btn_notes = create_nav_btn("Notes", self.show_notes)
        self.notes_container.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # --- BOTÓN 3: Calendar ---
        self.calendar_container, self.calendar_indicator, self.btn_calendar = create_nav_btn("Calendar", self.show_calendar)
        self.calendar_container.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # --- BOTÓN 4: AI Assistant ---
        self.ai_container, self.ai_indicator, self.btn_ai = create_nav_btn("AI Assistant", self.show_ai)
        self.ai_container.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        # Theme Toggle
        switch_color = "#00FF41" if self.is_cyber else "#3B8ED0"
        self.appearance_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self._toggle_theme,
                                               progress_color=switch_color,
                                               font=ctk.CTkFont(family=self.colors["btn_font"][0], size=12),
                                               text_color=self.colors["btn_text_color"])
        self.appearance_switch.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        self.appearance_switch.select() # Default to dark

    def _toggle_theme(self):
        if self.appearance_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def _update_nav_visuals(self, active_btn_name):
        # Reset all
        categories = [
            ("todo", self.btn_todo, self.todo_indicator),
            ("notes", self.btn_notes, self.notes_indicator),
            ("calendar", self.btn_calendar, self.calendar_indicator),
            ("ai", self.btn_ai, self.ai_indicator)
        ]

        for name, btn, ind in categories:
            if name == active_btn_name:
                # Active State
                ind.configure(fg_color=self.colors["indicator_color"])
                
                if self.is_cyber:
                     # Cyber: Transparent bg, Border visible, Text Color same
                     btn.configure(fg_color="transparent", border_width=1, border_color=self.colors["border_color"])
                else:
                     # Standard: Blue bg, White text
                     btn.configure(fg_color=self.colors["active_bg"], text_color=self.colors["text_active"])
            else:
                # Inactive State
                ind.configure(fg_color="transparent")
                btn.configure(fg_color="transparent", border_width=0, text_color=self.colors["btn_text_color"])


    def show_todo(self):
        self.notes_view.grid_forget()
        self.ai_view.grid_forget()
        self.calendar_view.grid_forget()
        self.todo_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self._update_nav_visuals("todo")

    def show_notes(self):
        self.todo_view.grid_forget()
        self.ai_view.grid_forget()
        self.calendar_view.grid_forget()
        self.notes_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self._update_nav_visuals("notes")

    def show_calendar(self):
        self.todo_view.grid_forget()
        self.notes_view.grid_forget() 
        self.ai_view.grid_forget()
        self.calendar_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self._update_nav_visuals("calendar")

    def show_ai(self):
        self.todo_view.grid_forget()
        self.notes_view.grid_forget()
        self.calendar_view.grid_forget()
        self.ai_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self._update_nav_visuals("ai")