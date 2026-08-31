import type {
  OutputFieldRow,
  OutputQualityRule,
  OutputStatus,
  RunResult,
  TestdataHttp,
} from "./types";

/** 质量状态与界面文案分离，禁止把 unknown 写成“通过” */
export const OUTPUT_STATUS_LABEL: Record<OutputStatus, string> = {
  pass: "通过",
  attention: "需关注",
  unknown: "不可判定",
  "not-produced": "未产生",
};

/** 返回质量状态对应中文标签 */
export function statusLabel(status: OutputStatus): string {
  return OUTPUT_STATUS_LABEL[status];
}

/** 判断值是否视为“未产生/未绑定” */
function isMissingValue(value: unknown): boolean {
  return value === undefined || value === null;
}

/** 判断对象节点能否继续按字符串键下钻 */
function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

/**
 * 从 data 根对象按完整路径（如 data.scene.mean）安全读取嵌套值。
 * 遇到 null、数组、不存在键或非对象中间节点时返回 undefined。
 */
export function readDataPath(root: unknown, path: string): unknown {
  if (!path.startsWith("data.")) {
    return undefined;
  }
  const segments = path.slice("data.".length).split(".").filter(Boolean);
  if (segments.length === 0) {
    return root ?? undefined;
  }

  let current: unknown = root;
  for (const segment of segments) {
    if (!isRecord(current)) {
      return undefined;
    }
    if (!Object.prototype.hasOwnProperty.call(current, segment)) {
      return undefined;
    }
    current = current[segment];
  }
  return current;
}

/** 解析输出行的完整 data 路径 */
function dataPathOf(row: OutputFieldRow): string {
  return row.name.startsWith("data.") ? row.name : `data.${row.apiKey}`;
}

/** 从 RunResult 绑定 files 类输出，优先 files_http */
function resolveFileValue(row: OutputFieldRow, result: RunResult): unknown {
  const key = row.apiKey;
  const http = result.files_http;
  if (isRecord(http) && Object.prototype.hasOwnProperty.call(http, key)) {
    return http[key];
  }
  const files = result.files;
  if (isRecord(files) && Object.prototype.hasOwnProperty.call(files, key)) {
    return files[key];
  }
  return undefined;
}

/** 将输出知识行绑定到一次 RunResult 的实际值 */
export function resolveOutputValue(
  row: OutputFieldRow,
  result: RunResult | null | undefined,
): unknown {
  if (!result) {
    return undefined;
  }
  if (row.parent === "files") {
    return resolveFileValue(row, result);
  }
  if (row.parent === "data") {
    return readDataPath(result.data, dataPathOf(row));
  }
  return undefined;
}

/** 按结构化质量规则判定数值或等值条件 */
function evaluateQualityRule(
  rule: OutputQualityRule,
  value: unknown,
): OutputStatus {
  switch (rule.kind) {
    case "between": {
      if (rule.min === undefined || rule.max === undefined) {
        return "unknown";
      }
      const num = Number(value);
      if (Number.isNaN(num)) {
        return "unknown";
      }
      const inside = num >= rule.min && num <= rule.max;
      const pass = rule.passWhenInside !== false ? inside : !inside;
      return pass ? "pass" : "attention";
    }
    case "min": {
      if (rule.min === undefined) {
        return "unknown";
      }
      const num = Number(value);
      if (Number.isNaN(num)) {
        return "unknown";
      }
      return num >= rule.min ? "pass" : "attention";
    }
    case "max": {
      if (rule.max === undefined) {
        return "unknown";
      }
      const num = Number(value);
      if (Number.isNaN(num)) {
        return "unknown";
      }
      return num <= rule.max ? "pass" : "attention";
    }
    case "equals": {
      if (rule.value === undefined) {
        return "unknown";
      }
      return value === rule.value ? "pass" : "attention";
    }
    default:
      return "unknown";
  }
}

/**
 * 评估单条输出的质量状态。
 * 无 qualityRule 时绝不返回 pass；条件/可选输出缺失时返回 not-produced。
 */
export function evaluateOutputStatus(
  row: OutputFieldRow,
  value: unknown,
): OutputStatus {
  if (isMissingValue(value)) {
    if (row.conditional || row.optional) {
      return "not-produced";
    }
    return "unknown";
  }

  const rule = row.qualityRule;
  if (!rule) {
    return "unknown";
  }

  return evaluateQualityRule(rule, value);
}

