const TOKEN_KEY = "mosaic_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(t: string | null) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers || {});
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!(init.body instanceof FormData) && init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(path, { ...init, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return (await res.text()) as T;
}

export const api = {
  login: async (username: string, password: string) => {
    const body = new URLSearchParams({ username, password });
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) throw new Error("登录失败");
    return res.json() as Promise<{ access_token: string; roles: string[] }>;
  },
  health: () => request<{ status: string }>("/api/health"),
  paramDefs: () => request<any[]>("/api/param-definitions"),
  profiles: () => request<any[]>("/api/profiles"),
  createProfile: (body: any) => request("/api/profiles", { method: "POST", body: JSON.stringify(body) }),
  updateProfile: (id: number, body: any) =>
    request(`/api/profiles/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  jobs: () => request<any[]>("/api/jobs"),
  job: (id: string) => request<any>(`/api/jobs/${id}`),
  createJob: (body: any) => request("/api/jobs", { method: "POST", body: JSON.stringify(body) }),
  jobAction: (id: string, action: string, body?: any) =>
    request(`/api/jobs/${id}/${action}`, { method: "POST", body: JSON.stringify(body || {}) }),
  logs: (id: string) => request<string>(`/api/jobs/${id}/logs?tail=300`),
  cliGuide: () => request<string>("/api/docs/cli-guide"),
};
