import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import RequireAuth from "./auth/RequireAuth";
import RequireRole from "./auth/RequireRole";
import DashboardLayout from "./layout/DashboardLayout";
import LoginPage from "./pages/LoginPage";
import ExecutiveDashboard from "./pages/ExecutiveDashboard";
import Sales from "./pages/Sales";
import Purchase from "./pages/Purchase";
import Manufacturing from "./pages/Manufacturing";
import Assets from "./pages/Assets";
import HR from "./pages/HR";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Everything below requires an authenticated session */}
          <Route element={<RequireAuth />}>
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard" element={<ExecutiveDashboard />} />

              <Route element={<RequireRole module="sales" />}>
                <Route path="/sales" element={<Sales />} />
              </Route>
              <Route element={<RequireRole module="purchase" />}>
                <Route path="/purchase" element={<Purchase />} />
              </Route>
              <Route element={<RequireRole module="manufacturing" />}>
                <Route path="/manufacturing" element={<Manufacturing />} />
              </Route>
              <Route element={<RequireRole module="assets" />}>
                <Route path="/assets" element={<Assets />} />
              </Route>
              <Route element={<RequireRole module="hr" />}>
                <Route path="/hr" element={<HR />} />
              </Route>
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
