export type ProcessStageTone = "input" | "step" | "branch" | "output";

export interface ProcessStage {
  kicker: string;
  title: string;
  note?: string;
  tone?: ProcessStageTone;
}

/** 算法原理页的可视化类型。 */
export type PrincipleVizKind =
  | "pipeline"
  | "lawnmower"
  | "index_spectrum"
  | "red_edge"
  | "regression"
  | "lut"
  | "lut_process"
  | "process"
  | "feature_space"
  | "sam"
  | "cnn_arch"
  | "fewshot"
  | "ace"
  | "unmix"
  | "rx"
  | "change"
  | "majority"
  | "zonal"
  | "spectrum_smooth"
  | "pca"
  | "atmosphere"
  | "brdf"
  | "ortho"
  | "mosaic";

export interface BandMark {
  id: string;
  label: string;
  nm: number;
  color: string;
}

export interface ArchLayer {
  name: string;
  note: string;
}

export interface PrincipleViz {
  kind: PrincipleVizKind;
  caption: string;
  bands?: BandMark[];
  layers?: ArchLayer[];
  steps?: string[];
  stages?: ProcessStage[];
}

export interface IoRow {
  name: string;
  meaning: string;
}

export interface PrincipleSummary {
  /** 须对齐文献或标准原文，不得自行引申。 */
  definition: string;
  value: string;
  keyInput: string;
  keyOutput: string;
  keyLimit: string;
}

export interface ParameterNote {
  name: string;
  role: string;
  guidance: string;
  effect: string;
  risk: string;
}

export interface FormulaItem {
  name: string;
  eq: string;
  note: string;
}

export interface ScenarioCase {
  title: string;
  body: string;
}

export interface PrincipleDoc {
  id: string;
  purpose: string;
  why: string;
  formula: string;
  formulaNote?: string;
  /** 多公式捆成一项时，写在公式列表下方。 */
  formulaTogether?: string;
  /** 原理页高亮的一句话理解。 */
  formulaTakeaway?: string;
  formulaItems?: FormulaItem[];
  /** 画在核心公式下方的处理过程图，与页中「原理示意」分开。 */
  formulaProcess?: PrincipleViz;
  scenarioCases?: ScenarioCase[];
  steps: string[];
  viz: PrincipleViz;
  inputs: IoRow[];
  outputs: IoRow[];
  industryGap: string;
  checks: string[];
  summary: PrincipleSummary;
  background: string[];
  prerequisites: string[];
  parameterNotes: ParameterNote[];
  resultInterpretation: string[];
  applicable: string[];
  notApplicable: string[];
  risks: string[];
  upstream: string[];
  downstream: string[];
  demoFocus: string[];
}
