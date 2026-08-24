import type { FieldRow } from "./types";

/** 下拉选项：值 + 中文说明 */
export interface SelectOption {
  value: string;
  label: string;
}

const METHOD_BY_ALGO: Record<string, SelectOption[]> = {
  "22_normalize": [
    { value: "snv", label: "SNV 标准正态变量" },
    { value: "zscore", label: "Z-score" },
    { value: "minmax", label: "MinMax" },
    { value: "l2", label: "L2 归一化" },
  ],
  "23_pca": [
    { value: "mnf", label: "MNF" },
    { value: "pca", label: "PCA" },
  ],
  "35_spectral_matching": [
    { value: "sam", label: "SAM 光谱角" },
    { value: "sid", label: "SID 光谱信息散度" },
  ],
  "42_anomaly_detect": [
    { value: "lrx", label: "局部 RX" },
    { value: "rx", label: "全局 RX" },
  ],
};

const SELECT_BY_KEY: Record<string, SelectOption[]> = {
  model: [
    { value: "svm", label: "SVM 支持向量机" },
    { value: "rf", label: "随机森林" },
  ],
  kernel: [
    { value: "rbf", label: "RBF 径向基" },
    { value: "linear", label: "线性" },
  ],
  mode: [
    { value: "continuous", label: "连续（指数）" },
    { value: "categorical", label: "分类" },
  ],
  preprocess: [{ value: "snv", label: "SNV" }],
};

const KIND_ZH: Record<string, string> = {
  geotiff: "GeoTIFF 影像",
  geojson: "GeoJSON 矢量",
  csv: "CSV 表格",
  json: "JSON",
};

/** 文件字段中文名 */
export function fileFieldTitle(name: string): string {
  return name === "file2" ? "辅文件" : "主文件";
}

/** 文件类型中文 */
export function fileKindLabel(type: string): string {
  return KIND_ZH[type] || type || "文件";
}

/** 从 params.red_band 取出 red_band */
export function paramKey(fieldName: string): string {
  return fieldName.startsWith("params.") ? fieldName.slice("params.".length) : fieldName;
}

export function isFileField(field: FieldRow): boolean {
  return field.name === "file" || field.name === "file2";
}

export function isParamField(field: FieldRow): boolean {
  return field.name.startsWith("params.");
}

/** 参数控件类型 */
export function paramWidget(algoId: string, field: FieldRow): "select" | "number" | "bool" | "json" | "text" {
  const key = paramKey(field.name);
  if (selectOptions(algoId, key).length) return "select";
  if (field.type === "bool") return "bool";
  if (field.type === "int" || field.type === "float") return "number";
  if (field.type === "list" || field.type === "dict") return "json";
  return "text";
}

export function selectOptions(algoId: string, key: string): SelectOption[] {
  if (key === "method") return METHOD_BY_ALGO[algoId] || [];
  return SELECT_BY_KEY[key] || [];
}

/** 把 testdata 默认值写成表单字符串 */
export function stringifyParam(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

/** 按字段类型解析表单值；空字符串则跳过 */
export function parseFormParams(
  fields: FieldRow[],
  values: Record<string, string>,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const field of fields) {
    if (!isParamField(field)) continue;
    const key = paramKey(field.name);
    const raw = (values[key] ?? "").trim();
    if (raw === "") continue;
    const parsed = parseOne(field.type, raw);
    if (parsed === undefined) {
      throw new Error(`参数 ${key} 格式不正确，当前值：${raw}`);
    }
    out[key] = parsed;
  }
  return out;
}

function parseOne(type: string, raw: string): unknown {
  if (type === "int") {
    const n = Number.parseInt(raw, 10);
    return Number.isFinite(n) ? n : undefined;
  }
  if (type === "float") {
    const n = Number.parseFloat(raw);
    return Number.isFinite(n) ? n : undefined;
  }
  if (type === "bool") return raw === "true" || raw === "1";
  if (type === "list" || type === "dict") {
    try {
      return JSON.parse(raw);
    } catch {
      return undefined;
    }
  }
  return raw;
}

/** 文件选择器 accept */
export function fileAccept(type: string): string {
  if (type === "geotiff") return ".tif,.tiff,image/tiff";
  if (type === "geojson") return ".geojson,.json,application/geo+json";
  if (type === "csv") return ".csv,text/csv";
  if (type === "json") return ".json,application/json";
  return "";
}
