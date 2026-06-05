import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { Factory, Loader2, LogIn } from "lucide-react";
import { useAuth } from "../auth/AuthContext";

interface LocationState {
  from?: { pathname?: string };
}

export default function LoginPage() {
  const { user, loading, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [usr, setUsr] = useState("");
  const [pwd, setPwd] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const from = (location.state as LocationState | null)?.from?.pathname;

  if (!loading && user) return <Navigate to={from || user.home_route} replace />;

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const u = await signIn(usr.trim(), pwd);
      navigate(from || u.home_route, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid email or password.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div 
      className="relative flex min-h-screen items-center justify-center font-['Inter',system-ui,-apple-system,sans-serif]"
      style={{
        backgroundImage: `url('https://images.unsplash.com/photo-1497864149936-d3163f0c0f4b?q=80&w=2069&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
        
      }}
    >
      {/* Overlay for better contrast */}
      <div className="absolute inset-0 bg-black/40" />
      
      {/* Brand header - positioned at top */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-6 lg:p-8">
        <div className="flex items-center gap-3 text-white">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/20 backdrop-blur-sm font-bold">
            TF
          </div>
          <span className="text-lg font-light tracking-wide">TechFab Industries</span>
        </div>
        <p className="text-xs text-white/60 font-light tracking-wider">
          © {new Date().getFullYear()} TechFab Industries
        </p>
      </div>

      {/* Centered more transparent form */}
      <div className="relative z-10 w-full max-w-md">
        <div className="mx-4 rounded-2xl bg-white/20 backdrop-blur-xl border border-white/30 shadow-2xl">
          <div className="p-8">
            {/* Brand icon and title */}
            <div className="mb-8 text-center">
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-white/20 backdrop-blur-sm">
                <Factory size={32} className="text-white" />
              </div>
              <h2 className="text-3xl font-light tracking-wide text-white">Welcome Back</h2>
              <p className="mt-3 text-sm font-light text-white/70 tracking-wide">
                Sign in with your ERPNext credentials
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-lg border border-rose-300/50 bg-rose-500/20 backdrop-blur-sm px-4 py-3 text-sm text-white">
                {error}
              </div>
            )}

            <form onSubmit={onSubmit} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-light tracking-wide text-white/80">
                  Email Address
                </label>
                <input
                  type="email"
                  autoComplete="username"
                  value={usr}
                  onChange={(e) => setUsr(e.target.value)}
                  required
                  placeholder="you@techfab.com"
                  className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-3 text-sm text-white placeholder-white/50 outline-none transition focus:border-white/40 focus:bg-white/20 focus:ring-2 focus:ring-white/10 font-light tracking-wide"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-light tracking-wide text-white/80">
                  Password
                </label>
                <input
                  type="password"
                  autoComplete="current-password"
                  value={pwd}
                  onChange={(e) => setPwd(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full rounded-lg bg-white/10 border border-white/20 px-4 py-3 text-sm text-white placeholder-white/50 outline-none transition focus:border-white/40 focus:bg-white/20 focus:ring-2 focus:ring-white/10 font-light tracking-wide"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-white/90 py-3 text-sm font-medium text-slate-800 transition hover:bg-white hover:shadow-lg disabled:opacity-60 tracking-wide"
              >
                {submitting ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <LogIn size={18} />
                )}
                {submitting ? "Signing in…" : "Sign In"}
              </button>
            </form>
          </div>
        </div>
        
        {/* Management dashboard description */}
        <div className="mt-8 text-center">
          <p className="text-sm font-light text-white/60 tracking-wider">
            Management Dashboard
          </p>
          <p className="mt-1 text-xs font-light text-white/50 tracking-wide">
            Sales • Procurement • Production • Assets • Payroll
          </p>
        </div>
      </div>
    </div>
  );
}