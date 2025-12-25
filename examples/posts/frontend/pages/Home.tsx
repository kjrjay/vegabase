import { Link } from "@inertiajs/react";

interface HomeProps {
  message: string;
}

export default function Home({ message }: HomeProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 shadow-2xl text-center">
        <h1 className="text-5xl font-bold text-white mb-4">🚀 PyReact Start</h1>
        <p className="text-xl text-white/80 mb-8">{message}</p>
        <Link
          href="/posts"
          className="bg-white text-indigo-600 px-6 py-3 rounded-lg font-semibold hover:bg-white/90 transition"
        >
          View Posts →
        </Link>
      </div>
    </div>
  );
}
