import { type FormEvent, useState } from "react";
import { useNavigate, useRouter } from "@tanstack/react-router";
import MainLayout from "../../layouts/MainLayout";
import type { User, Task } from "../../types";

interface TasksIndexProps {
  user: User | null;
  tasks: Task[];
}

export default function TasksIndex({ user, tasks = [] }: TasksIndexProps) {
  const [title, setTitle] = useState("");
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setProcessing(true);
    try {
      await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ title }),
      });
      setTitle("");
      // Invalidate cache and refresh
      await router.invalidate();
      navigate({ to: "/tasks" });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <MainLayout user={user}>
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
            {tasks.length} Total
          </span>
        </div>

        {/* Create Task Form */}
        <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
          <form onSubmit={handleSubmit} className="flex gap-4">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What needs to be done?"
              className="flex-1 px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
              disabled={processing}
            />
            <button
              type="submit"
              disabled={processing}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              Add Task
            </button>
          </form>
        </div>

        {/* Task List */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {tasks.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No tasks yet. Add one above!</div>
          ) : (
            <ul className="divide-y divide-gray-100">
              {tasks.map((task) => (
                <TaskItem key={task.id} task={task} />
              ))}
            </ul>
          )}
        </div>
      </div>
    </MainLayout>
  );
}

interface TaskItemProps {
  task: Task;
}

function TaskItem({ task }: TaskItemProps) {
  const router = useRouter();

  const toggle = async () => {
    await fetch(`/tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ completed: !task.completed }),
    });
    await router.invalidate();
  };

  const deleteTask = async () => {
    await fetch(`/tasks/${task.id}`, {
      method: "DELETE",
      credentials: "include",
    });
    await router.invalidate();
  };

  return (
    <li className="p-4 hover:bg-gray-50 transition-colors flex items-center gap-4 group">
      <button
        onClick={toggle}
        className={`w-6 h-6 rounded border flex items-center justify-center transition-colors ${
          task.completed
            ? "bg-green-500 border-green-500 text-white"
            : "border-gray-300 hover:border-blue-500"
        }`}
      >
        {!!task.completed && (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>

      <span
        className={`flex-1 text-lg ${task.completed ? "text-gray-400 line-through" : "text-gray-800"}`}
      >
        {task.title}
      </span>

      <button
        onClick={deleteTask}
        className="text-red-400 opacity-0 group-hover:opacity-100 hover:text-red-600 transition-all"
      >
        Delete
      </button>
    </li>
  );
}
