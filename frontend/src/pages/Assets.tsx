import { useApi } from "../lib/useApi";
import { getAssetDashboard } from "../api/dashboard";
import { PageHeader, Panel } from "../components/Panel";
import { DataTable, type Column } from "../components/DataTable";
import { FullPageSpinner } from "../components/Spinner";
import { ErrorBox } from "../components/Message";
import { formatINR, formatDate } from "../lib/format";
import type { AlertSeverity, Asset, MaintenanceAlert } from "../types";

const SEVERITY_STYLE: Record<AlertSeverity, string> = {
  overdue: "bg-rose-50 text-rose-700 border-rose-200",
  critical: "bg-amber-50 text-amber-700 border-amber-200",
  warning: "bg-yellow-50 text-yellow-700 border-yellow-200",
};
const SEVERITY_LABEL: Record<AlertSeverity, string> = {
  overdue: "Overdue",
  critical: "Due ≤30d",
  warning: "Due ≤90d",
};

export default function Assets() {
  const { data, error, loading } = useApi(getAssetDashboard, []);

  if (loading) return <FullPageSpinner label="Loading assets…" />;
  if (error) return <ErrorBox message={error} />;
  if (!data) return null;

  const alertCols: Column<MaintenanceAlert>[] = [
    {
      key: "asset_name",
      header: "Asset",
      render: (r) => (
        <span className="font-medium text-slate-700">{r.asset_name}</span>
      ),
    },
    { key: "maintenance_task", header: "Task" },
    { key: "maintenance_type", header: "Type" },
    {
      key: "next_due_date",
      header: "Due",
      render: (r) => formatDate(r.next_due_date),
    },
    {
      key: "severity",
      header: "Status",
      render: (r) => (
        <span
          className={`inline-block rounded-md border px-2 py-0.5 text-xs font-medium ${SEVERITY_STYLE[r.severity]}`}
        >
          {SEVERITY_LABEL[r.severity]} ·{" "}
          {r.days_to_due < 0
            ? `${Math.abs(r.days_to_due)}d ago`
            : `${r.days_to_due}d`}
        </span>
      ),
    },
  ];

  const assetCols: Column<Asset>[] = [
    {
      key: "asset_name",
      header: "Asset",
      render: (r) => (
        <span className="font-medium text-slate-700">{r.asset_name}</span>
      ),
    },
    { key: "asset_category", header: "Category" },
    { key: "location", header: "Location", render: (r) => r.location || "—" },
    { key: "status", header: "Status" },
    {
      key: "purchase_date",
      header: "Purchased",
      render: (r) => formatDate(r.purchase_date),
    },
    {
      key: "gross_purchase_amount",
      header: "Value",
      align: "right",
      render: (r) => formatINR(r.gross_purchase_amount),
    },
  ];

  return (
    <>
      <PageHeader
        title="Assets & Service"
        subtitle="Factory equipment and preventive maintenance (90-day window)"
      />

      <Panel title="Maintenance Alerts">
        <DataTable
          columns={alertCols}
          rows={data.maintenance_alerts}
          keyField={(r, i) => `${r.asset_name}-${i}`}
          empty="No maintenance due within 90 days."
        />
      </Panel>

      <div className="mt-6">
        <Panel title="Asset Registry">
          <DataTable
            columns={assetCols}
            rows={data.assets}
            keyField={(r) => r.name}
            empty="No assets."
          />
        </Panel>
      </div>
    </>
  );
}