/** 列出结果中未登记的文件键，供“说明待补充”展示 */
export function extraUnregisteredFileKeys(
  rows: OutputFieldRow[],
  result: RunResult | null | undefined,
): string[] {
  if (!result) return [];
  const known = new Set(
    rows.filter((row) => row.parent === "files").map((row) => row.apiKey),
  );
  const observed = new Set<string>([
    ...Object.keys(isRecord(result.files_http) ? result.files_http : {}),
    ...Object.keys(isRecord(result.files) ? result.files : {}),
  ]);
  return [...observed].filter((key) => !known.has(key)).sort();
}

/** 判断绑定值是否可作为可视化资源 */
export function asTestdataHttp(value: unknown): TestdataHttp | null {
  if (!isRecord(value)) return null;
  if (!("url" in value) || !("vis" in value) || typeof value.name !== "string") {
    return null;
  }
  const url = value.url;
  if (url !== null && typeof url !== "string") return null;
  if (typeof value.vis !== "string") return null;
  return value as unknown as TestdataHttp;
}

/** 算法服务原始信封字段；控制台预览字段不得混入 */
const ORIGINAL_API_KEYS = [
  "success",
  "algorithm_id",
  "algorithm",
  "implemented",
  "message",
  "data",
  "files",
] as const;

export type OriginalApiPayload = {
  success: boolean;
  algorithm_id: string | null;
  algorithm: string | null;
  implemented: boolean | null;
  message: string;
  data: Record<string, unknown>;
  files: Record<string, string>;
};

/** 从控制台运行结果中抽出算法服务原始 JSON 信封 */
export function originalApiPayload(
  result: RunResult | null | undefined,
): OriginalApiPayload | null {
  if (!result) return null;
  const extra = result as RunResult & Record<string, unknown>;
  const data = isRecord(result.data) ? result.data : {};
  const files = isRecord(result.files)
    ? (result.files as Record<string, string>)
    : {};
  void ORIGINAL_API_KEYS;
  return {
    success: result.success,
    algorithm_id: result.algorithm_id ?? null,
    algorithm: typeof extra.algorithm === "string" ? extra.algorithm : null,
    implemented: typeof extra.implemented === "boolean" ? extra.implemented : null,
    message: result.message ?? "",
    data,
    files,
  };
}

export type FlattenedApiField = {
  path: string;
  value: unknown;
};

const ENVELOPE_ORDER = [
  "success",
  "algorithm_id",
  "algorithm",
  "implemented",
  "message",
] as const;

/** 信封、data、files 按返回顺序逐项展开；对象下钻，数组保持原值 */
export function flattenApiFields(
  payload: OriginalApiPayload | null | undefined,
): FlattenedApiField[] {
  if (!payload) return [];
  const rows: FlattenedApiField[] = [];
  for (const key of ENVELOPE_ORDER) {
    rows.push({ path: key, value: payload[key] });
  }
  flattenRecord(rows, payload.data, "data");
  flattenRecord(rows, payload.files, "files");
  return rows;
}

function flattenRecord(
  rows: FlattenedApiField[],
  value: unknown,
  prefix: string,
): void {
  if (!isRecord(value) || Object.keys(value).length === 0) {
    rows.push({ path: prefix, value });
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    const path = `${prefix}.${key}`;
    if (isRecord(child) && Object.keys(child).length > 0) {
      flattenRecord(rows, child, path);
    } else {
      rows.push({ path, value: child });
    }
  }
}

/** 信封字段的固定说明，避免与知识库产物说明混淆 */
export const ENVELOPE_FIELD_HELP: Record<string, string> = {
  success: "算法服务是否按协议返回成功。true 表示本次调用完成，不代表专题图业务合格。",
  algorithm_id: "本次运行的算法标识，与请求路径中的算法 ID 一致。",
  algorithm: "算法中文名称，来自服务实现，不是控制台另写的标题。",
  implemented: "该算法是否已实现真实计算。false 时通常只返回骨架说明。",
  message: "服务对本次运行的一句话状态说明，属于接口原文。",
};

