import type { AlgorithmCard, RasterMeta, RunResult, SpectrumPoint } from "./types";

async function readJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export async function fetchHealth(): Promise<boolean> {
  try {
    const res = await fetch("/api/v1/console/health", { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function listAlgorithms(): Promise<AlgorithmCard[]> {
  const data = await readJson<{ algorithms: AlgorithmCard[] }>(
    await fetch("/api/v1/console/algorithms"),
  );
  return data.algorithms;
}

export async function getAlgorithm(id: string): Promise<AlgorithmCard> {
  return readJson<AlgorithmCard>(await fetch(`/api/v1/console/algorithms/${id}`));
}

export async function runConsole(opts: {
  id: string;
  useTestdata: boolean;
  file?: File | null;
  file2?: File | null;
  params: string;
}): Promise<RunResult> {
  const form = new FormData();
  form.set("use_testdata", opts.useTestdata ? "true" : "false");
  form.set("params", opts.params || "{}");
  if (!opts.useTestdata) {
    if (opts.file) form.set("file", opts.file);
    if (opts.file2) form.set("file2", opts.file2);
  }
  const res = await fetch(`/api/v1/console/run/${opts.id}`, {
    method: "POST",
    body: form,
  });
  const data = (await res.json()) as RunResult;
  if (!res.ok) {
    throw new Error(data.message || `运行失败 ${res.status}`);
  }
  return data;
}

export async function fetchText(url: string): Promise<string> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`读取失败 ${res.status}`);
  return res.text();
}

export async function fetchJson(url: string): Promise<unknown> {
  return readJson(await fetch(url));
}

export function rasterMetaUrl(previewUrl: string): string {
  const u = new URL(previewUrl, window.location.origin);
  u.pathname = "/api/v1/console/preview/meta";
  u.searchParams.delete("mode");
  return u.pathname + u.search;
}

export function spectrumUrl(previewUrl: string, row: number, col: number): string {
  const u = new URL(previewUrl, window.location.origin);
  u.pathname = "/api/v1/console/preview/spectrum";
  u.searchParams.delete("mode");
  u.searchParams.set("row", String(row));
  u.searchParams.set("col", String(col));
  return u.pathname + u.search;
}

export async function fetchRasterMeta(previewUrl: string): Promise<RasterMeta> {
  return readJson<RasterMeta>(await fetch(rasterMetaUrl(previewUrl)));
}

export async function fetchSpectrum(
  previewUrl: string,
  row: number,
  col: number,
): Promise<SpectrumPoint> {
  return readJson<SpectrumPoint>(await fetch(spectrumUrl(previewUrl, row, col)));
}
