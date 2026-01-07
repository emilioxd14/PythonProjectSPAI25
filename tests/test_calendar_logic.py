
import unittest
from datetime import date, datetime
import sys
import os

# Add modules path to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calendar.calendar_logic import CalendarLogic

class MockTodoController:
    def __init__(self, tasks):
        self.tasks = tasks

    def get_tasks(self):
        return self.tasks

class TestCalendarLogic(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            {'title': 'Task 1', 'due_date': '2023-10-01', 'due_time': '10:00'},
            {'title': 'Task 2', 'due_date': '2023-10-05', 'due_time': '12:00'},
            {'title': 'Task 3', 'due_date': '2023-10-10', 'due_time': '09:00'},
            {'title': 'Task 4', 'due_date': '2023-10-05', 'due_time': '08:00'}, # Same day as Task 2, earlier
            {'title': 'Task Invalid', 'due_date': 'invalid-date'},
            {'title': 'Task No Date', 'due_date': ''},
            {'title': 'Task Out of Range', 'due_date': '2023-11-01'},
        ]
        self.controller = MockTodoController(self.tasks)
        self.logic = CalendarLogic(self.controller)

    def test_get_events_dict(self):
        start_date = date(2023, 10, 1)
        end_date = date(2023, 10, 5)
        
        events = self.logic.get_events_dict(start_date, end_date)
        
        # Check keys are date objects
        for k in events.keys():
            self.assertIsInstance(k, date)
            
        # Check Task 1 is present (start boundary)
        self.assertIn(date(2023, 10, 1), events)
        self.assertEqual(len(events[date(2023, 10, 1)]), 1)
        
        # Check Task 2 and 4 are present (end boundary)
        self.assertIn(date(2023, 10, 5), events)
        self.assertEqual(len(events[date(2023, 10, 5)]), 2)
        
        # Check sorting: Task 4 (08:00) should be before Task 2 (12:00)
        day_5_tasks = events[date(2023, 10, 5)]
        self.assertEqual(day_5_tasks[0]['title'], 'Task 4')
        self.assertEqual(day_5_tasks[1]['title'], 'Task 2')
        
        # Check Task 3 (out of range) is NOT present
        self.assertNotIn(date(2023, 10, 10), events)
        
        # Check invalid/no date tasks are ignored
        # Converting all task titles in result to a flat list
        all_titles = []
        for d in events:
            for t in events[d]:
                all_titles.append(t['title'])
                
        self.assertNotIn('Task Invalid', all_titles)
        self.assertNotIn('Task No Date', all_titles)
        self.assertNotIn('Task Out of Range', all_titles)

if __name__ == '__main__':
    unittest.main()
