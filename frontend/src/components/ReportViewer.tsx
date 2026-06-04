import { formatINR, formatNumber } from "../lib/format";
import type { ReportColumn, ReportResponse } from "../types";

function isNumeric(col: ReportColumn): boolean {
  return (
    col.fieldtype === "Currency" ||
    col.fieldtype === "Int" ||
    col.fieldtype === "Float"
  );
}

function renderCell(col: ReportColumn, value: string | number | null): string {
  if (value === null || value === undefined || value === "") return "—";
  if (col.fieldtype === "Currency") return formatINR(Number(value));
  if (col.fieldtype === "Int" || col.fieldtype === "Float")
    return formatNumber(Number(value));
  return String(value);
}

export function ReportViewer({ report }: { report: ReportResponse }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            {report.columns.map((c) => (
              <th
                key={c.fieldname}
                className={`px-4 py-3 font-medium ${isNumeric(c) ? "text-right" : ""}`}
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {report.data.length === 0 ? (
            <tr>
              <td
                colSpan={report.columns.length}
                className="px-4 py-10 text-center text-slate-400"
              >
                No data for this period.
              </td>
            </tr>
          ) : (
            report.data.map((row, i) => (
              <tr
                key={i}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                {report.columns.map((c) => (
                  <td
                    key={c.fieldname}
                    className={`px-4 py-3 ${isNumeric(c) ? "text-right tabular-nums" : ""}`}
                  >
                    {renderCell(c, row[c.fieldname] ?? null)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
