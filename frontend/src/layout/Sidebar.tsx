import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Factory,
  Wrench,
  Users,
  ChevronLeft,
  X,
  type LucideIcon,
} from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import type { ModuleKey } from "../types";

const MODULE_NAV: Record<ModuleKey, { label: string; to: string; icon: LucideIcon }> = {
  sales: { label: "Sales", to: "/sales", icon: ShoppingCart },
  purchase: { label: "Purchase", to: "/purchase", icon: Package },
  manufacturing: { label: "Manufacturing", to: "/manufacturing", icon: Factory },
  assets: { label: "Assets & Service", to: "/assets", icon: Wrench },
  hr: { label: "HR & Payroll", to: "/hr", icon: Users },
};

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export function Sidebar({
  collapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
}: SidebarProps) {
  const { user } = useAuth();
  const modules = user?.modules ?? [];

  const navItems = [
    { label: "Overview", to: "/dashboard", icon: LayoutDashboard },
    ...modules.map((m) => MODULE_NAV[m]),
  ];

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
      isActive
        ? "bg-white/15 text-white shadow-lg shadow-black/10 backdrop-blur-sm border border-white/10"
        : "text-white/60 hover:bg-white/[0.07] hover:text-white/90"
    }`;

  const renderContent = (isCollapsed: boolean) => (
    <div className="flex h-full flex-col bg-slate-900/80 backdrop-blur-xl border-r border-white/[0.08] text-white">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-white/[0.06]">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-600 shadow-lg shadow-brand-500/20 font-bold text-sm">
          TF
        </div>
        {!isCollapsed && (
          <div className="leading-tight">
            <div className="font-semibold tracking-wide">TechFab</div>
            <div className="text-xs text-white/40 font-light tracking-wider">Industries</div>
          </div>
        )}
        <button
          onClick={onCloseMobile}
          className="ml-auto rounded-lg p-1.5 hover:bg-white/10 transition-colors lg:hidden"
          aria-label="Close menu"
        >
          <X size={18} className="text-white/60" />
        </button>
      </div>

      <nav className="flex-1 space-y-1.5 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={linkClass}
            onClick={onCloseMobile}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon size={18} className="shrink-0" />
            {!isCollapsed && <span className="tracking-wide">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <button
        onClick={onToggleCollapse}
        className="hidden items-center gap-2 border-t border-white/[0.06] px-5 py-4 text-sm text-white/40 hover:text-white/70 transition-colors lg:flex"
      >
        <ChevronLeft size={18} className={`transition-transform duration-300 ${isCollapsed ? "rotate-180" : ""}`} />
        {!isCollapsed && <span className="tracking-wide">Collapse</span>}
      </button>
    </div>
  );

  return (
    <>
      <aside
        className={`hidden shrink-0 transition-all duration-300 lg:block ${collapsed ? "w-16" : "w-64"}`}
      >
        {renderContent(collapsed)}
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onCloseMobile} />
          <div className="absolute left-0 top-0 h-full w-64 animate-in slide-in-from-left">
            {renderContent(false)}
          </div>
        </div>
      )}
    </>
  );
}