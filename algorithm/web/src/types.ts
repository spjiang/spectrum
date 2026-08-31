export type VisKind =
  | "raster_falsecolor"
  | "raster_index"
  | "raster_class"
  | "geojson_map"
  | "csv_track"
  | "csv_spectrum"
  | "csv_table"
  | "json_table"
  | "png"
  | "none";

export interface FieldRow {
  name: string;
  label?: string;
  type: string;
  required?: boolean;
  format?: string;
  description: string;
  unit?: string;
  default?: unknown;
  defaultReason?: string;
  range?: string;
  selectionGuide?: string;
  effect?: string;
  risk?: string;
  example?: string;
  qualityCheck?: string;
  downstreamUse?: string;
  vis: VisKind;
}

/** 输出产物顶部决策摘要 */
export interface OutputSummary {
  what: string;
  value: string;
  caution: string;
}

/** 多波段文件中的单波段说明 */
export interface OutputBand {
  index?: number;
  label?: string;
  name?: string;
  unit?: string;
  range?: string;
  meaning?: string;
  description?: string;
}

/** 可机器判定的质量规则 */
export interface OutputQualityRule {
  kind: "between" | "min" | "max" | "equals";
  min?: number;
  max?: number;
  value?: string | number | boolean;
  passWhenInside?: boolean;
  basis: string;
}

/** 输出知识行：文件产物或核心 data 指标 */
export interface OutputFieldRow extends FieldRow {
  apiKey: string;
  parent: "files" | "data";
  label: string;
  effect: string;
  businessMeaning: string;
  interpretation: string;
  abnormalSigns: string[];
  optional?: boolean;
  conditional?: string;
  bands?: OutputBand[];
  misuseWarning?: string;
  relatedOutputs?: string[];
  qualityRule?: OutputQualityRule;
  knowledgeSource?: "algorithm" | "fallback";
}

/** 质量状态枚举：与 UI 文案分离，供组件映射展示 */
export type OutputStatus = "pass" | "attention" | "unknown" | "not-produced";

export interface TestdataHttp {
  url: string | null;
  vis: VisKind;
  name: string;
  job?: string;
  error?: string;
}

export interface AlgorithmCard {
  id: string;
  title: string;
  level: string;
  group: string;
  implemented: boolean;
  purpose: string;
  scenario: string;
  method: string;
  endpoint: string;
  console_run: string;
  compare: "before_after" | "cube_to_product" | "single";
  testdata: {
    file: string | null;
    file2: string | null;
    params: Record<string, unknown>;
    exists: boolean;
  };
  testdata_http?: {
    file: TestdataHttp | null;
    file2: TestdataHttp | null;
  };
  output_summary: OutputSummary;
  fields: {
    inputs: FieldRow[];
    outputs: OutputFieldRow[];
  };
}

export interface RunResult {
  success: boolean;
  algorithm_id?: string;
  algorithm?: string;
  implemented?: boolean;
  message?: string;
  data?: Record<string, unknown>;
  files?: Record<string, string>;
  files_http?: Record<string, TestdataHttp>;
  job_id?: string | null;
}

export interface RasterMeta {
  height: number;
  width: number;
  bands: number;
  name?: string;
}

export interface SpectrumPoint {
  wavelengths_nm: number[];
  values: number[];
  row: number;
  col: number;
}
