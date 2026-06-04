import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  empty?: string;
  keyField?: (row: T, index: number) => string | number;
}

const alignClass = (align?: "left" | "right" | "center") =>
  align === "right" ? "text-right" : align === "center" ? "text-center" : "";

export function DataTable<T>({
  columns,
  rows,
  empty = "No records found.",
  keyField,
}: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            {columns.map((c) => (
              <th key={c.key} className={`px-4 py-3 font-medium ${alignClass(c.align)}`}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-10 text-center text-slate-400"
              >
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((row, i) => (
              <tr
                key={keyField ? keyField(row, i) : i}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                {columns.map((c) => {
                  const fallback = (row as Record<string, unknown>)[c.key];
                  return (
                    <td
                      key={c.key}
                      className={`px-4 py-3 ${alignClass(c.align)} ${c.className ?? ""}`}
                    >
                      {c.render
                        ? c.render(row)
                        : fallback === null || fallback === undefined || fallback === ""
                          ? "—"
                          : (fallback as ReactNode)}
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
