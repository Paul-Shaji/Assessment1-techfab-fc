import { iconFor } from "./icons";
import { TrendBadge } from "./TrendBadge";
import { formatNumber } from "../lib/format";
import type { StatCard as StatCardType } from "../types";

export function StatCard({
  card,
  onClick,
}: {
  card: StatCardType;
  onClick?: () => void;
}) {
  const Icon = iconFor(card.icon);
  return (
    <button
      type="button"
      onClick={onClick}
      className="group flex w-full flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 text-left shadow-card transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md"
    >
      <div className="flex items-center justify-between">
        <span className="rounded-lg bg-brand-50 p-2 text-brand-600 transition group-hover:bg-brand-100">
          <Icon size={20} />
        </span>
        {card.trend_label && (
          <TrendBadge trend={card.trend} label={card.trend_label} />
        )}
      </div>
      <div>
        <div className="text-3xl font-semibold tracking-tight text-slate-900">
          {formatNumber(card.value)}
        </div>
        <div className="mt-1 text-sm text-slate-500">{card.label}</div>
      </div>
    </button>
  );
}
