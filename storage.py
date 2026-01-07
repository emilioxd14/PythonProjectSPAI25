import json
import os
import shutil


class TodoStorage:
    def __init__(self, filename="todo_list_data.json"):
        """
        Handles saving and loading data to the user's AppData folder.
        Args:
            filename (str): The name of the file (defaults to tasks).
        """
        # 1. Get the path to the system's safe storage (AppData/Local)
        # On Windows: C:\Users\Name\AppData\Local
        # On Mac: /Users/Name/Library/Application Support (conceptually similar)
        base_path = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')

        # 2. Create a specific folder for your project
        # Feel free to change "MyIntegratedApp" to your project name
        self.app_folder = os.path.join(base_path, "MyIntegratedApp")

        # 3. Create the folder if it doesn't exist
        if not os.path.exists(self.app_folder):
            try:
                os.makedirs(self.app_folder)
            except OSError as e:
                print(f"Error creating folder: {e}")

        # 4. Set the full path to the file
        self.filepath = os.path.join(self.app_folder, filename)

    def save_data(self, data):
        """Writes the list of data to the JSON file."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """Reads the JSON file and returns the list."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            print(f"Corrupt JSON file detected: {e}")
            try:
                backup_path = self.filepath + ".bak"
                shutil.move(self.filepath, backup_path)
                print(f"Backed up corrupt file to: {backup_path}")
            except Exception as move_error:
                print(f"Failed to backup corrupt file: {move_error}")
            return []
        except Exception as e:
            print(f"Error loading data: {e}")
            return []


# Testing block: Runs only if you run 'storage.py' directly
if __name__ == "__main__":
    storage = TodoStorage()
    print(f"Storage is ready! Saving files to:\n{storage.filepath}")