// Thin typed wrapper over Frappe's /api/method endpoints.
//
// Auth is cookie-based: the httpOnly `sid` set by login() is sent automatically
// because every request uses credentials:"include". We never store the session
// in JS. Frappe wraps whitelisted returns in { message }, which we unwrap here.

const BASE = "/api/method";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type ParamValue = string | number | boolean | undefined | null;
type Params = Record<string, ParamValue>;

// When the SPA is served from the Frappe site, window.csrf_token is injected.
// Behind the Vite dev proxy it is absent, so we fall back to the "fetch" sentinel.
function csrfToken(): string {
  const w = window as unknown as { csrf_token?: string };
  return w.csrf_token || "fetch";
}

function buildQuery(params: Params): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") q.append(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

function extractError(json: Record<string, unknown>, status: number): string {
  // Frappe puts user-facing errors in _server_messages: a JSON string whose
  // entries are themselves JSON strings like {"message": "..."}.
  const raw = json["_server_messages"];
  if (typeof raw === "string") {
    try {
      const arr = JSON.parse(raw) as string[];
      if (arr.length) {
        const first = JSON.parse(arr[0]) as { message?: string };
        if (first.message) return stripHtml(first.message);
      }
    } catch {
      /* fall through */
    }
  }
  if (typeof json["exception"] === "string") return json["exception"] as string;
  if (typeof json["message"] === "string") return json["message"] as string;
  return `Request failed (${status})`;
}

function stripHtml(s: string): string {
  return s.replace(/<[^>]*>/g, "").trim();
}

async function handle<T>(res: Response): Promise<T> {
  const text = await res.text();
  let json: Record<string, unknown> = {};
  try {
    json = text ? (JSON.parse(text) as Record<string, unknown>) : {};
  } catch {
    json = { _raw: text };
  }
  if (!res.ok) throw new ApiError(extractError(json, res.status), res.status);
  return json["message"] as T;
}

export async function apiGet<T>(method: string, params: Params = {}): Promise<T> {
  const res = await fetch(`${BASE}/${method}${buildQuery(params)}`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  return handle<T>(res);
}

export async function apiPost<T>(method: string, body: Params = {}): Promise<T> {
  const form = new URLSearchParams();
  for (const [k, v] of Object.entries(body)) {
    if (v !== undefined && v !== null && v !== "") form.append(k, String(v));
  }
  const res = await fetch(`${BASE}/${method}`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Frappe-CSRF-Token": csrfToken(),
      Accept: "application/json",
    },
    body: form.toString(),
  });
  return handle<T>(res);
}
