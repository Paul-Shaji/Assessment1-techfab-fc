import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  getCurrentUser,
  login as apiLogin,
  logout as apiLogout,
} from "../api/dashboard";
import type { CurrentUser, ModuleKey } from "../types";

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  signIn: (usr: string, pwd: string) => Promise<CurrentUser>;
  signOut: () => Promise<void>;
  canAccess: (module: ModuleKey) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Bootstrap from the server — the session is the source of truth, never
  // anything cached in JS. Runs once on mount.
  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((u) => {
        if (active) setUser(u);
      })
      .catch(() => {
        if (active) setUser(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const signIn = async (usr: string, pwd: string): Promise<CurrentUser> => {
    const res = await apiLogin(usr, pwd);
    const current: CurrentUser = {
      user: res.user,
      email: res.user,
      full_name: res.full_name,
      roles: res.roles,
      modules: res.modules,
      home_route: res.home_route,
    };
    setUser(current);
    return current;
  };

  const signOut = async (): Promise<void> => {
    try {
      await apiLogout();
    } finally {
      setUser(null);
    }
  };

  const canAccess = (module: ModuleKey): boolean =>
    !!user && user.modules.includes(module);

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut, canAccess }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
