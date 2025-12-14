import React, { useState } from 'react';
import { Head, Link, router } from '@inertiajs/react';
import MainLayout from '../../layouts/MainLayout';

export default function TicketsIndex({ user, tickets }) {
    const [isCreating, setIsCreating] = useState(false);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        router.post('/tickets', { title, description }, {
            onSuccess: () => {
                setTitle('');
                setDescription('');
                setIsCreating(false);
            }
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'open': return 'bg-blue-100 text-blue-800';
            case 'closed': return 'bg-gray-100 text-gray-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <MainLayout user={user}>
            <Head title="Tickets" />
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Tickets</h1>
                <button
                    onClick={() => setIsCreating(!isCreating)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    {isCreating ? 'Cancel' : '+ New Ticket'}
                </button>
            </div>

            {isCreating && (
                <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
                    <h2 className="text-xl font-semibold mb-4">Create New Ticket</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Title
                            </label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                required
                            />
                        </div>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Description
                            </label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows="4"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                        >
                            Create Ticket
                        </button>
                    </form>
                </div>
            )}

            <div className="bg-white rounded-lg shadow-sm border">
                {tickets.length === 0 ? (
                    <div className="p-8 text-center">
                        <div className="text-6xl mb-4">🎟️</div>
                        <h3 className="text-xl font-medium text-gray-900 mb-2">No Tickets Yet</h3>
                        <p className="text-gray-500">Create your first ticket to get started.</p>
                    </div>
                ) : (
                    <div className="divide-y">
                        {tickets.map((ticket) => (
                            <Link
                                key={ticket.id}
                                href={`/tickets/${ticket.id}`}
                                className="block p-4 hover:bg-gray-50 transition"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                                            {ticket.title}
                                        </h3>
                                        {ticket.description && (
                                            <p className="text-gray-600 text-sm line-clamp-2">
                                                {ticket.description}
                                            </p>
                                        )}
                                        <p className="text-gray-400 text-xs mt-2">
                                            {new Date(ticket.created_at).toLocaleString('en-US')}
                                        </p>
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                                        {ticket.status}
                                    </span>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}
