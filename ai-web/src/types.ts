/** L3 参谋接口合同，与后端 JSON 对齐。 */

export interface AideQuestion {
  title: string;
  crop: string;
  canopy: string;
  sensor: string;
  task: string;
  hook: string;
}

export interface AidePlanItem {
  algorithmId: string;
  title: string;
  role?: string;
  reason: string;
}

export interface AidePlan {
  primary: AidePlanItem;
  contrast: AidePlanItem;
  skipped: AidePlanItem[];
}

export interface AideQuality {
  status: "pass" | "warn" | "unknown" | string;
  label: string;
  detail: string;
}

export interface AideResult {
  algorithmId: string;
  success: boolean;
  message: string;
  stats: { min: number; max: number; mean: number } | null;
  previewUrl: string | null;
  quality: AideQuality;
}

export interface AideAdvice {
  headline: string;
  bullets: string[];
  isPrescription: boolean;
}

export interface AideLlm {
  used: boolean;
  fallback: boolean;
  reason: string;
}

export interface AideResponse {
  success: boolean;
  scenarioId: string;
  question: AideQuestion;
  plan: AidePlan;
  results: AideResult[];
  advice: AideAdvice;
  llm: AideLlm;
  message?: string;
}
