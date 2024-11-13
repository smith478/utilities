import React, { useState, useEffect } from 'react';
import { PlusCircle, Trash2, CheckCircle, Circle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const TodoApp = () => {
  const [tasks, setTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });
  const [error, setError] = useState('');

  // In a real app, these would be API calls
  const fetchTasks = () => {
    // Simulated API call
    const mockTasks = [
      {
        id: "20240312123456",
        title: "Sample Task",
        description: "This is a sample task",
        completed: false,
        created_at: "2024-03-12T12:34:56"
      }
    ];
    setTasks(mockTasks);
    updateStats(mockTasks);
  };

  const updateStats = (currentTasks) => {
    const completed = currentTasks.filter(t => t.completed).length;
    setStats({
      total: currentTasks.length,
      completed,
      pending: currentTasks.length - completed
    });
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleAddTask = () => {
    if (!newTaskTitle.trim()) {
      setError('Task title cannot be empty');
      return;
    }

    const newTask = {
      id: Date.now().toString(),
      title: newTaskTitle,
      description: newTaskDesc,
      completed: false,
      created_at: new Date().toISOString()
    };

    setTasks(prev => [...prev, newTask]);
    updateStats([...tasks, newTask]);
    setNewTaskTitle('');
    setNewTaskDesc('');
    setError('');
  };

  const toggleComplete = (taskId) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId 
        ? { ...task, completed: !task.completed }
        : task
    ));
  };

  const deleteTask = (taskId) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Todo List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-2 bg-gray-100 rounded">
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-sm text-gray-600">Total</div>
              </div>
              <div className="text-center p-2 bg-green-100 rounded">
                <div className="text-2xl font-bold">{stats.completed}</div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div className="text-center p-2 bg-yellow-100 rounded">
                <div className="text-2xl font-bold">{stats.pending}</div>
                <div className="text-sm text-gray-600">Pending</div>
              </div>
            </div>

            {/* Add Task Form */}
            <div className="space-y-2">
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                placeholder="Task title"
                className="w-full p-2 border rounded"
              />
              <textarea
                value={newTaskDesc}
                onChange={(e) => setNewTaskDesc(e.target.value)}
                placeholder="Description (optional)"
                className="w-full p-2 border rounded"
              />
              <button
                onClick={handleAddTask}
                className="w-full bg-blue-500 text-white p-2 rounded flex items-center justify-center gap-2"
              >
                <PlusCircle className="w-4 h-4" />
                Add Task
              </button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Task List */}
            <div className="space-y-2">
              {tasks.map(task => (
                <div
                  key={task.id}
                  className="flex items-center gap-2 p-2 border rounded hover:bg-gray-50"
                >
                  <button
                    onClick={() => toggleComplete(task.id)}
                    className="flex-shrink-0"
                  >
                    {task.completed ? (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    ) : (
                      <Circle className="w-6 h-6 text-gray-400" />
                    )}
                  </button>
                  <div className="flex-grow">
                    <div className={task.completed ? 'line-through text-gray-500' : ''}>
                      {task.title}
                    </div>
                    {task.description && (
                      <div className="text-sm text-gray-600">{task.description}</div>
                    )}
                  </div>
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="text-red-500"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TodoApp;