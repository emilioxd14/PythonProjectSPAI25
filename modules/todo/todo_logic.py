from storage import TodoStorage

class TodoLogic:
    def __init__(self):
        self.storage = TodoStorage(filename="todo_list.json")
        self.tasks = self.storage.load_data()
        # Ensure data is in list format, if file was empty
        if not isinstance(self.tasks, list):
            self.tasks = []

    def get_tasks(self):
        return self.tasks

    def add_task(self, text):
        """Adds a new task dictionary."""
        # Prevent duplicates based on text
        if not any(t['text'] == text for t in self.tasks):
            new_task = {"text": text, "completed": False}
            self.tasks.append(new_task)
            self._save()

    def toggle_task_status(self, text):
        """Finds the task by text and flips its boolean status."""
        for task in self.tasks:
            if task['text'] == text:
                task['completed'] = not task['completed']
                break
        self._save()

    def clear_completed_tasks(self):
        """Keeps only tasks that are NOT completed."""
        self.tasks = [t for t in self.tasks if not t['completed']]
        self._save()

    def _save(self):
        self.storage.save_data(self.tasks)