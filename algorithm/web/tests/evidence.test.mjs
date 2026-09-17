import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { promisify } from "node:util";
import { pathToFileURL } from "node:url";

const evidenceUrl = new URL("../../shared/scientific_evidence.json", import.meta.url);
const rows = JSON.parse(await readFile(evidenceUrl, "utf8"));
const requiredTargets = new Set([
  "principle",
  "source-panel",
  "console-output",
  "ai-knowledge",
  "product-analysis",
  "docs-api-checklist",
  "docs-algorithm-inventory",
]);
const claimKeys = [
  "category",
  "claimId",
  "implementationRefs",
  "referenceIds",
  "reviewNote",
  "status",
  "targets",
  "text",
].sort();
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
].sort();

test("共享证据覆盖 55 项并保持引用闭合", () => {
  assert.equal(rows.length, 55);
  assert.equal(new Set(rows.map((row) => row.algorithmId)).size, 55);
  assert.ok(
    rows.reduce((total, row) => total + row.references.length, 0) >= 74,
  );

  for (const row of rows) {
    assert.deepEqual(
      Object.keys(row).sort(),
      ["algorithmId", "claims", "grade", "implementation", "references", "title"].sort(),
    );
    assert.match(row.implementation, /^algorithm\/source\/algorithms\/[^/]+\/service\.py$/);
    assert.ok(row.claims.length > 0);
    assert.ok(row.references.length > 0, `${row.algorithmId}: 未迁移任何引用`);

    const refs = new Map(row.references.map((ref) => [ref.referenceId, ref]));
    assert.equal(refs.size, row.references.length, `${row.algorithmId}: 引用 ID 重复`);
    const claims = new Map(row.claims.map((claim) => [claim.claimId, claim]));
    assert.equal(claims.size, row.claims.length, `${row.algorithmId}: claim ID 重复`);

    for (const claim of row.claims) {
      assert.deepEqual(Object.keys(claim).sort(), claimKeys);
      assert.ok(["definition", "formula", "input", "output", "limitation"].includes(claim.category));
      assert.ok(["verified", "qualified", "implementation-only"].includes(claim.status));
      assert.ok(claim.claimId.length > 0 && claim.text.length > 0 && claim.reviewNote.length > 0);
      assert.ok(claim.targets.length > 0 && claim.implementationRefs.length > 0);
      assert.ok(claim.targets.every((target) => requiredTargets.has(target)));
      for (const referenceId of claim.referenceIds) {
        assert.ok(refs.has(referenceId), `${row.algorithmId}: ${referenceId} 不存在`);
        assert.ok(
          refs.get(referenceId).supports.includes(claim.claimId),
          `${row.algorithmId}: ${referenceId} 未反向支持 ${claim.claimId}`,
        );
      }
    }
    assert.deepEqual(
      new Set(row.claims.flatMap((claim) => claim.targets)),
      requiredTargets,
      `${row.algorithmId}: 审查目标不完整`,
    );
    for (const ref of row.references) {
      assert.deepEqual(Object.keys(ref).sort(), referenceKeys);
      assert.ok(
        [
          "primary-paper",
          "official-documentation",
          "academic-material",
          "secondary-index",
        ].includes(ref.sourceType),
      );
      assert.ok(ref.supports.length > 0);
      for (const claimId of ref.supports) {
        assert.ok(claims.has(claimId), `${row.algorithmId}: ${claimId} 不存在`);
        assert.ok(claims.get(claimId).referenceIds.includes(ref.referenceId));
      }
    }
  }
});

test("文献 URL 与中文提要满足发布门禁", () => {
  for (const row of rows) {
    for (const ref of row.references) {
      assert.ok(ref.url.startsWith("https://"), `${ref.referenceId}: URL 非 HTTPS`);
      assert.ok(ref.summary.length >= 20, `${ref.referenceId}: 中文提要过短`);
      assert.match(ref.summary, /[\u3400-\u9fff]/, `${ref.referenceId}: 提要不是中文`);
    }
  }
});

test("前端运行时校验且查询返回不可污染的共享 JSON 克隆", async () => {
  const workdir = await mkdtemp(join(tmpdir(), "evidence-test-"));
  const outfile = join(workdir, "evidence.mjs");
  try {
    await promisify(execFile)(
      new URL("../node_modules/.bin/esbuild", import.meta.url).pathname,
      [
        new URL("../src/evidence.ts", import.meta.url).pathname,
        "--bundle",
        "--platform=node",
        "--format=esm",
        `--outfile=${outfile}`,
      ],
    );
    const frontend = await import(`${pathToFileURL(outfile).href}?t=${Date.now()}`);
    const expected = rows.find((row) => row.algorithmId === "27_ndvi");
    const first = frontend.getAlgorithmEvidence("27_ndvi");
    assert.deepEqual(first, expected);
    assert.equal(frontend.getAlgorithmEvidence("not_registered"), undefined);

    first.claims[0].text = "polluted";
    assert.deepEqual(frontend.getAlgorithmEvidence("27_ndvi"), expected);

    const invalidStatus = structuredClone(rows);
    invalidStatus[0].claims[0].status = "typo";
    assert.throws(() => frontend.validateEvidenceData(invalidStatus), /status/);

    const missingField = structuredClone(rows);
    delete missingField[0].references[0].authors;
    assert.throws(() => frontend.validateEvidenceData(missingField), /reference/);

    const invalidSourceType = structuredClone(rows);
    invalidSourceType[0].references[0].sourceType = "blog";
    assert.throws(() => frontend.validateEvidenceData(invalidSourceType), /sourceType/);
  } finally {
    await rm(workdir, { recursive: true, force: true });
  }
});
