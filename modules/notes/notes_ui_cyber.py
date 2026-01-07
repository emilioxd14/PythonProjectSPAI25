import customtkinter as ctk

class StickyNote(ctk.CTkFrame):
    """Represents a single data block with neon border options."""

    def __init__(self, master, text_content="", color="#00FFFF", on_delete=None, on_change=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_change = on_change
        self.current_color = color # This will now be the BORDER color
        
        # Cyber Styling
        # fg_color is almost black
        # border_color is the variable neon color
        self.configure(fg_color="#050505", corner_radius=0, width=200, height=220,
                       border_width=1, border_color=self.current_color)
        self.pack_propagate(False)

        # 1. HEADER / DELETE (Top)
        # A small header bar for the 'window' feel
        header = ctk.CTkFrame(self, fg_color="#111111", height=25, corner_radius=0)
        header.pack(fill="x", side="top", padx=1, pady=1)
        
        # ID Label (Decoration)
        ctk.CTkLabel(header, text="> ID_REF", font=("Consolas", 10), text_color="gray40").pack(side="left", padx=5)

        self.delete_btn = ctk.CTkButton(
            header, text="[X]", width=25, height=25,
            font=("Consolas", 12, "bold"),
            fg_color="transparent", text_color=self.current_color, hover_color="#330000",
            command=on_delete, corner_radius=0
        )
        self.delete_btn.pack(side="right")

        # 2. COLOR PICKER (Bottom - changes Border)
        self.color_bar = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.color_bar.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Neon Colors: Cyan, Green, Pink
        colors = [("#00FFFF", "Cyan"), ("#00FF41", "Green"), ("#FF00FF", "Pink")]
        for hex_color, name in colors:
            btn = ctk.CTkButton(self.color_bar, text="", width=12, height=12, 
                                fg_color=hex_color, corner_radius=0,
                                hover_color=hex_color,
                                border_width=0,
                                command=lambda c=hex_color: self.change_color(c))
            btn.pack(side="left", padx=5)

        # 3. TEXT AREA
        self.textbox = ctk.CTkTextbox(
            self, fg_color="transparent", text_color="white",
            font=("Consolas", 14), wrap="word",
            border_width=0
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=(5, 5))
        self.textbox.insert("0.0", text_content)

    def change_color(self, new_color):
        self.current_color = new_color
        self.configure(border_color=new_color)
        self.delete_btn.configure(text_color=new_color)
        if self.on_change:
            self.on_change()

    def get_data(self):
        """Returns the note's data as a dictionary."""
        try:
            text = self.textbox.get("0.0", "end").strip()
            # We map the border color back to the 'color' field so it persists
            return {"text": text, "color": self.current_color}
        except ValueError:
            return {"text": "", "color": self.current_color}


class StickyNotesFrame(ctk.CTkFrame):
    """The Cyberpunk Data Grid."""

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller
        self.notes_list = []
        self._resize_timer = None
        
        # Main BG
        self.configure(fg_color="black")

        # Top Bar
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(self.top_bar, text="> DATA_FRAGMENTS", 
                                        font=("Consolas", 24, "bold"), text_color="#00FF41")
        self.title_label.pack(side="left")

        # Add Button
        self.add_button = ctk.CTkButton(self.top_bar, text="[ + NEW_DATA ]", 
                                        font=("Consolas", 14, "bold"),
                                        fg_color="transparent", border_width=1, border_color="#00FF41",
                                        text_color="#00FF41", hover_color="#003300", corner_radius=0,
                                        command=lambda: self.add_note(save=True))
        self.add_button.pack(side="right")

        # Scrollable Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="", 
                                                   fg_color="black", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Bind resize event
        self.bind("<Configure>", self._on_resize)

        # Load initial data
        self.load_notes()

    def _on_resize(self, event):
        """Simple debounce for resize events."""
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(100, self.refresh_grid)

    def _get_grid_pos(self, index):
        """Calculates row and column based on current width."""
        width = self.winfo_width()
        cols = 2 if width < 600 else 3
        
        # Configure grid columns
        for i in range(3):
            if i < cols:
                self.scroll_frame.grid_columnconfigure(i, weight=1)
            else:
                self.scroll_frame.grid_columnconfigure(i, weight=0)
                
        row = index // cols
        col = index % cols
        return row, col

    def add_note(self, note_data=None, save=True):
        if note_data is None:
            note_data = {"text": "", "color": "#00FFFF"} # Default Cyan
        
        if isinstance(note_data, str):
            note_data = {"text": note_data, "color": "#00FFFF"}

        # Map old colors to new neon ones if switching themes
        # Yellow -> Cyan, Blue -> Green, Pink -> Pink
        color_map = {
            "#F9F871": "#00FFFF", # Yellow -> Cyan
            "#81ECEC": "#00FF41", # Blue -> Green
            "#FAB1A0": "#FF00FF"  # Pink -> Pink
        }
        c = note_data.get('color', "#00FFFF")
        if c in color_map:
            c = color_map[c]

        new_note = StickyNote(
            self.scroll_frame,
            text_content=note_data.get('text', ""),
            color=c,
            on_delete=lambda: self.delete_note_from_ui(new_note),
            on_change=lambda: self.save_notes()
        )

        new_note.textbox.bind("<KeyRelease>", lambda event: self.save_notes())

        self.notes_list.append(new_note)
        self.refresh_grid()

        if save:
            self.save_notes()

    def delete_note_from_ui(self, note_widget):
        note_widget.destroy()
        if note_widget in self.notes_list:
            self.notes_list.remove(note_widget)
        self.refresh_grid()
        self.save_notes()

    def refresh_grid(self):
        for index, note in enumerate(self.notes_list):
            note.grid_forget()
            row, col = self._get_grid_pos(index)
            note.grid(row=row, column=col, padx=10, pady=10)

    def save_notes(self):
        data = [note.get_data() for note in self.notes_list]
        self.controller.update_all_notes(data)

    def load_notes(self):
        data = self.controller.get_notes()
        for item in data:
            self.add_note(item, save=False)
