"use client";

import { useEffect, useState } from "react";
import { WebSocketClient } from "@/lib/websocket";
import { Bell } from "lucide-react";

export function NotificationFeed() {
  const [notifications, setNotifications] = useState<{id: string, message: string, read: boolean}[]>([]);

  useEffect(() => {
    const ws = new WebSocketClient("/operators/live");
    const unsubscribe = ws.subscribe((data) => {
      setNotifications(prev => [
        { id: Date.now().toString(), message: `Event: ${data.type}`, read: false },
        ...prev
      ].slice(0, 20));
    });
    ws.connect();

    return () => {
      unsubscribe();
      ws.disconnect();
    };
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="relative">
      <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors">
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-[10px] font-bold flex items-center justify-center rounded-full">
            {unreadCount}
          </span>
        )}
      </button>
    </div>
  );
}
