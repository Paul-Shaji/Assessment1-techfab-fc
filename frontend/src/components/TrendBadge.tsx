import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

export function TrendBadge({ trend, label }: { trend: number; label?: string }) {
  const up = trend > 0;
  const down = trend < 0;
  const cls = up
    ? "bg-emerald-50 text-emerald-700"
    : down
      ? "bg-rose-50 text-rose-700"
      : "bg-slate-100 text-slate-500";
  const Icon = up ? ArrowUpRight : down ? ArrowDownRight : Minus;
  return (
    <span
      className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}
    >
      <Icon size={12} />
      {up ? "+" : ""}
      {trend}%
      {label && <span className="ml-1 font-normal opacity-70">{label}</span>}
    </span>
  );
}
