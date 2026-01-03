import { type ReactNode } from "react";
import { Link, useLocation } from "@tanstack/react-router";
import Avatar from "../components/Avatar";
import type { User } from "../types";

interface MainLayoutProps {
  children: ReactNode;
  user: User | null;
}

interface NavLinkProps {
  to: string;
  children: ReactNode;
  active: boolean;
}

export default function MainLayout({ children, user }: MainLayoutProps) {
  const location = useLocation();
  const url = location.pathname;

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-2xl font-bold text-blue-400">Ticketing</h1>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <NavLink to="/" active={url === "/"}>
            Dashboard
          </NavLink>
          <NavLink to="/tasks" active={url.startsWith("/tasks")}>
            Tasks
          </NavLink>
          <NavLink to="/tickets" active={url.startsWith("/tickets")}>
            Tickets
          </NavLink>
          <NavLink to="/about" active={url === "/about"}>
            About
          </NavLink>
        </nav>

        <div className="p-4 border-t border-gray-800">
          {user ? (
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-lg font-bold">
                {user.name?.[0] || "U"}
              </div>
              <div>
                <div className="font-medium">{user.name}</div>
                <div className="text-xs text-gray-400">@{user.username}</div>
              </div>
            </div>
          ) : (
            <Link
              to="/login"
              className="block text-center px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 text-sm"
            >
              Login
            </Link>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm h-16 flex items-center px-8 justify-between">
          <h2 className="text-xl font-semibold text-gray-800">Application</h2>
          {user && <Avatar user={user} />}
        </header>

        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}

function NavLink({ to, children, active }: NavLinkProps) {
  return (
    <Link
      to={to}
      className={`block px-4 py-3 rounded transition-colors ${
        active ? "bg-blue-600 text-white" : "text-gray-400 hover:bg-gray-800 hover:text-white"
      }`}
    >
      {children}
    </Link>
  );
}
