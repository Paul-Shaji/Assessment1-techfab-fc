import { formatNumber } from "../lib/format";

export interface Segment {
  label: string;
  value: number;
  /** Tailwind background class, e.g. "bg-emerald-500" */
  color: string;
}

export function SegmentedBar({ segments }: { segments: Segment[] }) {
  const total = segments.reduce((s, x) => s + Math.max(x.value, 0), 0) || 1;
  return (
    <div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-100">
        {segments.map((s) => (
          <div
            key={s.label}
            className={s.color}
            style={{ width: `${(Math.max(s.value, 0) / total) * 100}%` }}
            title={`${s.label}: ${formatNumber(s.value)}`}
          />
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
        {segments.map((s) => (
          <span key={s.label} className="inline-flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${s.color}`} />
            {s.label}:
            <b className="text-slate-700">{formatNumber(s.value)}</b>
          </span>
        ))}
      </div>
    </div>
  );
}
