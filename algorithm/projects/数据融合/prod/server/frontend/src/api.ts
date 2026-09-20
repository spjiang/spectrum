const TOKEN_KEY = "mosaic_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(t: string | null) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

function redirectToLogin() {
  setToken(null);
  localStorage.removeItem("mosaic_user");
  localStorage.removeItem("mosaic_roles");
  if (!window.location.pathname.startsWith("/login")) {
    window.location.replace("/login");
  }
}

function httpErrorMessage(text: string, fallback: string) {
  let msg = text || fallback;
  try {
    const j = JSON.parse(text);
    if (typeof j.detail === "string") msg = j.detail;
  } catch {
    /* keep raw */
  }
  return msg;
}

function rejectUnlessOk(status: number, text: string, fallback: string): never {
  if (status === 401) {
    redirectToLogin();
    const err = new Error("登录已失效，请重新登录");
    err.name = "AuthExpiredError";
    throw err;
  }
  throw new Error(httpErrorMessage(text, fallback));
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
    rejectUnlessOk(res.status, await res.text(), res.statusText);
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
    rejectUnlessOk(res.status, await res.text(), res.statusText);
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
  inspectUpload: (
    file: File,
    onProgress?: (pct: number, phase: "upload" | "parse") => void,
  ) => {
    const body = new FormData();
    body.append("file", file);
    return new Promise<InspectMeta>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/tools/inspect");
      const token = getToken();
      if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
      xhr.upload.onprogress = (ev) => {
        if (!ev.lengthComputable) return;
        onProgress?.(Math.min(99, Math.round((ev.loaded / ev.total) * 100)), "upload");
      };
      xhr.onerror = () => reject(new Error("上传失败"));
      xhr.onabort = () => reject(new DOMException("Aborted", "AbortError"));
      xhr.onload = () => {
        onProgress?.(100, "parse");
        const text = xhr.responseText || "";
        if (xhr.status < 200 || xhr.status >= 300) {
          try {
            rejectUnlessOk(xhr.status, text, xhr.statusText || "解析失败");
          } catch (e) {
            reject(e);
          }
          return;
        }
        try {
          resolve(JSON.parse(text) as InspectMeta);
        } catch {
          reject(new Error("解析响应失败"));
        }
      };
      xhr.send(body);
    });
  },
  inspectPreview: async (id: string) => {
    const headers = new Headers();
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const res = await fetch(`/api/tools/inspect/${id}/preview`, { headers });
    if (!res.ok) rejectUnlessOk(res.status, await res.text(), res.statusText);
    return res.blob();
  },
  inspectPixel: (id: string, col: number, row: number, signal?: AbortSignal) =>
    request<InspectPixel>(`/api/tools/inspect/${id}/pixel?col=${col}&row=${row}`, { signal }),
};

export type InspectBand = {
  index: number;
  name: string;
  wavelength_nm: number | null;
  fwhm_nm: number | null;
  dtype: string;
  valid: number;
  min: number | null;
  max: number | null;
  mean: number | null;
  std: number | null;
  p2: number | null;
  p50: number | null;
  p98: number | null;
};

export type InspectMeta = {
  id: string;
  filename: string;
  format: string;
  size_bytes: number;
  width: number;
  height: number;
  count: number;
  dtype: string;
  nodata: number | null;
  bands: InspectBand[];
  xmp: { raw: string; tags: { ns: string; name: string; value: string }[] };
  exif: Record<string, unknown>;
  tiff: {
    pages?: number;
    compression?: string | null;
    photometric?: string | null;
    tiled?: boolean;
    tags?: { id: number; name: string; value: unknown }[];
    geotiff?: Record<string, unknown> | null;
  } | null;
  geotransform: { origin_x: number; origin_y: number; pixel_w: number; pixel_h: number } | null;
  preview: { width: number; height: number; scale: number };
  stats_sampled?: boolean;
};

export type InspectPixel = {
  col: number;
  row: number;
  values: Array<number | string | null>;
  bands?: Array<{ name: string; value: number | string | null; wavelength_nm: number | null }>;
  rgb: number[] | null;
  hex: string | null;
  x: number | null;
  y: number | null;
};
