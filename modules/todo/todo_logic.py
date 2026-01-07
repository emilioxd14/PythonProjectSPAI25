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

    def add_task(self, text, due_date=None, due_time=None, priority="Medium"):
        """Adds a new task dictionary."""
        # Prevent duplicates based on text
        if not any(t['text'] == text for t in self.tasks):
            new_task = {
                "text": text,
                "completed": False,
                "due_date": due_date,
                "due_time": due_time,
                "priority": priority
            }
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

    def update_task(self, original_text, new_text, new_priority, new_date, new_time):
        """Actualiza texto, prioridad, fecha y hora de una tarea existente."""
        for task in self.tasks:
            # Buscamos la tarea por su nombre original
            if task['text'] == original_text:
                task['text'] = new_text
                task['priority'] = new_priority
                
                # Guardamos la fecha (o None si el usuario la borró)
                if new_date and new_date.strip():
                    task['due_date'] = new_date.strip()
                else:
                    task['due_date'] = None
                    
                # Guardamos la hora (o None)
                if new_time and new_time.strip():
                    task['due_time'] = new_time.strip()
                else:
                    task['due_time'] = None

                break
        self._save()

    def _save(self):
        self.storage.save_data(self.tasks)