/** 按处理层的 AI 赋能案例，与 /api/v1/l3-aide/layers 对齐。 */

export interface AideLlm {
  used: boolean;
  fallback: boolean;
  reason: string;
  detail?: string;
  model?: string | null;
  baseUrl?: string | null;
}

export interface LayerTraditional {
  headline: string;
  bullets: string[];
}

export interface LayerAi {
  headline: string;
  markdown: string;
}

export interface LayerSummary {
  id: string;
  level: string;
  title: string;
  kicker: string;
  benefit: string;
}

export interface LayerCase {
  id: string;
  level: string;
  title: string;
  kicker: string;
  question: string;
  hook: string;
  context?: string[];
  story?: { title: string; text: string }[];
  jobs?: { who: string; does: string }[];
  llmIo?: {
    inputTitle: string;
    input: string[];
    outputTitle: string;
    output: string;
    ifNoKey: string;
  };
  resultNotes?: Record<string, string>;
  benefit?: string;
  demoAlgorithmId?: string;
  scenarioId?: string;
  traditional: LayerTraditional;
  ai: LayerAi;
  mustNot: string[];
}

export interface LayerDemo {
  algorithmId: string;
  success: boolean;
  message: string;
  stats: { min: number; max: number; mean: number } | null;
  previewUrl: string | null;
  data?: Record<string, unknown>;
}

export interface LayerPlanItem {
  algorithmId: string;
  title: string;
  reason: string;
}

export interface LayerQuality {
  status: string;
  label: string;
  detail: string;
}

export interface LayerResult {
  algorithmId: string;
  success: boolean;
  message: string;
  stats: { min: number; max: number; mean: number } | null;
  previewUrl: string | null;
  quality: LayerQuality;
}

export interface LayerRun {
  success: boolean;
  layerId: string;
  level: string;
  title: string;
  question: string;
  hook: string;
  traditional: LayerTraditional;
  ai: LayerAi;
  templateAi?: LayerAi;
  mustNot: string[];
  demo: LayerDemo | null;
  plan?: { primary: LayerPlanItem; contrast: LayerPlanItem; skipped: LayerPlanItem[] } | null;
  results?: LayerResult[] | null;
  prompt?: { system: string; user: string };
  llm: AideLlm;
  message?: string;
}
