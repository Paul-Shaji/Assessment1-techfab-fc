import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { FullPageSpinner } from "../components/Spinner";

// Gate for any authenticated route. While the session is being verified we show
// a spinner (not a redirect) to avoid bouncing a logged-in user to /login on
// refresh. Unauthenticated users are sent to /login with the return path.
export default function RequireAuth() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <FullPageSpinner label="Checking session…" />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}
