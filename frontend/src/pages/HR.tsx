import { useState } from "react";
import { useApi } from "../lib/useApi";
import { getHRDashboard } from "../api/dashboard";
import { PageHeader, Panel } from "../components/Panel";
import { DataTable, type Column } from "../components/DataTable";
import { FullPageSpinner } from "../components/Spinner";
import { ErrorBox } from "../components/Message";
import { formatINR, formatDate, formatNumber } from "../lib/format";
import type { AttendanceLog, OvertimeLog, PayrollRow } from "../types";

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

const ATT_STYLE: Record<string, string> = {
  Present: "bg-emerald-50 text-emerald-700",
  Absent: "bg-rose-50 text-rose-700",
  "On Leave": "bg-amber-50 text-amber-700",
  "Half Day": "bg-sky-50 text-sky-700",
};

export default function HR() {
  const [date, setDate] = useState(todayISO());
  const { data, error, loading } = useApi(() => getHRDashboard(date), [date]);

  const attCols: Column<AttendanceLog>[] = [
    {
      key: "employee_name",
      header: "Employee",
      render: (r) => (
        <span className="font-medium text-slate-700">{r.employee_name}</span>
      ),
    },
    { key: "department", header: "Department", render: (r) => r.department || "—" },
    {
      key: "status",
      header: "Status",
      render: (r) => (
        <span
          className={`inline-block rounded-md px-2 py-0.5 text-xs font-medium ${
            ATT_STYLE[r.status] ?? "bg-slate-100 text-slate-600"
          }`}
        >
          {r.status}
        </span>
      ),
    },
    {
      key: "custom_overtime_hours",
      header: "OT (hrs)",
      align: "right",
      render: (r) => formatNumber(r.custom_overtime_hours),
    },
  ];

  const otCols: Column<OvertimeLog>[] = [
    {
      key: "attendance_date",
      header: "Date",
      render: (r) => formatDate(r.attendance_date),
    },
    { key: "employee_name", header: "Employee" },
    {
      key: "custom_overtime_hours",
      header: "Overtime (hrs)",
      align: "right",
      render: (r) => formatNumber(r.custom_overtime_hours),
    },
  ];

  const payCols: Column<PayrollRow>[] = [
    {
      key: "employee_name",
      header: "Employee",
      render: (r) => (
        <span className="font-medium text-slate-700">{r.employee_name}</span>
      ),
    },
    { key: "department", header: "Department", render: (r) => r.department || "—" },
    {
      key: "basic",
      header: "Basic",
      align: "right",
      render: (r) => formatINR(r.basic ?? 0),
    },
    {
      key: "overtime",
      header: "Overtime",
      align: "right",
      render: (r) => formatINR(r.overtime ?? 0),
    },
    {
      key: "attendance_deduction",
      header: "Deduction",
      align: "right",
      render: (r) => (
        <span className="text-rose-600">
          {formatINR(r.attendance_deduction ?? 0)}
        </span>
      ),
    },
    {
      key: "net_pay",
      header: "Net Pay",
      align: "right",
      render: (r) => <b>{formatINR(r.net_pay)}</b>,
    },
  ];

  return (
    <>
      <PageHeader
        title="HR & Payroll"
        subtitle={
          data
            ? `Payroll period ${formatDate(data.period.from_date)} – ${formatDate(data.period.to_date)}`
            : "Attendance, overtime and payroll"
        }
        actions={
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm outline-none focus:border-brand-500"
          />
        }
      />

      {error ? (
        <ErrorBox message={error} />
      ) : loading ? (
        <FullPageSpinner label="Loading HR…" />
      ) : data ? (
        <>
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <Panel title={`Attendance · ${formatDate(date)}`}>
              <DataTable
                columns={attCols}
                rows={data.attendance}
                keyField={(r) => r.employee}
                empty="No attendance for this date."
              />
            </Panel>
            <Panel title="Production Overtime (this month)">
              <DataTable
                columns={otCols}
                rows={data.overtime_logs}
                keyField={(r, i) => `${r.employee}-${i}`}
                empty="No overtime logged."
              />
            </Panel>
          </div>
          <div className="mt-6">
            <Panel title="Monthly Payroll">
              <DataTable
                columns={payCols}
                rows={data.payroll}
                keyField={(r) => r.salary_slip}
                empty="No submitted salary slips this period."
              />
            </Panel>
          </div>
        </>
      ) : null}
    </>
  );
}
