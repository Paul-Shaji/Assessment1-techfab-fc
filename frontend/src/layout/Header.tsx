import { useEffect, useRef, useState } from "react";
import { Menu, Bell, LogOut, ChevronDown, Wrench } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { getNotifications } from "../api/dashboard";
import type { NotificationItem } from "../types";

function initials(name: string): string {
  const parts = name.split(/\s+/).filter(Boolean).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase()).join("") || "U";
}

export function Header({ onOpenMobile }: { onOpenMobile: () => void }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [menu, setMenu] = useState<"none" | "notif" | "user">("none");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getNotifications()
      .then((r) => setItems(r.items))
      .catch(() => setItems([]));
  }, []);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setMenu("none");
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const handleLogout = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-slate-200 bg-white px-4 lg:px-6">
      <button
        onClick={onOpenMobile}
        className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>
      <div className="font-semibold text-slate-800 lg:hidden">TechFab</div>

      <div className="ml-auto flex items-center gap-2" ref={ref}>
        <div className="relative">
          <button
            onClick={() => setMenu(menu === "notif" ? "none" : "notif")}
            className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100"
            aria-label="Notifications"
          >
            <Bell size={20} />
            {items.length > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-semibold text-white">
                {items.length}
              </span>
            )}
          </button>
          {menu === "notif" && (
            <div className="absolute right-0 mt-2 w-80 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg">
              <div className="border-b border-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                Maintenance alerts
              </div>
              <div className="max-h-80 overflow-y-auto">
                {items.length === 0 ? (
                  <p className="px-4 py-6 text-center text-sm text-slate-400">
                    No upcoming maintenance.
                  </p>
                ) : (
                  items.map((n, i) => (
                    <div
                      key={`${n.asset_name}-${i}`}
                      className="flex items-start gap-3 border-b border-slate-50 px-4 py-3 last:border-0"
                    >
                      <Wrench size={16} className="mt-0.5 shrink-0 text-amber-500" />
                      <div className="text-sm">
                        <div className="font-medium text-slate-700">{n.asset_name}</div>
                        <div className="text-slate-500">
                          {n.maintenance_task} · due in {n.days_to_due}d
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setMenu(menu === "user" ? "none" : "user")}
            className="flex items-center gap-2 rounded-lg p-1.5 pr-2 hover:bg-slate-100"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-sm font-semibold text-white">
              {initials(user?.full_name ?? "U")}
            </span>
            <span className="hidden text-sm font-medium text-slate-700 sm:block">
              {user?.full_name}
            </span>
            <ChevronDown size={16} className="text-slate-400" />
          </button>
          {menu === "user" && (
            <div className="absolute right-0 mt-2 w-56 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg">
              <div className="border-b border-slate-100 px-4 py-3">
                <div className="text-sm font-medium text-slate-700">{user?.full_name}</div>
                <div className="truncate text-xs text-slate-400">{user?.email}</div>
              </div>
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm text-rose-600 hover:bg-rose-50"
              >
                <LogOut size={16} /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
