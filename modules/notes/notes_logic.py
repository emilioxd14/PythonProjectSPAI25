# modules/notes/notes_logic.py
from storage import TodoStorage


class NotesLogic:
    def __init__(self):
        # 1. Initialize Storage
        self.storage = TodoStorage(filename="sticky_notes.json")

        # 2. Load existing data immediately
        self.notes = self.storage.load_data()

    def get_notes(self):
        """Returns the list of note strings for the UI to display."""
        return self.notes

    def update_all_notes(self, new_note_list):
        """
        REQUIRED BY UI:
        The UI sends the full list of text strings here whenever
        a note is added, deleted, or typed in.
        """
        self.notes = new_note_list
        self.storage.save_data(self.notes)