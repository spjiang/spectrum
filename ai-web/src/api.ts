/** 调用算法服务上的按层赋能接口。 */

import type { LlmConfig } from "./llmConfig";
import { llmRequestBody } from "./llmConfig";
import type { LayerCase, LayerRun, LayerSummary } from "./types";

export async function fetchAideHealth(): Promise<boolean> {
  try {
    const res = await fetch("/api/v1/l3-aide/health", { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchLayers(): Promise<LayerSummary[]> {
  const res = await fetch("/api/v1/l3-aide/layers", { cache: "no-store" });
  if (!res.ok) throw new Error("层目录加载失败");
  const data = (await res.json()) as { layers: LayerSummary[] };
  return data.layers || [];
}

export async function fetchLayer(id: string): Promise<LayerCase> {
  const res = await fetch(`/api/v1/l3-aide/layers/${id}`, { cache: "no-store" });
  let data: LayerCase & { message?: string };
  try {
    data = (await res.json()) as LayerCase & { message?: string };
  } catch {
    throw new Error("算法服务返回不是 JSON");
  }
  if (!res.ok) {
    throw new Error(data.message || "未知处理层");
  }
  return data;
}

export async function runLayer(id: string, config?: LlmConfig): Promise<LayerRun> {
  const llm = config ? llmRequestBody(config) : undefined;
  const res = await fetch(`/api/v1/l3-aide/layers/${id}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(llm ? { llm } : {}),
  });
  let data: LayerRun;
  try {
    data = (await res.json()) as LayerRun;
  } catch {
    throw new Error("算法服务返回不是 JSON");
  }
  if (!res.ok) {
    throw new Error(data.message || `运行失败 ${res.status}`);
  }
  return data;
}
