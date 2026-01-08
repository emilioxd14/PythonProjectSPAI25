from datetime import datetime
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

    def add_task(self, text, due_date=None, due_time=None, reminder=False):
        """Adds a new task dictionary."""
        # Prevent duplicates based on text
        if not any(t['text'] == text for t in self.tasks):
            new_task = {
                "text": text, 
                "completed": False,
                "due_date": due_date,   # Expecting "YYYY-MM-DD"
                "due_time": due_time,   # Expecting "HH:MM"
                "reminder": reminder    # bool
            }
            self.tasks.append(new_task)
            self._save()

    def check_due_tasks(self):
        """Returns a list of tasks that are currently overdue and have reminders enabled."""
        overdue_tasks = []
        now = datetime.now()
        
        for task in self.tasks:
            # Skip completed tasks or tasks without reminders
            if task.get('completed') or not task.get('reminder'):
                continue
                
            due_date_str = task.get('due_date')
            due_time_str = task.get('due_time')
            
            if due_date_str:
                try:
                    # Construct datetime check
                    if due_time_str:
                        due_dt_str = f"{due_date_str} {due_time_str}"
                        due_dt = datetime.strptime(due_dt_str, "%d.%m.%Y %H:%M")
                    else:
                        # If no time specified, maybe warn at end of day? 
                        # Or just ignore 'time' and check if date is past. 
                        # Let's assume end of day logic or just simple date comparison.
                        # For simple reminder logic, let's treat "no time" as "start of day" or ignore.
                        # User request implies specific deadlines. 
                        # Let's default to 23:59 if no time, or just compare dates.
                        due_dt = datetime.strptime(due_date_str, "%d.%m.%Y")

                    if due_dt < now:
                        overdue_tasks.append(task)
                except ValueError:
                    continue # Handle data errors gracefully

        return overdue_tasks

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