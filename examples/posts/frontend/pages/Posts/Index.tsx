import { Link } from "@tanstack/react-router";
import { useState } from "react";

interface Post {
  id: number;
  title: string;
  body: string;
}

interface Flash {
  type: "success" | "error" | "warning" | "info";
  message: string;
}

interface PostsIndexProps {
  posts: Post[];
  flash?: Flash;
}

export default function PostsIndex({ posts, flash }: PostsIndexProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (postId: number) => {
    if (confirm("Are you sure?")) {
      setDeletingId(postId);
      try {
        await fetch(`/posts/${postId}/delete`, { method: "POST" });
        window.location.reload();
      } catch (error) {
        console.error("Delete failed:", error);
        setDeletingId(null);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Posts</h1>
          <Link
            to="/posts/create"
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            + New Post
          </Link>
        </div>

        {flash && (
          <div
            className={`px-4 py-3 rounded-lg mb-6 ${
              flash.type === "success"
                ? "bg-green-100 text-green-800"
                : flash.type === "error"
                  ? "bg-red-100 text-red-800"
                  : flash.type === "warning"
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-blue-100 text-blue-800"
            }`}
          >
            {flash.message}
          </div>
        )}

        {posts.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-8 text-center text-gray-500">
            No posts yet. Create your first post!
          </div>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <div key={post.id} className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{post.title}</h2>
                    <p className="text-gray-600 mt-2">{post.body}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(post.id)}
                    disabled={deletingId === post.id}
                    className="text-red-500 hover:text-red-700 text-sm disabled:opacity-50"
                  >
                    {deletingId === post.id ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8">
          <Link to="/" className="text-indigo-600 hover:text-indigo-800">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
