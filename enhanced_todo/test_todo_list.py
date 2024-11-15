import unittest
import json
import os
from datetime import datetime
from unittest.mock import patch
from todo import TodoList

class TestTodoList(unittest.TestCase):
    def setUp(self):
        """Set up a new TodoList instance before each test."""
        self.test_file = "test_todo.json"
        self.todo_list = TodoList(self.test_file)
        
    def tearDown(self):
        """Clean up the test file after each test."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
    def test_init_creates_file(self):
        """Test that initialization creates the JSON file if it doesn't exist."""
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as file:
            self.assertEqual(json.load(file), [])
            
    @patch('datetime.datetime')
    def test_add_task(self, mock_datetime):
        """Test adding a new task."""
        # Mock the datetime
        mock_date = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_date
        
        task = self.todo_list.add_task(
            title="Test Task",
            description="Test Description",
            due_date="2024-12-31"
        )
        
        expected_task = {
            "id": "20240101120000",
            "title": "Test Task",
            "description": "Test Description",
            "due_date": "2024-12-31",
            "created_at": mock_date.isoformat(),
            "completed": False,
            "completed_at": None
        }
        
        self.assertEqual(task, expected_task)
        
        # Verify task was saved to file
        tasks = self.todo_list.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], expected_task)
        
    def test_add_task_empty_title(self):
        """Test that adding a task with empty title raises ValueError."""
        with self.assertRaises(ValueError):
            self.todo_list.add_task(title="")
            
    def test_get_task(self):
        """Test getting a specific task."""
        task = self.todo_list.add_task(title="Test Task")
        retrieved_task = self.todo_list.get_task(task["id"])
        self.assertEqual(task, retrieved_task)
        
        # Test getting non-existent task
        self.assertIsNone(self.todo_list.get_task("non-existent-id"))
        
    def test_update_task(self):
        """Test updating a task."""
        task = self.todo_list.add_task(title="Original Title")
        updated_task = self.todo_list.update_task(
            task["id"],
            {"title": "Updated Title", "description": "New Description"}
        )
        
        self.assertEqual(updated_task["title"], "Updated Title")
        self.assertEqual(updated_task["description"], "New Description")
        
        # Verify changes were saved
        saved_task = self.todo_list.get_task(task["id"])
        self.assertEqual(saved_task, updated_task)
        
    @patch('datetime.datetime')
    def test_toggle_complete(self, mock_datetime):
        """Test toggling task completion."""
        mock_date = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_date
        
        task = self.todo_list.add_task(title="Test Task")
        
        # Test completing task
        updated_task = self.todo_list.toggle_complete(task["id"])
        self.assertTrue(updated_task["completed"])
        self.assertEqual(updated_task["completed_at"], mock_date.isoformat())
        
        # Test uncompleting task
        updated_task = self.todo_list.toggle_complete(task["id"])
        self.assertFalse(updated_task["completed"])
        self.assertIsNone(updated_task["completed_at"])
        
    def test_delete_task(self):
        """Test deleting a task."""
        task = self.todo_list.add_task(title="Test Task")
        
        # Test successful deletion
        self.assertTrue(self.todo_list.delete_task(task["id"]))
        self.assertEqual(len(self.todo_list.get_all_tasks()), 0)
        
        # Test deleting non-existent task
        self.assertFalse(self.todo_list.delete_task("non-existent-id"))
        
    def test_get_stats(self):
        """Test getting task statistics."""
        # Add some tasks
        task1 = self.todo_list.add_task(title="Task 1")
        task2 = self.todo_list.add_task(title="Task 2")
        task3 = self.todo_list.add_task(title="Task 3")
        
        # Complete some tasks
        self.todo_list.toggle_complete(task1["id"])
        self.todo_list.toggle_complete(task2["id"])
        
        stats = self.todo_list.get_stats()
        expected_stats = {
            "total": 3,
            "completed": 2,
            "pending": 1
        }
        
        self.assertEqual(stats, expected_stats)
        
    def test_file_error_handling(self):
        """Test handling of file read/write errors."""
        # Test handling of corrupted JSON file
        with open(self.test_file, 'w') as file:
            file.write("corrupted json{")
            
        tasks = self.todo_list._read_tasks()
        self.assertEqual(tasks, [])

if __name__ == '__main__':
    # usage: python -m unittest test_todo_list.py
    unittest.main()