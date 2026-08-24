/** 算法原理页的可视化类型（按「怎么学更直观」选型）。 */
export type PrincipleVizKind =
  | "pipeline"
  | "lawnmower"
  | "index_spectrum"
  | "red_edge"
  | "regression"
  | "lut"
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
}

export interface IoRow {
  name: string;
  meaning: string;
}

export interface PrincipleSummary {
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

export interface PrincipleDoc {
  id: string;
  purpose: string;
  why: string;
  formula: string;
  formulaNote?: string;
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
