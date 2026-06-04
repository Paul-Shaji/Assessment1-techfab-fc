import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";

export function PageHeader({
  title,
  subtitle,
  icon: Icon,
  actions,
}: {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-7 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3.5">
        {Icon && (
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-lg shadow-brand-500/20">
            <Icon size={22} />
          </span>
        )}
        <div>
          <h1 className="text-[1.7rem] font-bold leading-tight tracking-tight text-slate-900">
            {title}
          </h1>
          {subtitle && (
            <p className="mt-0.5 text-sm font-light tracking-wide text-slate-500">
              {subtitle}
            </p>
          )}
        </div>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Panel({
  title,
  children,
  actions,
}: {
  title?: string;
  children: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
      {(title || actions) && (
        <div className="mb-4 flex items-center justify-between gap-3">
          {title && (
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              {title}
            </h2>
          )}
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
