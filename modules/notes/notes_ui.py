# modules/notes/notes_ui.py

import customtkinter as ctk
from datetime import datetime


class StickyNote(ctk.CTkFrame):
    """Represents a single yellow square note."""

    def __init__(self, master, text_content="", is_favorite=False, created_at=None,
                 is_locked=False, pin=None, on_delete=None,
                 on_favorite_toggle=None, on_lock_toggle=None, on_text_change=None, **kwargs):
        super().__init__(master, **kwargs)

        # State storage
        self.is_favorite = is_favorite
        self.created_at = created_at
        self.is_locked = is_locked
        self.pin = pin

        # WICHTIG: Das ist unser "Single Source of Truth".
        # Der Text hier drin ist immer aktuell.
        self.real_text_content = text_content

        # Callbacks
        self.on_favorite_toggle = on_favorite_toggle
        self.on_lock_toggle = on_lock_toggle
        self.on_text_change = on_text_change  # Callback zum Speichern beim Tippen

        self.configure(fg_color="#F9F871", corner_radius=10, width=200, height=200)

        # --- LAYOUT ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Schloss-Button (Oben Links)
        self.lock_btn = ctk.CTkButton(
            self,
            text="🔒" if self.is_locked else "🔓",
            width=25, height=25,
            fg_color="transparent", text_color="black", hover_color="#E0E060",
            command=self._handle_lock_click
        )
        self.lock_btn.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # 2. Button Container (Oben Rechts)
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.grid(row=0, column=1, sticky="ne", padx=5, pady=5)

        self.fav_btn = ctk.CTkButton(
            btn_container,
            text="★" if self.is_favorite else "☆",
            width=25, height=25,
            fg_color="transparent", text_color="black", hover_color="#E0E060",
            command=self._handle_favorite_click
        )
        self.fav_btn.pack(side="left", padx=(0, 5))

        self.delete_btn = ctk.CTkButton(
            btn_container, text="✕", width=25, height=25,
            fg_color="transparent", text_color="black", hover_color="#E0E060",
            command=on_delete
        )
        self.delete_btn.pack(side="left")

        # 3. Text Area (Mitte)
        self.textbox = ctk.CTkTextbox(
            self, fg_color="transparent", text_color="black",
            font=("Comic Sans MS", 14), wrap="word"
        )
        self.textbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        # WICHTIG: Wir binden das Tippen an unsere interne Logik
        self.textbox.bind("<KeyRelease>", self._on_key_release)

        # Inhalt initial anzeigen
        self._update_text_display()

        # 4. Erstellungsdatum (Unten Links)
        display_date = self.created_at if self.created_at else "?"
        self.date_label = ctk.CTkLabel(
            self,
            text=f"📅 {display_date}",
            font=("Arial", 10), text_color="gray40"
        )
        self.date_label.grid(row=2, column=0, columnspan=2, sticky="sw", padx=10, pady=(0, 5))

    def _on_key_release(self, event):
        """Wird bei jedem Tastendruck aufgerufen."""
        if not self.is_locked:
            # 1. Text sofort intern sichern
            self.real_text_content = self.textbox.get("0.0", "end").strip()
            # 2. Controller benachrichtigen (Speichern)
            if self.on_text_change:
                self.on_text_change()

    def _update_text_display(self):
        """Zeigt entweder den Text oder eine Maske an, je nach Lock-Status."""
        # Zustand temporär auf normal setzen, um Text zu ändern
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")

        if self.is_locked:
            self.textbox.insert("0.0", "🔒 Content Locked\n(Click lock to open)")
            self.textbox.configure(state="disabled")  # Eingabe sperren
        else:
            self.textbox.insert("0.0", self.real_text_content)
            # Eingabe bleibt möglich

    def _handle_favorite_click(self):
        if self.on_favorite_toggle:
            self.on_favorite_toggle(self.get_text())

    def _handle_lock_click(self):
        """Verwaltet das Sperren und Entsperren mit PIN-Dialog."""

        if self.is_locked:
            # === ENTSPERREN ===
            dialog = ctk.CTkInputDialog(text="Enter PIN to unlock:", title="Unlock Note")
            input_pin = dialog.get_input()

            if input_pin == self.pin:
                self.is_locked = False
                self.lock_btn.configure(text="🔓")
                self._update_text_display()
                # Controller benachrichtigen
                if self.on_lock_toggle:
                    self.on_lock_toggle(self.real_text_content, False, None)
            elif input_pin is not None:
                print("Wrong PIN")

        else:
            # === SPERREN ===
            dialog = ctk.CTkInputDialog(text="Set 4-digit PIN:", title="Protect Note")
            new_pin = dialog.get_input()

            if new_pin and len(new_pin) > 0:
                self.is_locked = True
                self.pin = new_pin
                # Wir müssen hier kein get_text() machen, da real_text_content dank
                # _on_key_release immer aktuell ist.
                self.lock_btn.configure(text="🔒")
                self._update_text_display()
                # Controller benachrichtigen
                if self.on_lock_toggle:
                    self.on_lock_toggle(self.real_text_content, True, new_pin)

    def get_text(self):
        """Gibt immer den sicheren internen Text zurück."""
        return self.real_text_content

    def get_data(self):
        return {
            "text": self.get_text(),
            "is_favorite": self.is_favorite,
            "created_at": self.created_at,
            "is_locked": self.is_locked,
            "pin": self.pin
        }


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

    def _handle_favorite_toggle(self, note_text):
        new_sorted_data = self.controller.toggle_favorite(note_text)
        self.reload_ui_from_data(new_sorted_data)

    def _handle_lock_toggle(self, note_text, is_locked, pin):
        """Aktualisiert nur den Status, lädt aber NICHT neu, um Flackern zu vermeiden."""
        self.controller.set_lock_status(note_text, is_locked, pin)

    def reload_ui_from_data(self, data):
        for note in self.notes_list:
            note.destroy()
        self.notes_list = []

        for item in data:
            self._create_note_widget(
                text=item['text'],
                is_favorite=item.get('is_favorite', False),
                created_at=item.get('created_at'),
                is_locked=item.get('is_locked', False),
                pin=item.get('pin'),
                save=False
            )

        self.refresh_grid()

    def _create_note_widget(self, text="", is_favorite=False, created_at=None, is_locked=False, pin=None, save=True):

        if created_at is None:
            created_at = datetime.now().strftime("%d.%m.%Y")

        new_note = StickyNote(
            self.scroll_frame,
            text_content=text,
            is_favorite=is_favorite,
            created_at=created_at,
            is_locked=is_locked,
            pin=pin,
            on_delete=lambda: self.delete_note_from_ui(new_note),
            on_favorite_toggle=self._handle_favorite_toggle,
            on_lock_toggle=self._handle_lock_toggle,
            # WICHTIG: Hier übergeben wir den neuen Callback
            on_text_change=self.save_notes
        )

        self.notes_list.append(new_note)

        if save:
            self.save_notes()

        return new_note

    def add_note(self, text="", save=True):
        self._create_note_widget(text=text, save=save)
        self.refresh_grid()

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
        """Sammelt alle Daten und speichert sie."""
        data = [note.get_data() for note in self.notes_list]
        self.controller.update_all_notes(data)

    def load_notes(self):
        data = self.controller.get_notes()
        self.reload_ui_from_data(data)