import { useState, useRef, useEffect } from "react";
import { router } from "@inertiajs/react";
import type { User } from "../types";

interface AvatarProps {
  user: User;
}

export default function Avatar({ user }: AvatarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((word) => word[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = () => {
    router.post("/logout");
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="flex items-center gap-3">
      <div className="relative" ref={dropdownRef}>
        <button onClick={() => setIsOpen(!isOpen)} className="focus:outline-none">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name}
              className="w-10 h-10 rounded-full border-2 border-gray-200 hover:border-blue-400 transition"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold text-sm hover:bg-blue-700 transition cursor-pointer">
              {getInitials(user.name)}
            </div>
          )}
        </button>

        {/* Dropdown menu */}
        {isOpen && (
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-10">
            <div className="p-3 border-b">
              <p className="font-semibold text-gray-900">{user.name}</p>
              <p className="text-sm text-gray-500">@{user.username}</p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 text-red-600 text-sm rounded-b-lg"
            >
              Logout
            </button>
          </div>
        )}
      </div>
      <span className="text-sm font-medium text-gray-700 hidden sm:inline">{user.name}</span>
    </div>
  );
}
