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
    let msg = text || res.statusText;
    try {
      const j = JSON.parse(text);
      if (typeof j.detail === "string") msg = j.detail;
    } catch {
      /* keep raw */
    }
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return (await res.text()) as T;
}

async function openAuthedFile(path: string, fallbackName: string) {
  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(path, { headers });
  if (!res.ok) {
    const text = await res.text();
    let msg = text || res.statusText;
    try {
      const j = JSON.parse(text);
      if (typeof j.detail === "string") msg = j.detail;
    } catch {
      /* keep raw */
    }
    throw new Error(msg);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const opened = window.open(url, "_blank", "noopener");
  if (!opened) {
    const a = document.createElement("a");
    a.href = url;
    a.download = fallbackName;
    a.click();
  }
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
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
  systemStatus: () =>
    request<{
      status: string;
      postgres: string;
      rabbitmq: string;
      worker: string;
      can_edit: boolean;
    }>("/api/system/status"),
  getWorkerEnv: () =>
    request<{
      worker_env: {
        rabbitmq_url: string;
        pythonpath: string;
        workdir: string;
        mplbackend: string;
        data_roots: string;
        default_input_dir: string;
        default_output_dir: string;
        source: string;
      };
      can_edit: boolean;
    }>("/api/system/worker-env"),
  updateWorkerEnv: (body: {
    data_roots: string;
    default_input_dir: string;
    default_output_dir: string;
  }) =>
    request<{
      worker_env: {
        rabbitmq_url: string;
        pythonpath: string;
        workdir: string;
        mplbackend: string;
        data_roots: string;
        default_input_dir: string;
        default_output_dir: string;
        source: string;
      };
      can_edit: boolean;
    }>("/api/system/worker-env", { method: "PUT", body: JSON.stringify(body) }),
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
  deleteJob: (id: string) => request<void>(`/api/jobs/${id}`, { method: "DELETE" }),
  clearJobs: () => request<{ deleted: number }>("/api/jobs", { method: "DELETE" }),
  logs: (id: string) => request<string>(`/api/jobs/${id}/logs?tail=800`),
  openJobReport: (id: string) => openAuthedFile(`/api/jobs/${id}/report.pdf`, "质量报告.pdf"),
  workerInspect: () => request<any>("/api/system/worker"),
  killAllWorkerJobs: () => request<{ killed: number }>("/api/system/worker/kill-all", { method: "POST" }),
  cliGuide: () => request<string>("/api/docs/cli-guide"),
  paramGuide: () => request<string>("/api/docs/param-guide"),
  users: () => request<any[]>("/api/users"),
  createUser: (body: { username: string; password: string; roles: string[] }) =>
    request("/api/users", { method: "POST", body: JSON.stringify(body) }),
  updateUser: (id: number, body: { password?: string; roles?: string[]; is_active?: boolean }) =>
    request(`/api/users/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  rbac: () => request<{ menus: Record<string, string[]> }>("/api/rbac"),
  updateRoleMenus: (role: string, menus: string[]) =>
    request<{ menus: Record<string, string[]> }>(`/api/rbac/roles/${role}`, {
      method: "PUT",
      body: JSON.stringify({ menus }),
    }),
  updatePermissionRoles: (key: string, roles: string[]) =>
    request<{ menus: Record<string, string[]> }>(`/api/rbac/permissions/${key}`, {
      method: "PUT",
      body: JSON.stringify({ roles }),
    }),
};
