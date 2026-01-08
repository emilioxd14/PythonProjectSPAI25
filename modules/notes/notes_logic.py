# modules/notes/notes_logic.py

from storage import TodoStorage
import copy


class NotesLogic:
    def __init__(self):
        # 1. Storage initialisieren
        self.storage = TodoStorage(filename="sticky_notes.json")

        # 2. Daten laden
        # Neue Struktur: {'text': '...', 'is_favorite': bool, 'created_at': '...', 'is_locked': bool, 'pin': '...'}
        self.notes = self.storage.load_data()

        # Sicherstellen, dass alle Felder existieren (für alte Dateien)
        for note in self.notes:
            if 'is_favorite' not in note: note['is_favorite'] = False
            if 'created_at' not in note: note['created_at'] = "?"
            if 'is_locked' not in note: note['is_locked'] = False
            if 'pin' not in note: note['pin'] = None

    def get_notes(self):
        """Gibt die Liste sortiert zurück (Favoriten zuerst)."""
        sorted_notes = sorted(self.notes, key=lambda note: note.get('is_favorite', False), reverse=True)
        return copy.deepcopy(sorted_notes)

    def update_all_notes(self, new_note_list):
        """Speichert die gesamte Liste, die von der UI kommt."""
        self.notes = new_note_list
        self.storage.save_data(self.notes)

    def toggle_favorite(self, note_text):
        """Schaltet den Favoritenstatus um."""
        found = False
        for note in self.notes:
            if note['text'] == note_text:
                note['is_favorite'] = not note.get('is_favorite', False)
                found = True
                break

        if found:
            self.storage.save_data(self.notes)

        return self.get_notes()

    def set_lock_status(self, note_text, is_locked, pin=None):
        """Aktualisiert den Sperrstatus und die PIN einer Notiz."""
        found = False
        for note in self.notes:
            if note['text'] == note_text:
                note['is_locked'] = is_locked
                note['pin'] = pin
                found = True
                break

        if found:
            self.storage.save_data(self.notes)

        return self.get_notes()