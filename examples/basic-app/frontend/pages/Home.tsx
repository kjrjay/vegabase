export default function Home({ message }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 shadow-2xl text-center">
                <h1 className="text-5xl font-bold text-white mb-4">
                    🚀 PyReact Start
                </h1>
                <p className="text-xl text-white/80">
                    {message}
                </p>
            </div>
        </div>
    );
}
