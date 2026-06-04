import { useState } from "react";
import { FileBarChart, IndianRupee, X } from "lucide-react";
import { useApi } from "../lib/useApi";
import {
  getDashboardStats,
  getManagementReport,
  getPayrollSummary,
} from "../api/dashboard";
import { StatCard } from "../components/StatCard";
import { PageHeader, Panel } from "../components/Panel";
import { ReportViewer } from "../components/ReportViewer";
import { FullPageSpinner, Spinner } from "../components/Spinner";
import type { ReportResponse } from "../types";

type OpenReport = { title: string; data: ReportResponse } | null;

export default function ExecutiveDashboard() {
  const { data, error, loading } = useApi(getDashboardStats, []);
  const [report, setReport] = useState<OpenReport>(null);
  const [reportLoading, setReportLoading] = useState(false);

  const openReport = async (which: "mgmt" | "payroll") => {
    setReportLoading(true);
    try {
      if (which === "mgmt") {
        setReport({
          title: "TechFab Management Report",
          data: await getManagementReport(),
        });
      } else {
        setReport({
          title: "Department-Wise Payroll Summary",
          data: await getPayrollSummary(),
        });
      }
    } finally {
      setReportLoading(false);
    }
  };

  if (loading) return <FullPageSpinner label="Loading metrics…" />;

  return (
    <>
      <PageHeader
        title="Management Dashboard"
        subtitle="TechFab Industries — executive overview"
      />

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data?.cards.map((card) => (
              <StatCard key={card.key} card={card} />
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => openReport("mgmt")}
              className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700"
            >
              <FileBarChart size={18} /> View Management Report
            </button>
            <button
              onClick={() => openReport("payroll")}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              <IndianRupee size={18} /> View Payroll Summary
            </button>
          </div>

          {reportLoading && (
            <div className="mt-6 flex justify-center">
              <Spinner size={28} />
            </div>
          )}

          {report && !reportLoading && (
            <div className="mt-6">
              <Panel
                title={report.title}
                actions={
                  <button
                    onClick={() => setReport(null)}
                    className="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-slate-600"
                  >
                    <X size={14} /> Close
                  </button>
                }
              >
                <ReportViewer report={report.data} />
              </Panel>
            </div>
          )}
        </>
      )}
    </>
  );
}
