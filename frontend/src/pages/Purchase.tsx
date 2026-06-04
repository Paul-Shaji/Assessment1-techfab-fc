import { Package } from "lucide-react";
import { useApi } from "../lib/useApi";
import { getPurchaseDashboard } from "../api/dashboard";
import { PageHeader, Panel } from "../components/Panel";
import { DataTable, type Column } from "../components/DataTable";
import { SegmentedBar } from "../components/ProgressBar";
import { FullPageSpinner } from "../components/Spinner";
import { ErrorBox } from "../components/Message";
import { formatINR, formatDate, formatNumber } from "../lib/format";
import type { InventoryItem, PurchaseOrderRow } from "../types";

export default function Purchase() {
  const { data, error, loading } = useApi(getPurchaseDashboard, []);

  if (loading) return <FullPageSpinner label="Loading inventory…" />;
  if (error) return <ErrorBox message={error} />;
  if (!data) return null;

  const totals = data.inventory.reduce(
    (acc, i) => ({
      available: acc.available + i.available,
      shortage: acc.shortage + i.shortage,
      ordered: acc.ordered + i.ordered,
    }),
    { available: 0, shortage: 0, ordered: 0 },
  );

  const invCols: Column<InventoryItem>[] = [
    {
      key: "item_name",
      header: "Item",
      render: (r) => (
        <div>
          <div className="font-medium text-slate-700">
            {r.item_name || r.item_code}
          </div>
          <div className="text-xs text-slate-400">{r.item_group}</div>
        </div>
      ),
    },
    {
      key: "available",
      header: "Available",
      align: "right",
      render: (r) => (
        <span className="font-medium text-emerald-600">
          {formatNumber(r.available)}
        </span>
      ),
    },
    {
      key: "shortage",
      header: "Shortage",
      align: "right",
      render: (r) =>
        r.shortage > 0 ? (
          <span className="font-medium text-rose-600">
            {formatNumber(r.shortage)}
          </span>
        ) : (
          <span className="text-slate-300">—</span>
        ),
    },
    {
      key: "ordered",
      header: "Ordered",
      align: "right",
      render: (r) => (
        <span className="text-amber-600">{formatNumber(r.ordered)}</span>
      ),
    },
    {
      key: "uom",
      header: "UOM",
      render: (r) => <span className="text-slate-400">{r.uom}</span>,
    },
  ];

  const poCols: Column<PurchaseOrderRow>[] = [
    {
      key: "name",
      header: "PO",
      render: (r) => <span className="font-medium text-slate-700">{r.name}</span>,
    },
    {
      key: "supplier_name",
      header: "Supplier",
      render: (r) => r.supplier_name || r.supplier,
    },
    { key: "status", header: "Status" },
    {
      key: "per_received",
      header: "Received",
      align: "right",
      render: (r) => `${formatNumber(r.per_received)}%`,
    },
    {
      key: "transaction_date",
      header: "Date",
      render: (r) => formatDate(r.transaction_date),
    },
    {
      key: "grand_total",
      header: "Total",
      align: "right",
      render: (r) => formatINR(r.grand_total),
    },
  ];

  return (
    <>
      <PageHeader
        icon={Package}
        title="Purchase"
        subtitle="Raw-material availability, shortages and open orders"
      />

      <Panel title="Stock Position (all stock items)">
        <SegmentedBar
          segments={[
            { label: "Available", value: totals.available, color: "bg-emerald-500" },
            { label: "Shortage (to buy)", value: totals.shortage, color: "bg-rose-500" },
            { label: "Already ordered", value: totals.ordered, color: "bg-amber-400" },
          ]}
        />
      </Panel>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Panel title="Inventory">
          <DataTable
            columns={invCols}
            rows={data.inventory}
            keyField={(r) => r.item_code}
            empty="No stock items found."
          />
        </Panel>
        <Panel title="Active Purchase Orders">
          <DataTable
            columns={poCols}
            rows={data.active_purchase_orders}
            keyField={(r) => r.name}
            empty="No open purchase orders."
          />
        </Panel>
      </div>
    </>
  );
}
