import { useApi } from "../lib/useApi";
import { getSalesDashboard } from "../api/dashboard";
import { PageHeader, Panel } from "../components/Panel";
import { DataTable, type Column } from "../components/DataTable";
import { FullPageSpinner } from "../components/Spinner";
import { ErrorBox } from "../components/Message";
import { formatINR, formatDate, formatNumber } from "../lib/format";
import type {
  OrderCategory,
  RewardLogEntry,
  RewardSummary,
  SalesOrder,
} from "../types";

const CATEGORY_STYLE: Record<string, string> = {
  Government: "bg-indigo-50 text-indigo-700 border-indigo-200",
  Corporate: "bg-sky-50 text-sky-700 border-sky-200",
  Retail: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Other: "bg-slate-100 text-slate-600 border-slate-200",
};

function categoryOf(name: string): string {
  const p = name.split("-")[0]?.toUpperCase();
  if (p === "GOV") return "Government";
  if (p === "COR") return "Corporate";
  if (p === "RET") return "Retail";
  return "Other";
}

function CategoryBadge({ category }: { category: string }) {
  return (
    <span
      className={`inline-block rounded-md border px-2 py-0.5 text-xs font-medium ${
        CATEGORY_STYLE[category] ?? CATEGORY_STYLE.Other
      }`}
    >
      {category}
    </span>
  );
}

function CategoryCard({ bucket }: { bucket: OrderCategory }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-card">
      <CategoryBadge category={bucket.category} />
      <div className="mt-3 text-2xl font-semibold text-slate-900">
        {formatNumber(bucket.count)}
      </div>
      <div className="text-xs text-slate-500">
        orders · {formatINR(bucket.total)}
      </div>
    </div>
  );
}

export default function Sales() {
  const { data, error, loading } = useApi(getSalesDashboard, []);

  if (loading) return <FullPageSpinner label="Loading sales…" />;
  if (error) return <ErrorBox message={error} />;
  if (!data) return null;

  const allOrders = data.orders_by_category.flatMap((b) => b.orders);

  const orderCols: Column<SalesOrder>[] = [
    {
      key: "name",
      header: "Order",
      render: (r) => <span className="font-medium text-slate-700">{r.name}</span>,
    },
    {
      key: "category",
      header: "Category",
      render: (r) => <CategoryBadge category={categoryOf(r.name)} />,
    },
    {
      key: "customer_name",
      header: "Customer",
      render: (r) => r.customer_name || r.customer,
    },
    { key: "status", header: "Status" },
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

  const summaryCols: Column<RewardSummary>[] = [
    {
      key: "sales_person",
      header: "Salesperson",
      render: (r) => (
        <span className="font-medium text-slate-700">{r.sales_person}</span>
      ),
    },
    {
      key: "entries",
      header: "Entries",
      align: "right",
      render: (r) => formatNumber(r.entries),
    },
    {
      key: "total_collection",
      header: "Collection",
      align: "right",
      render: (r) => formatINR(r.total_collection),
    },
    {
      key: "total_points",
      header: "Points",
      align: "right",
      render: (r) => (
        <b className="text-brand-700">{formatNumber(r.total_points)}</b>
      ),
    },
  ];

  const ledgerCols: Column<RewardLogEntry>[] = [
    { key: "date", header: "Date", render: (r) => formatDate(r.date) },
    { key: "sales_person", header: "Salesperson" },
    { key: "customer", header: "Customer" },
    {
      key: "collection_amount",
      header: "Collection",
      align: "right",
      render: (r) => formatINR(r.collection_amount),
    },
    {
      key: "points_earned",
      header: "Points",
      align: "right",
      render: (r) => formatNumber(r.points_earned),
    },
  ];

  return (
    <>
      <PageHeader
        title="Sales"
        subtitle="Orders by customer category and salesperson rewards"
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {data.orders_by_category.map((b) => (
          <CategoryCard key={b.category} bucket={b} />
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <Panel title="Sales Orders">
            <DataTable
              columns={orderCols}
              rows={allOrders}
              keyField={(r) => r.name}
              empty="No sales orders."
            />
          </Panel>
        </div>
        <div className="space-y-6">
          <Panel title="Reward Tiers">
            <ul className="space-y-2 text-sm">
              {data.reward_tiers.map((t) => (
                <li key={t.label} className="flex justify-between gap-3">
                  <span className="text-slate-600">{t.label}</span>
                  <span className="font-medium text-slate-800">{t.rule}</span>
                </li>
              ))}
            </ul>
          </Panel>
          <Panel title="Reward Leaders">
            <DataTable
              columns={summaryCols}
              rows={data.reward_summary}
              keyField={(r) => r.sales_person}
              empty="No rewards yet."
            />
          </Panel>
        </div>
      </div>

      <div className="mt-6">
        <Panel title="Reward Points Ledger">
          <DataTable
            columns={ledgerCols}
            rows={data.reward_ledger}
            empty="No reward entries."
          />
        </Panel>
      </div>
    </>
  );
}