export const ENVELOPE_FIELD_LABEL: Record<string, string> = {
  success: "调用成功",
  algorithm_id: "算法标识",
  algorithm: "算法名称",
  implemented: "是否已实现",
  message: "服务说明",
};

export type FieldVisKind =
  | "boolean"
  | "number"
  | "text"
  | "array"
  | "file"
  | "empty"
  | "json";

export type FieldHelpSource = "envelope" | "knowledge" | "pending";

/** 按返回路径匹配知识库输出行 */
export function knowledgeRowForPath(
  rows: OutputFieldRow[],
  path: string,
): OutputFieldRow | undefined {
  return rows.find((row) => {
    if (row.name === path) return true;
    return `${row.parent}.${row.apiKey}` === path;
  });
}

/** 字段标题：优先知识库标签，其次信封固定名 */
export function fieldTitle(path: string, row: OutputFieldRow | undefined): string {
  if (row?.label) return row.label;
  if (ENVELOPE_FIELD_LABEL[path]) return ENVELOPE_FIELD_LABEL[path];
  return path.split(".").pop() || path;
}

/** 字段说明来源：信封固定文案、知识库或待补充 */
export function fieldHelp(
  path: string,
  row: OutputFieldRow | undefined,
): { source: FieldHelpSource; text: string } {
  if (ENVELOPE_FIELD_HELP[path]) {
    return { source: "envelope", text: ENVELOPE_FIELD_HELP[path] };
  }
  if (row?.description) {
    return { source: "knowledge", text: row.description };
  }
  return {
    source: "pending",
    text: "说明待补充。接口返回了该键，知识库尚未登记专业解读。",
  };
}

/** 接口原值的可读文本，布尔值保持 true/false */
export function displayFieldValue(value: unknown): string {
  if (value === undefined || value === null) return "—";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "—";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}

/** 按路径与值类型选择可视化形态 */
export function fieldVisKind(path: string, value: unknown): FieldVisKind {
  if (value === undefined || value === null) return "empty";
  if (path.startsWith("files.") && typeof value === "string") return "file";
  if (typeof value === "boolean") return "boolean";
  if (typeof value === "number" && Number.isFinite(value)) return "number";
  if (Array.isArray(value)) return "array";
  if (typeof value === "string") return "text";
  return "json";
}

/** 识别 [行, 列] 形态的 shape 数组 */
export function asShape(value: unknown): { rows: number; cols: number } | null {
  if (!Array.isArray(value) || value.length !== 2) return null;
  const [rows, cols] = value;
  if (typeof rows !== "number" || typeof cols !== "number") return null;
  if (!Number.isFinite(rows) || !Number.isFinite(cols) || rows <= 0 || cols <= 0) {
    return null;
  }
  return { rows, cols };
}

export type NumericDomain = {
  min: number;
  max: number;
  marker: number;
};

/** 数值轴：优先知识库定义域，其次同级 min/max */
export function numericDomain(
  path: string,
  value: number,
  row: OutputFieldRow | undefined,
  fields: FlattenedApiField[],
): NumericDomain | null {
  const rule = row?.qualityRule;
  if (
    rule?.kind === "between" &&
    rule.min !== undefined &&
    rule.max !== undefined &&
    rule.min !== rule.max
  ) {
    return { min: rule.min, max: rule.max, marker: value };
  }
  const parent = path.includes(".") ? path.slice(0, path.lastIndexOf(".")) : "";
  if (!parent) return null;
  const last = path.split(".").pop() || "";
  if (!/^(min|max|mean|median|std|stddev|p\d+)$/i.test(last)) {
    return null;
  }
  const minField = fields.find((item) => item.path === `${parent}.min`);
  const maxField = fields.find((item) => item.path === `${parent}.max`);
  if (
    typeof minField?.value === "number" &&
    typeof maxField?.value === "number" &&
    minField.value !== maxField.value
  ) {
    return { min: minField.value, max: maxField.value, marker: value };
  }
  return null;
}

/** 将标记值映射到 0–100，超出定义域时夹紧 */
export function domainPercent(domain: NumericDomain): number {
  const span = domain.max - domain.min;
  if (span === 0) return 50;
  const raw = ((domain.marker - domain.min) / span) * 100;
  return Math.min(100, Math.max(0, raw));
}
