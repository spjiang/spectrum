import evidenceData from "../../shared/scientific_evidence.json";
import type { SourcePanelClaimItem, SourcePanelView } from "./types";

export type EvidenceGrade = "A" | "B" | "C";
export type ClaimStatus =
  | "verified"
  | "qualified"
  | "implementation-only";
export type ClaimCategory =
  | "definition"
  | "formula"
  | "input"
  | "output"
  | "limitation";
export type EvidenceSourceType =
  | "primary-paper"
  | "official-documentation"
  | "academic-material"
  | "secondary-index";
export type EvidenceTarget =
  | "principle"
  | "source-panel"
  | "console-output"
  | "ai-knowledge"
  | "product-analysis"
  | "docs-api-checklist"
  | "docs-algorithm-inventory";

export interface EvidenceClaim {
  claimId: string;
  category: ClaimCategory;
  text: string;
  status: ClaimStatus;
  targets: EvidenceTarget[];
  referenceIds: string[];
  implementationRefs: string[];
  reviewNote: string;
}

export interface EvidenceReference {
  referenceId: string;
  authors: string;
  year: string;
  title: string;
  venue: string;
  url: string;
  sourceType: EvidenceSourceType;
  summary: string;
  supports: string[];
}

export interface AlgorithmEvidence {
  algorithmId: string;
  title: string;
  grade: EvidenceGrade;
  implementation: string;
  claims: EvidenceClaim[];
  references: EvidenceReference[];
}

const topLevelKeys = [
  "algorithmId",
  "claims",
  "grade",
  "implementation",
  "references",
  "title",
];
const claimKeys = [
  "category",
  "claimId",
  "implementationRefs",
  "referenceIds",
  "reviewNote",
  "status",
  "targets",
  "text",
];
const referenceKeys = [
  "authors",
  "referenceId",
  "sourceType",
  "summary",
  "supports",
  "title",
  "url",
  "venue",
  "year",
];
const requiredTargets = new Set<EvidenceTarget>([
  "principle",
  "source-panel",
  "console-output",
  "ai-knowledge",
  "product-analysis",
  "docs-api-checklist",
  "docs-algorithm-inventory",
]);

function parseTarget(value: unknown, field: string): EvidenceTarget {
  const target = requireString(value, field);
  switch (target) {
    case "principle":
    case "source-panel":
    case "console-output":
    case "ai-knowledge":
    case "product-analysis":
    case "docs-api-checklist":
    case "docs-algorithm-inventory":
      return target;
    default:
      throw new TypeError(`${field} 非法`);
  }
}

function requireRecord(value: unknown, field: string): asserts value is Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError(`${field} 必须是对象`);
  }
}

function requireExactKeys(
  value: Record<string, unknown>,
  expected: string[],
  field: string,
): void {
  const actual = Object.keys(value).sort();
  if (actual.length !== expected.length || actual.some((key, index) => key !== expected[index])) {
    throw new TypeError(`${field} 字段不完整`);
  }
}

function requireString(value: unknown, field: string): string {
  if (typeof value !== "string" || value.trim() === "") {
    throw new TypeError(`${field} 必须是非空字符串`);
  }
  return value;
}

function requireStringList(
  value: unknown,
  field: string,
  allowEmpty = false,
): string[] {
  if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) {
    throw new TypeError(`${field} 必须是${allowEmpty ? "" : "非空"}数组`);
  }
  return value.map((item, index) => requireString(item, `${field}[${index}]`));
}

function parseClaim(value: unknown, field: string): EvidenceClaim {
  requireRecord(value, field);
  requireExactKeys(value, claimKeys, field);
  const category = requireString(value.category, `${field}.category`);
  if (
    category !== "definition"
    && category !== "formula"
    && category !== "input"
    && category !== "output"
    && category !== "limitation"
  ) {
    throw new TypeError(`${field}.category 非法`);
  }
  const status = requireString(value.status, `${field}.status`);
  if (status !== "verified" && status !== "qualified" && status !== "implementation-only") {
    throw new TypeError(`${field}.status 非法`);
  }
  if (!Array.isArray(value.targets) || value.targets.length === 0) {
    throw new TypeError(`${field}.targets 必须是非空数组`);
  }
  const targets = value.targets.map((target, index) =>
    parseTarget(target, `${field}.targets[${index}]`),
  );
  return {
    claimId: requireString(value.claimId, `${field}.claimId`),
    category,
    text: requireString(value.text, `${field}.text`),
    status,
    targets,
    referenceIds: requireStringList(value.referenceIds, `${field}.referenceIds`, true),
    implementationRefs: requireStringList(value.implementationRefs, `${field}.implementationRefs`),
    reviewNote: requireString(value.reviewNote, `${field}.reviewNote`),
  };
}

