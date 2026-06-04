// Typed bindings for assessment1.api.dashboard.* whitelisted methods.
import { apiGet, apiPost } from "./client";
import type {
  AssetDashboard,
  CurrentUser,
  DashboardStats,
  HRDashboard,
  LoginResponse,
  ManufacturingDashboard,
  NotificationsResponse,
  PurchaseDashboard,
  ReportResponse,
  SalesDashboard,
} from "../types";

const M = "assessment1.api.dashboard";

// Auth
export const login = (usr: string, pwd: string) =>
  apiPost<LoginResponse>(`${M}.login`, { usr, pwd });

export const getCurrentUser = () =>
  apiGet<CurrentUser>(`${M}.get_current_user_roles`);

// GET to sidestep CSRF (no token in the SPA); the method only clears the session.
export const logout = () => apiGet<{ success: boolean }>(`${M}.logout`);

// Executive
export const getDashboardStats = () =>
  apiGet<DashboardStats>(`${M}.get_dashboard_stats`);

export const getNotifications = () =>
  apiGet<NotificationsResponse>(`${M}.get_notifications`);

// Role modules
export const getSalesDashboard = () =>
  apiGet<SalesDashboard>(`${M}.get_sales_dashboard`);

export const getPurchaseDashboard = () =>
  apiGet<PurchaseDashboard>(`${M}.get_purchase_dashboard`);

export const getManufacturingDashboard = () =>
  apiGet<ManufacturingDashboard>(`${M}.get_manufacturing_dashboard`);

export const getAssetDashboard = () =>
  apiGet<AssetDashboard>(`${M}.get_asset_dashboard`);

export const getHRDashboard = (attendance_date?: string) =>
  apiGet<HRDashboard>(`${M}.get_hr_dashboard`, { attendance_date });

// Reports
export const getManagementReport = () =>
  apiGet<ReportResponse>(`${M}.get_techfab_management_report`);

export const getPayrollSummary = (from_date?: string, to_date?: string) =>
  apiGet<ReportResponse>(`${M}.get_payroll_summary_report`, { from_date, to_date });
