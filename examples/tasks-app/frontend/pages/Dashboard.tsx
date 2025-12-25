import { Head } from "@inertiajs/react";
import MainLayout from "../layouts/MainLayout";
import type { User } from "../types";

interface DashboardProps {
  user: User | null;
  data: Record<string, unknown>;
}

export default function Dashboard({ user, data }: DashboardProps) {
  return (
    <MainLayout user={user}>
      <Head title="Dashboard" />
      <div className="p-8 font-sans">
        <h1 className="text-3xl font-bold mb-4">Welcome{user ? `, ${user.name}` : ""}!</h1>
        <p className="mb-4">This is a server-side rendered page using Bun + FastAPI + Inertia.</p>

        <div className="bg-gray-100 p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-2">Data from Python:</h2>
          <pre className="bg-white p-2 rounded border">{JSON.stringify(data, null, 2)}</pre>
        </div>
      </div>
    </MainLayout>
  );
}
