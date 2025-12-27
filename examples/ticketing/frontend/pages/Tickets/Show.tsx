import { Head, Link, router } from "@inertiajs/react";
import MainLayout from "../../layouts/MainLayout";
import type { User, Ticket } from "../../types";

interface TicketsShowProps {
  user: User | null;
  ticket: Ticket;
}

export default function TicketsShow({ user, ticket }: TicketsShowProps) {
  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this ticket?")) {
      router.delete(`/tickets/${ticket.id}`);
    }
  };

  const handleStatusChange = (newStatus: Ticket["status"]) => {
    router.put(`/tickets/${ticket.id}`, { status: newStatus });
  };

  const getStatusColor = (status: Ticket["status"]) => {
    switch (status) {
      case "open":
        return "bg-blue-100 text-blue-800";
      case "closed":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <MainLayout user={user}>
      <Head title={`Ticket #${ticket.id} - ${ticket.title}`} />

      <div className="mb-6">
        <Link href="/tickets" className="text-blue-600 hover:text-blue-700">
          ← Back to Tickets
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{ticket.title}</h1>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}
                >
                  {ticket.status}
                </span>
              </div>
              <p className="text-gray-500 text-sm">
                Ticket #{ticket.id} • Created {new Date(ticket.created_at).toLocaleString("en-US")}
              </p>
            </div>
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Delete
            </button>
          </div>
        </div>

        <div className="p-6">
          <h2 className="text-lg font-semibold mb-3">Description</h2>
          {ticket.description ? (
            <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
          ) : (
            <p className="text-gray-400 italic">No description provided</p>
          )}
        </div>

        <div className="p-6 border-t bg-gray-50">
          <h2 className="text-lg font-semibold mb-3">Actions</h2>
          <div className="flex gap-2">
            {ticket.status !== "open" && (
              <button
                onClick={() => handleStatusChange("open")}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Reopen
              </button>
            )}
            {ticket.status !== "closed" && (
              <button
                onClick={() => handleStatusChange("closed")}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
              >
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
