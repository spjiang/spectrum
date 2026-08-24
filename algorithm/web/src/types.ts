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
  fields: {
    inputs: FieldRow[];
    outputs: FieldRow[];
  };
}

export interface RunResult {
  success: boolean;
  algorithm_id?: string;
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