function parseReference(value: unknown, field: string): EvidenceReference {
  requireRecord(value, field);
  requireExactKeys(value, referenceKeys, field);
  const sourceType = requireString(value.sourceType, `${field}.sourceType`);
  if (
    sourceType !== "primary-paper"
    && sourceType !== "official-documentation"
    && sourceType !== "academic-material"
    && sourceType !== "secondary-index"
  ) {
    throw new TypeError(`${field}.sourceType 非法`);
  }
  const url = requireString(value.url, `${field}.url`);
  if (!url.startsWith("https://")) {
    throw new TypeError(`${field}.url 必须使用 HTTPS`);
  }
  const summary = requireString(value.summary, `${field}.summary`);
  if (summary.length < 20 || !/[\u3400-\u9fff]/u.test(summary)) {
    throw new TypeError(`${field}.summary 必须是至少 20 字的中文提要`);
  }
  return {
    referenceId: requireString(value.referenceId, `${field}.referenceId`),
    authors: requireString(value.authors, `${field}.authors`),
    year: requireString(value.year, `${field}.year`),
    title: requireString(value.title, `${field}.title`),
    venue: requireString(value.venue, `${field}.venue`),
    url,
    sourceType,
    summary,
    supports: requireStringList(value.supports, `${field}.supports`),
  };
}

export function validateEvidenceData(value: unknown): AlgorithmEvidence[] {
  if (!Array.isArray(value) || value.length === 0) {
    throw new TypeError("scientific evidence 顶层必须是非空数组");
  }
  const algorithmIds = new Set<string>();
  return value.map((item, rowIndex) => {
    const field = `rows[${rowIndex}]`;
    requireRecord(item, field);
    requireExactKeys(item, topLevelKeys, field);
    const algorithmId = requireString(item.algorithmId, `${field}.algorithmId`);
    if (algorithmIds.has(algorithmId)) {
      throw new TypeError(`${field}.algorithmId 重复`);
    }
    algorithmIds.add(algorithmId);
    const grade = requireString(item.grade, `${field}.grade`);
    if (grade !== "A" && grade !== "B" && grade !== "C") {
      throw new TypeError(`${field}.grade 非法`);
    }
    if (!Array.isArray(item.claims) || item.claims.length === 0) {
      throw new TypeError(`${field}.claims 必须是非空数组`);
    }
    if (!Array.isArray(item.references) || item.references.length === 0) {
      throw new TypeError(`${field}.references 必须是非空数组`);
    }
    const claims = item.claims.map((claim, index) => parseClaim(claim, `${field}.claims[${index}]`));
    const references = item.references.map(
      (reference, index) => parseReference(reference, `${field}.references[${index}]`),
    );
    const claimMap = new Map(claims.map((claim) => [claim.claimId, claim]));
    const referenceMap = new Map(references.map((reference) => [reference.referenceId, reference]));
    if (claimMap.size !== claims.length || referenceMap.size !== references.length) {
      throw new TypeError(`${field} claim/reference ID 重复`);
    }
    const coveredTargets = new Set(claims.flatMap((claim) => claim.targets));
    if (
      coveredTargets.size !== requiredTargets.size
      || [...requiredTargets].some((target) => !coveredTargets.has(target))
    ) {
      throw new TypeError(`${field}.claims 审查 targets 不完整`);
    }
    for (const claim of claims) {
      for (const referenceId of claim.referenceIds) {
        const reference = referenceMap.get(referenceId);
        if (!reference || !reference.supports.includes(claim.claimId)) {
          throw new TypeError(`${field} claim/reference 未双向闭合`);
        }
      }
    }
    for (const reference of references) {
      for (const claimId of reference.supports) {
        const claim = claimMap.get(claimId);
        if (!claim || !claim.referenceIds.includes(reference.referenceId)) {
          throw new TypeError(`${field} reference/claim 未双向闭合`);
        }
      }
    }
    return {
      algorithmId,
      title: requireString(item.title, `${field}.title`),
      grade,
      implementation: requireString(item.implementation, `${field}.implementation`),
      claims,
      references,
    };
  });
}

