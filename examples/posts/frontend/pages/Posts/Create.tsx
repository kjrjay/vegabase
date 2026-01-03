import { Link, useNavigate } from "@tanstack/react-router";
import { FormEvent, useState } from "react";

export default function PostsCreate() {
  const [data, setData] = useState({ title: "", body: "" });
  const [processing, setProcessing] = useState(false);
  const [errors, setErrors] = useState<{ title?: string; body?: string }>({});

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setProcessing(true);
    setErrors({});

    try {
      const response = await fetch("/posts/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (response.redirected) {
        window.location.href = response.url;
      } else if (!response.ok) {
        const errorData = await response.json();
        setErrors(errorData.detail || {});
      }
    } catch (error) {
      console.error("Submit failed:", error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Create Post</h1>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-8">
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">Title</label>
            <input
              type="text"
              name="title"
              value={data.title}
              onChange={(e) => setData({ ...data, title: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter post title..."
            />
            {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">Body</label>
            <textarea
              name="body"
              value={data.body}
              onChange={(e) => setData({ ...data, body: e.target.value })}
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Write your post content..."
            />
            {errors.body && <p className="text-red-500 text-sm mt-1">{errors.body}</p>}
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={processing}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {processing ? "Creating..." : "Create Post"}
            </button>
            <Link
              to="/posts"
              className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
