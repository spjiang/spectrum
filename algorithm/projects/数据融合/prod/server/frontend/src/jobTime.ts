const LIVE = new Set(["queued", "running", "paused", "awaiting_continue"]);

export function formatJobDateTime(v?: string | null): string {
  if (!v) return "—";
  const s = String(v).replace("T", " ");
  return s.length >= 19 ? s.slice(0, 19) : s;
}

export function jobElapsedHours(
  job: {
    started_at?: string | null;
    created_at?: string | null;
    finished_at?: string | null;
    status?: string | null;
  },
  nowMs = Date.now(),
): string {
  const startMs = Date.parse(String(job.started_at || job.created_at || ""));
  if (!Number.isFinite(startMs)) return "—";
  const live = LIVE.has(job.status || "");
  const endMs = live ? nowMs : Date.parse(String(job.finished_at || ""));
  if (!Number.isFinite(endMs)) return "—";
  const hours = Math.max(0, (endMs - startMs) / 3_600_000);
  return `${hours.toFixed(1)} 小时`;
}
