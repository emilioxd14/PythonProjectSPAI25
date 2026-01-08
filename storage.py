# storage.py

import json
import os


class TodoStorage:
    # NOTE: Adjusted the path in __init__ to correctly access data_dir
    # from nested modules like modules/notes/notes_logic.py
    def __init__(self, filename="data.json", data_dir="app_data"):
        # Determine the root directory relative to where the script is executed
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.root_dir, data_dir)
        self.filepath = os.path.join(self.data_dir, filename)

        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def load_data(self):
        """Loads data from the JSON file or returns an empty list if not found."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Return empty list on corrupted or empty file
            return []

    def save_data(self, data):
        """Saves the data list to the JSON file."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            # Handle saving errors (e.g., file permissions)
            print(f"Error saving data to {self.filepath}: {e}")