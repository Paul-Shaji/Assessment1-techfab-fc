import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";
import type { ModuleKey } from "../types";

// Module-level gate. Assumes RequireAuth already ran (user is present). If the
// user lacks the module, bounce them to their own home route rather than 404.
// This is UX only — the backend re-checks every fetch via _require_any_role.
export default function RequireRole({ module }: { module: ModuleKey }) {
  const { user, canAccess } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (!canAccess(module)) return <Navigate to={user.home_route} replace />;
  return <Outlet />;
}
