import { useApi } from "../lib/useApi";
import { getManufacturingDashboard } from "../api/dashboard";
import { PageHeader, Panel } from "../components/Panel";
import { DataTable, type Column } from "../components/DataTable";
import { SegmentedBar } from "../components/ProgressBar";
import { FullPageSpinner } from "../components/Spinner";
import { ErrorBox } from "../components/Message";
import { formatNumber, formatDate } from "../lib/format";
import type { ItemProduction, ProductionPlanRow, WorkOrderRow } from "../types";

const WO_STATUS_STYLE: Record<string, string> = {
  "Not Started": "bg-slate-100 text-slate-600",
  "In Process": "bg-amber-50 text-amber-700",
  Completed: "bg-emerald-50 text-emerald-700",
  Stopped: "bg-rose-50 text-rose-700",
  Draft: "bg-slate-100 text-slate-500",
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-block rounded-md px-2 py-0.5 text-xs font-medium ${
        WO_STATUS_STYLE[status] ?? "bg-slate-100 text-slate-600"
      }`}
    >
      {status}
    </span>
  );
}

export default function Manufacturing() {
  const { data, error, loading } = useApi(getManufacturingDashboard, []);

  if (loading) return <FullPageSpinner label="Loading production…" />;
  if (error) return <ErrorBox message={error} />;
  if (!data) return null;

  const itemCols: Column<ItemProduction>[] = [
    {
      key: "item_name",
      header: "Item",
      render: (r) => (
        <div>
          <div className="font-medium text-slate-700">
            {r.item_name || r.item_code}
          </div>
          <div className="text-xs text-slate-400">{r.item_code}</div>
        </div>
      ),
    },
    {
      key: "planned",
      header: "Planned",
      align: "right",
      render: (r) => formatNumber(r.planned),
    },
    {
      key: "under_production",
      header: "Under Production",
      align: "right",
      render: (r) => (
        <span className="text-amber-600">{formatNumber(r.under_production)}</span>
      ),
    },
    {
      key: "completed",
      header: "Completed",
      align: "right",
      render: (r) => (
        <span className="text-emerald-600">{formatNumber(r.completed)}</span>
      ),
    },
  ];

  const woCols: Column<WorkOrderRow>[] = [
    {
      key: "name",
      header: "Work Order",
      render: (r) => <span className="font-medium text-slate-700">{r.name}</span>,
    },
    {
      key: "item_name",
      header: "Item",
      render: (r) => r.item_name || r.production_item,
    },
    {
      key: "qty",
      header: "Qty",
      align: "right",
      render: (r) => formatNumber(r.qty),
    },
    {
      key: "produced_qty",
      header: "Produced",
      align: "right",
      render: (r) => formatNumber(r.produced_qty),
    },
    {
      key: "status",
      header: "Status",
      render: (r) => <StatusBadge status={r.status} />,
    },
    {
      key: "planned_start_date",
      header: "Start",
      render: (r) => formatDate(r.planned_start_date),
    },
  ];

  const planCols: Column<ProductionPlanRow>[] = [
    {
      key: "name",
      header: "Plan",
      render: (r) => <span className="font-medium text-slate-700">{r.name}</span>,
    },
    { key: "status", header: "Status" },
    {
      key: "posting_date",
      header: "Date",
      render: (r) => formatDate(r.posting_date),
    },
    {
      key: "total_planned_qty",
      header: "Planned Qty",
      align: "right",
      render: (r) => formatNumber(r.total_planned_qty),
    },
    {
      key: "total_produced_qty",
      header: "Produced Qty",
      align: "right",
      render: (r) => formatNumber(r.total_produced_qty),
    },
  ];

  return (
    <>
      <PageHeader
        title="Manufacturing"
        subtitle="Production status across control-panel items"
      />

      <Panel title="Production Quantity">
        <SegmentedBar
          segments={[
            { label: "Planned", value: data.totals.planned, color: "bg-slate-400" },
            {
              label: "Under production",
              value: data.totals.under_production,
              color: "bg-amber-400",
            },
            {
              label: "Completed",
              value: data.totals.completed,
              color: "bg-emerald-500",
            },
          ]}
        />
      </Panel>

      <div className="mt-6">
        <Panel title="By Item">
          <DataTable
            columns={itemCols}
            rows={data.by_item}
            keyField={(r) => r.item_code}
            empty="No production items."
          />
        </Panel>
      </div>

      <div className="mt-6">
        <Panel title="Work Orders">
          <DataTable
            columns={woCols}
            rows={data.work_orders}
            keyField={(r) => r.name}
            empty="No work orders."
          />
        </Panel>
      </div>

      {data.production_plans.length > 0 && (
        <div className="mt-6">
          <Panel title="Production Plans">
            <DataTable
              columns={planCols}
              rows={data.production_plans}
              keyField={(r) => r.name}
            />
          </Panel>
        </div>
      )}
    </>
  );
}
