import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../api/client";

interface UseApiResult<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

// Small fetch-on-mount helper. `deps` controls when the fetcher re-runs.
export function useApi<T>(fn: () => Promise<T>, deps: unknown[] = []): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const run = useCallback(() => {
    let active = true;
    setLoading(true);
    setError(null);
    fn()
      .then((res) => active && setData(res))
      .catch((e: unknown) => {
        if (!active) return;
        setError(e instanceof ApiError ? e.message : "Failed to load data.");
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);

  return { data, error, loading, reload: run };
}
