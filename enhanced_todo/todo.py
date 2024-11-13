import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class TodoList:
    def __init__(self, filename: str = 'todo.json'):
        self.filename = filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create the JSON file if it doesn't exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as file:
                json.dump([], file)

    def _read_tasks(self) -> List[Dict]:
        """Read tasks from the JSON file."""
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error reading file. Creating new task list.")
            return []

    def _write_tasks(self, tasks: List[Dict]) -> None:
        """Write tasks to the JSON file."""
        with open(self.filename, 'w') as file:
            json.dump(tasks, file, indent=2)

    def add_task(self, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict:
        """Add a new task to the list."""
        if not title:
            raise ValueError("Task title cannot be empty")

        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "title": title,
            "description": description,
            "due_date": due_date,
            "created_at": datetime.now().isoformat(),
            "completed": False,
            "completed_at": None
        }

        tasks = self._read_tasks()
        tasks.append(task)
        self._write_tasks(tasks)
        return task

    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks."""
        return self._read_tasks()

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID."""
        tasks = self._read_tasks()
        return next((task for task in tasks if task["id"] == task_id), None)

    def update_task(self, task_id: str, updates: Dict) -> Optional[Dict]:
        """Update a task's details."""
        tasks = self._read_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task.update(updates)
                self._write_tasks(tasks)
                return task
        return None

    def toggle_complete(self, task_id: str) -> Optional[Dict]:
        """Toggle the completion status of a task."""
        tasks = self._read_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                task["completed_at"] = datetime.now().isoformat() if task["completed"] else None
                self._write_tasks(tasks)
                return task
        return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        tasks = self._read_tasks()
        initial_length = len(tasks)
        tasks = [task for task in tasks if task["id"] != task_id]
        if len(tasks) != initial_length:
            self._write_tasks(tasks)
            return True
        return False

    def get_stats(self) -> Dict:
        """Get statistics about tasks."""
        tasks = self._read_tasks()
        completed = sum(1 for task in tasks if task["completed"])
        return {
            "total": len(tasks),
            "completed": completed,
            "pending": len(tasks) - completed
        }