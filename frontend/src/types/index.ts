// Shared API response types. These mirror assessment1/api/dashboard.py exactly.
// Frappe wraps every whitelisted return value in { message: ... }; the api client
// unwraps `.message`, so these describe the *inner* payload.

export type ModuleKey = "sales" | "purchase" | "manufacturing" | "assets" | "hr";

export interface SessionUser {
  user: string;
  full_name: string;
  roles: string[];
  modules: ModuleKey[];
  home_route: string;
}

export interface CurrentUser extends SessionUser {
  email: string;
}

export interface LoginResponse extends SessionUser {
  success: boolean;
}

// ── Executive dashboard ──────────────────────────────────────────────
export interface StatCard {
  key: string;
  label: string;
  icon: string;
  value: number;
  trend: number;
  trend_label: string;
}
export interface DashboardStats {
  cards: StatCard[];
}

export interface NotificationItem {
  asset_name: string;
  maintenance_task: string;
  next_due_date: string;
  days_to_due: number;
}
export interface NotificationsResponse {
  count: number;
  items: NotificationItem[];
}

// ── Sales ────────────────────────────────────────────────────────────
export interface Quotation {
  name: string;
  party_name: string;
  customer_name: string;
  grand_total: number;
  status: string;
  transaction_date: string;
}
export interface SalesOrder {
  name: string;
  customer: string;
  customer_name: string;
  grand_total: number;
  status: string;
  transaction_date: string;
}
export interface OrderCategory {
  category: "Government" | "Corporate" | "Retail" | "Other";
  prefix: string;
  count: number;
  total: number;
  orders: SalesOrder[];
}
export interface RewardLogEntry {
  sales_person: string;
  customer: string;
  collection_amount: number;
  points_earned: number;
  date: string;
  remarks: string;
}
export interface RewardSummary {
  sales_person: string;
  total_points: number;
  total_collection: number;
  entries: number;
}
export interface RewardTier {
  label: string;
  rule: string;
}
export interface SalesDashboard {
  quotations: Quotation[];
  orders_by_category: OrderCategory[];
  reward_ledger: RewardLogEntry[];
  reward_summary: RewardSummary[];
  reward_tiers: RewardTier[];
}

// ── Purchase ─────────────────────────────────────────────────────────
export interface InventoryItem {
  item_code: string;
  item_name: string;
  item_group: string;
  uom: string;
  available: number;
  shortage: number;
  ordered: number;
  projected: number;
}
export interface PurchaseOrderRow {
  name: string;
  supplier: string;
  supplier_name: string;
  grand_total: number;
  status: string;
  transaction_date: string;
  per_received: number;
}
export interface PurchaseDashboard {
  inventory: InventoryItem[];
  active_purchase_orders: PurchaseOrderRow[];
}

// ── Manufacturing ────────────────────────────────────────────────────
export interface WorkOrderRow {
  name: string;
  production_item: string;
  item_name: string;
  qty: number;
  produced_qty: number;
  status: string;
  planned_start_date: string | null;
}
export interface ItemProduction {
  item_code: string;
  item_name: string;
  planned: number;
  under_production: number;
  completed: number;
}
export interface ProductionTotals {
  planned: number;
  under_production: number;
  completed: number;
}
export interface ProductionPlanRow {
  name: string;
  status: string;
  posting_date: string;
  total_planned_qty: number;
  total_produced_qty: number;
}
export interface ManufacturingDashboard {
  work_orders: WorkOrderRow[];
  by_item: ItemProduction[];
  totals: ProductionTotals;
  production_plans: ProductionPlanRow[];
}

// ── Assets ───────────────────────────────────────────────────────────
export interface Asset {
  name: string;
  asset_name: string;
  asset_category: string;
  location: string | null;
  status: string;
  purchase_date: string | null;
  gross_purchase_amount: number;
}
export type AlertSeverity = "overdue" | "critical" | "warning";
export interface MaintenanceAlert {
  asset_name: string;
  maintenance_task: string;
  maintenance_type: string;
  next_due_date: string;
  last_completion_date: string | null;
  days_to_due: number;
  severity: AlertSeverity;
}
export interface AssetDashboard {
  assets: Asset[];
  maintenance_alerts: MaintenanceAlert[];
}

// ── HR & Payroll ─────────────────────────────────────────────────────
export interface AttendanceLog {
  employee: string;
  employee_name: string;
  department: string | null;
  status: string;
  custom_overtime_hours: number;
  in_time: string | null;
  out_time: string | null;
}
export interface OvertimeLog {
  employee: string;
  employee_name: string;
  attendance_date: string;
  custom_overtime_hours: number;
  department: string | null;
}
export interface PayrollRow {
  salary_slip: string;
  employee: string;
  employee_name: string;
  department: string | null;
  net_pay: number;
  basic: number | null;
  overtime: number | null;
  attendance_deduction: number | null;
}
export interface HRDashboard {
  attendance: AttendanceLog[];
  overtime_logs: OvertimeLog[];
  payroll: PayrollRow[];
  period: { from_date: string; to_date: string };
}

// ── Reports (Script Report passthrough) ──────────────────────────────
export interface ReportColumn {
  label: string;
  fieldname: string;
  fieldtype: string;
  width?: number;
  options?: string;
}
export interface ReportResponse {
  columns: ReportColumn[];
  data: Array<Record<string, string | number | null>>;
  from_date?: string;
  to_date?: string;
}
