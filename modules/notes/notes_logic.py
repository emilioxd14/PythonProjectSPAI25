# modules/notes/notes_logic.py
from storage import TodoStorage


class NotesLogic:
    def __init__(self):
        # 1. Initialize Storage
        self.storage = TodoStorage(filename="sticky_notes.json")

        # 2. Load existing data immediately
        self.notes = self.storage.load_data()

    def get_notes(self):
        """
        Returns the list of note dictionaries.
        Handles legacy data by converting strings to dictionaries on the fly.
        """
        legacy_handled_notes = []
        for item in self.notes:
            if isinstance(item, str):
                # Convert legacy string to dictionary
                legacy_handled_notes.append({"text": item, "color": "#F9F871"})
            else:
                legacy_handled_notes.append(item)
        
        # Update self.notes with cleaned data
        self.notes = legacy_handled_notes
        return self.notes

    def update_all_notes(self, new_note_list):
        """
        REQUIRED BY UI:
        The UI sends the full list of note dictionaries here whenever
        a note is added, deleted, or typed in.
        """
        self.notes = new_note_list
        self.storage.save_data(self.notes)