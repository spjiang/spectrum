/** 调用算法服务上的 L3 参谋接口。 */

import type { AideResponse } from "./types";

const DEFAULT: AideResponse["question"] = {
  title: "密植水稻，MAX-S810 刚采完，要不要补氮？",
  crop: "水稻",
  canopy: "密植封垄",
  sensor: "MAX-S810",
  task: "氮素辅助判断",
  hook: "对方机载已经会出 NDVI/NDRE。本页要证明的是：AI 团队决定「这场用哪个」，并挡住误用。",
};

export const defaultQuestion = DEFAULT;

export async function fetchAideHealth(): Promise<boolean> {
  try {
    const res = await fetch("/api/v1/l3-aide/health", { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function runAide(): Promise<AideResponse> {
  const res = await fetch("/api/v1/l3-aide/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenarioId: "rice_dense_max_n" }),
  });
  let data: AideResponse;
  try {
    data = (await res.json()) as AideResponse;
  } catch {
    throw new Error("算法服务返回不是 JSON");
  }
  if (!res.ok) {
    throw new Error(data.message || `运行失败 ${res.status}`);
  }
  return data;
}
