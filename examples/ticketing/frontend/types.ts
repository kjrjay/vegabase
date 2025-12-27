/**
 * Shared types for the tasks-app example.
 */

export interface User {
  id: number;
  username: string;
  name: string;
  avatar_url?: string;
}

export interface Task {
  id: number;
  title: string;
  completed: boolean;
}

export interface Ticket {
  id: number;
  title: string;
  description?: string;
  status: "open" | "closed";
  created_at: string;
}

export interface TicketWithAuthor {
  id: number;
  title: string;
  description?: string;
  status: "open" | "closed";
  created_at: string;
  author_name: string;
}
