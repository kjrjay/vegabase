// Title management would use document.title or react-helmet-async
import MainLayout from "../layouts/MainLayout";

export default function About() {
  return (
    <MainLayout user={null}>
      <div className="p-8 font-sans max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">About Vegabase</h1>

        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-3">What is Vegabase?</h2>
          <p className="text-gray-700 leading-relaxed">
            Vegabase is a Python web framework that brings the power of server-side rendering to
            your React applications. Built on FastAPI and Inertia.js, it provides a seamless
            full-stack development experience.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-3">Render Modes</h2>
          <p className="text-gray-700 mb-4">
            This demo showcases all four render modes available in Vegabase:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>
              <strong>SSR</strong> - Server-side rendered with React hydration (Tasks page)
            </li>
            <li>
              <strong>Client</strong> - Client-side only rendering, no SSR call (Dashboard)
            </li>
            <li>
              <strong>Cached</strong> - ISR with CDN caching, revalidates periodically (Tickets)
            </li>
            <li>
              <strong>Static</strong> - Pure HTML, no JavaScript hydration (this page!)
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-3">Features</h2>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>Type-safe Python backend with FastAPI</li>
            <li>React frontend with TypeScript</li>
            <li>Flash messages and session management</li>
            <li>Flexible rendering modes for optimal performance</li>
          </ul>
        </section>

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-yellow-800 text-sm">
            <strong>Note:</strong> This page is rendered with{" "}
            <code className="bg-yellow-100 px-1 rounded">mode="static"</code> — no JavaScript is
            loaded, making it lighter and more cacheable.
          </p>
        </div>
      </div>
    </MainLayout>
  );
}
