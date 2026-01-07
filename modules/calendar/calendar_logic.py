import calendar
import datetime

class CalendarLogic:
    def __init__(self, todo_controller):
        """
        initializes the CalendarLogic with a reference to the TodoController.
        
        Args:
            todo_controller: The controller that manages tasks.
        """
        self.todo_controller = todo_controller

    def get_month_matrix(self, year, month):
        """
        Returns a matrix representing a month's calendar.
        Each row is a week; days outside the month are 0.
        """
        return calendar.monthcalendar(year, month)

    def get_week_dates(self, reference_date):
        """
        Returns a list of 7 datetime.date objects representing the week
        containing the reference_date (Monday to Sunday).
        """
        if isinstance(reference_date, datetime.datetime):
            reference_date = reference_date.date()
            
        start_of_week = reference_date - datetime.timedelta(days=reference_date.weekday())
        week_dates = [start_of_week + datetime.timedelta(days=i) for i in range(7)]
        return week_dates

    def get_events(self, start_date, end_date):
        """
        Legacy method: Returns a list of tasks for a range. 
        Useful for single-day queries.
        """
        return self._filter_tasks(start_date, end_date)

    def get_events_dict(self, start_date, end_date):
        """
        OPTIMIZED METHOD:
        Fetches all tasks ONCE and organizes them into a dictionary.
        
        Args:
            start_date (datetime.date): The start of the range (inclusive).
            end_date (datetime.date): The end of the range (inclusive).
            
        Returns:
            dict: { datetime.date: [task1, task2, ...] } keys are date objects.
        """
        # Ensure we are working with date objects
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()
            
        all_tasks = self.todo_controller.get_tasks()
        events_map = {}
        
        for task in all_tasks:
            due_date_str = task.get('due_date')
            if not due_date_str:
                continue
                
            try:
                # Robust parsing
                task_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                
                # Strict filtering (inclusive)
                if start_date <= task_date <= end_date:
                    if task_date not in events_map:
                        events_map[task_date] = []
                    events_map[task_date].append(task)
            except (ValueError, TypeError):
                # Handle invalid date formats gracefully
                continue
                
        # Sort tasks by time within each date
        for date_key in events_map:
            events_map[date_key].sort(key=lambda x: (x.get('due_time') or "00:00"))
            
        return events_map

    def _filter_tasks(self, start_date, end_date):
        """
        Internal helper to filter tasks within a date range.
        """
        all_tasks = self.todo_controller.get_tasks()
        events = []

        # Ensure we are comparing date objects
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()

        for task in all_tasks:
            due_date_str = task.get('due_date')
            
            if not due_date_str:
                continue

            try:
                # Parse the due_date string "YYYY-MM-DD"
                task_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                
                if start_date <= task_date <= end_date:
                    events.append(task)
            except ValueError:
                continue

        # Sort events by date and time
        events.sort(key=lambda x: (x.get('due_date'), x.get('due_time') or "00:00"))
        
        return events