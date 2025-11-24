import customtkinter as ctk


class StickyNote(ctk.CTkFrame):
    """Represents a single yellow square note."""

    def __init__(self, master, text_content="", on_delete=None, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="#F9F871", corner_radius=10, width=200, height=200)
        self.pack_propagate(False)

        # Delete Button
        self.delete_btn = ctk.CTkButton(
            self, text="✕", width=25, height=25,
            fg_color="transparent", text_color="black", hover_color="#E0E060",
            command=on_delete
        )
        self.delete_btn.pack(anchor="ne", padx=5, pady=5)

        # Text Area
        self.textbox = ctk.CTkTextbox(
            self, fg_color="transparent", text_color="black",
            font=("Comic Sans MS", 14), wrap="word"
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.textbox.insert("0.0", text_content)

    def get_text(self):
        # Safety check: if widget is destroyed, return empty string
        try:
            return self.textbox.get("0.0", "end").strip()
        except ValueError:
            return ""


class StickyNotesFrame(ctk.CTkFrame):
    """The main 'Corkboard' area."""

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)

        self.controller = controller

        # Top Bar
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=20, pady=10)

        self.add_button = ctk.CTkButton(self.top_bar, text="+ New Note", command=lambda: self.add_note(save=True))
        self.add_button.pack(side="right")

        self.title_label = ctk.CTkLabel(self.top_bar, text="My Idea Board", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")

        # Scrollable Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        self.scroll_frame.grid_columnconfigure(2, weight=1)

        self.notes_list = []

        # Load initial data
        self.load_notes()

    def add_note(self, text="", save=True):
        """
        Creates a new note widget.
        :param text: The content of the note
        :param save: If True, saves to database immediately.
                     Set to False when loading existing notes to prevent recursion loops.
        """
        new_note = StickyNote(
            self.scroll_frame,
            text_content=text,
            on_delete=lambda: self.delete_note_from_ui(new_note)
        )

        # Bind key release to auto-save logic
        new_note.textbox.bind("<KeyRelease>", lambda event: self.save_notes())

        self.notes_list.append(new_note)
        self.refresh_grid()

        # --- FIX: Only save if this is a user action, not a load action ---
        if save:
            self.save_notes()

    def delete_note_from_ui(self, note_widget):
        note_widget.destroy()
        if note_widget in self.notes_list:
            self.notes_list.remove(note_widget)
        self.refresh_grid()
        self.save_notes()

    def refresh_grid(self):
        for note in self.notes_list:
            note.grid_forget()
        for index, note in enumerate(self.notes_list):
            row = index // 3
            col = index % 3
            note.grid(row=row, column=col, padx=10, pady=10)

    def save_notes(self):
        """Scrape text from UI and send to Controller"""
        data = [note.get_text() for note in self.notes_list]
        self.controller.update_all_notes(data)

    def load_notes(self):
        """Get data from Controller and populate UI"""
        data = self.controller.get_notes()
        for text in data:
            # --- FIX: Pass save=False to avoid triggering the save loop ---
            self.add_note(text, save=False)