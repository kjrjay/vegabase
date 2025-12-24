import { Link, router } from '@inertiajs/react';

export default function PostsIndex({ posts, flash }) {
    const handleDelete = (postId) => {
        if (confirm('Are you sure?')) {
            router.post(`/posts/${postId}/delete`);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="max-w-3xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Posts</h1>
                    <Link
                        href="/posts/create"
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
                    >
                        + New Post
                    </Link>
                </div>

                {flash?.success && (
                    <div className="bg-green-100 text-green-800 px-4 py-3 rounded-lg mb-6">
                        {flash.success}
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
                                        <h2 className="text-xl font-semibold text-gray-900">
                                            {post.title}
                                        </h2>
                                        <p className="text-gray-600 mt-2">{post.body}</p>
                                    </div>
                                    <button
                                        onClick={() => handleDelete(post.id)}
                                        className="text-red-500 hover:text-red-700 text-sm"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                <div className="mt-8">
                    <Link href="/" className="text-indigo-600 hover:text-indigo-800">
                        ← Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
}
