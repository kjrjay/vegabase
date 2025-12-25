import { type FormEvent } from "react";
import { Head, useForm, router } from "@inertiajs/react";
import MainLayout from "../../layouts/MainLayout";
import type { User, Task } from "../../types";

interface TasksIndexProps {
  user: User | null;
  tasks: Task[];
}

interface TaskForm {
  title: string;
}

export default function TasksIndex({ user, tasks }: TasksIndexProps) {
  const { data, setData, post, processing, reset } = useForm<TaskForm>({
    title: "",
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    post("/tasks", {
      onSuccess: () => reset(),
    });
  };

  return (
    <MainLayout user={user}>
      <Head title="Tasks" />

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
              value={data.title}
              onChange={(e) => setData({ title: e.target.value })}
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
  const toggle = () => {
    router.put(
      `/tasks/${task.id}`,
      {
        completed: !task.completed,
      },
      {
        preserveScroll: true,
      },
    );
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
        onClick={() => router.delete(`/tasks/${task.id}`)}
        className="text-red-400 opacity-0 group-hover:opacity-100 hover:text-red-600 transition-all"
      >
        Delete
      </button>
    </li>
  );
}