const evidenceRows = validateEvidenceData(evidenceData);

export function getAlgorithmEvidence(id: string): AlgorithmEvidence | undefined {
  const row = evidenceRows.find((item) => item.algorithmId === id);
  return row === undefined ? undefined : structuredClone(row);
}

export function evidenceGradeLabel(grade: EvidenceGrade): string {
  switch (grade) {
    case "A":
      return "证据等级 A：原始论文、标准或官方资料直接支持核心方法";
    case "B":
      return "证据等级 B：权威来源支持方法族，本仓库实现有简化";
    case "C":
      return "证据等级 C：证据有限，须标明工程实现或边界";
  }
}

export function claimStatusLabel(status: string): string {
  if (status === "implementation-only") {
    return "本仓库实现依据";
  }
  if (status === "qualified") {
    return "有条件成立";
  }
  if (status === "verified") {
    return "已对照来源核验";
  }
  return "状态未登记";
}

export function claimCategoryTitle(category: ClaimCategory): string {
  switch (category) {
    case "definition":
      return "定义";
    case "formula":
      return "公式";
    case "input":
      return "输入";
    case "output":
      return "输出";
    case "limitation":
      return "限制";
  }
}

function isRejectedStatus(status: string): boolean {
  return status === "rejected";
}

function isInterfaceContractClaim(claim: { claimId: string }): boolean {
  return claim.claimId === "input" || claim.claimId === "output";
}

function toClaimItem(
  claim: EvidenceClaim,
  gradeLabel: string,
  references: EvidenceReference[],
): SourcePanelClaimItem {
  const byId = new Map(references.map((item) => [item.referenceId, item]));
  const sources = claim.referenceIds.flatMap((referenceId) => {
    const item = byId.get(referenceId);
    if (item === undefined) {
      return [];
    }
    return [
      {
        referenceId: item.referenceId,
        authors: item.authors,
        year: item.year,
        title: item.title,
        url: item.url,
      },
    ];
  });
  return {
    claimId: claim.claimId,
    title: claimCategoryTitle(claim.category),
    text: claim.text,
    statusLabel: claimStatusLabel(claim.status),
    gradeLabel: claim.status === "implementation-only" ? "" : gradeLabel,
    referenceIds: [...claim.referenceIds],
    sources,
  };
}

export function buildSourcePanelView(
  evidence: AlgorithmEvidence,
  source?: { method?: string; diffs?: string[] } | null,
): SourcePanelView {
  const gradeLabel = evidenceGradeLabel(evidence.grade);
  const visibleClaims = evidence.claims.filter(
    (claim) =>
      claim.targets.includes("source-panel") &&
      !isRejectedStatus(claim.status) &&
      !isInterfaceContractClaim(claim),
  );
  const claims = visibleClaims
    .filter((claim) => claim.status !== "implementation-only")
    .map((claim) => toClaimItem(claim, gradeLabel, evidence.references));
  const implementationClaims = visibleClaims
    .filter((claim) => claim.status === "implementation-only")
    .map((claim) => toClaimItem(claim, gradeLabel, evidence.references));
  const shown = new Map(
    [...claims, ...implementationClaims].map((claim) => [claim.claimId, claim]),
  );
  const references = evidence.references.flatMap((reference) => {
    const supportedClaims = reference.supports.flatMap((claimId) => {
      const claim = shown.get(claimId);
      return claim === undefined
        ? []
        : [{ claimId: claim.claimId, title: claim.title, text: claim.text }];
    });
    if (supportedClaims.length === 0) {
      return [];
    }
    return [{
      referenceId: reference.referenceId,
      authors: reference.authors,
      year: reference.year,
      title: reference.title,
      venue: reference.venue,
      url: reference.url,
      summary: reference.summary,
      supportedClaims,
    }];
  });
  return {
    method: source?.method ?? "",
    gradeLabel,
    claims,
    references,
    implementationClaims,
    implementationDiffs: [...(source?.diffs ?? [])],
  };
}
