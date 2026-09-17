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
const execFileAsync = promisify(execFile);
const esbuildBin = new URL("../node_modules/.bin/esbuild", import.meta.url).pathname;

async function bundleModule(entryUrl, outfile) {
  await execFileAsync(esbuildBin, [
    entryUrl.pathname,
    "--bundle",
    "--platform=node",
    "--format=esm",
    `--outfile=${outfile}`,
  ]);
  return import(`${pathToFileURL(outfile).href}?t=${Date.now()}`);
}

function flattenPanelText(view) {
  return JSON.stringify(view);
}

function allPanelClaims(view) {
  return [...view.claims, ...view.implementationClaims];
}

test("55 项均可通过 getAlgorithmEvidence 获取", async () => {
  const workdir = await mkdtemp(join(tmpdir(), "source-evidence-"));
  try {
    const frontend = await bundleModule(
      new URL("../src/evidence.ts", import.meta.url),
      join(workdir, "evidence.mjs"),
    );
    assert.equal(rows.length, 55);
    for (const row of rows) {
      const evidence = frontend.getAlgorithmEvidence(row.algorithmId);
      assert.ok(evidence, `${row.algorithmId}: getAlgorithmEvidence 未返回`);
      assert.equal(evidence.algorithmId, row.algorithmId);
      assert.equal(evidence.title, row.title);
      assert.equal(evidence.grade, row.grade);
    }
    assert.equal(frontend.getAlgorithmEvidence("not_registered"), undefined);
  } finally {
    await rm(workdir, { recursive: true, force: true });
  }
});

test("rejected 主张不得进入 SourcePanel，显示主张的 referenceIds 可解析", async () => {
  const workdir = await mkdtemp(join(tmpdir(), "source-panel-bind-"));
  try {
    const frontend = await bundleModule(
      new URL("../src/evidence.ts", import.meta.url),
      join(workdir, "evidence.mjs"),
    );
    assert.equal(typeof frontend.buildSourcePanelView, "function");

    const evidence = frontend.getAlgorithmEvidence("27_ndvi");
    evidence.claims.push({
      claimId: "rejected-claim",
      category: "definition",
      text: "伪造主张，不得展示",
      status: "rejected",
      targets: ["source-panel"],
      referenceIds: ["rejected-ref"],
      implementationRefs: ["/Users/secret/service.py"],
      reviewNote: "测试用拒绝项",
    });
    evidence.references.push({
      referenceId: "rejected-ref",
      authors: "Nobody",
      year: "1900",
      title: "Isolated Rejected Paper",
      venue: "None",
      url: "https://example.com/rejected",
      sourceType: "primary-paper",
      summary: "这条引用只支持被拒绝主张，不得出现在文献页。",
      supports: ["rejected-claim"],
    });

    const view = frontend.buildSourcePanelView(evidence, {
      method: "NDVI = (NIR − RED) / (NIR + RED)",
      diffs: ["分母加 1e-12，只防除零，不是 USGS 公式的一部分。"],
    });

    const panelText = flattenPanelText(view);
    assert.equal(view.claims.some((claim) => claim.claimId === "rejected-claim"), false);
    assert.equal(
      view.implementationClaims.some((claim) => claim.claimId === "rejected-claim"),
      false,
    );
    assert.equal(view.references.some((item) => item.referenceId === "rejected-ref"), false);
    assert.doesNotMatch(panelText, /伪造主张，不得展示/);
    assert.doesNotMatch(panelText, /Isolated Rejected Paper/);
    assert.doesNotMatch(panelText, /\/Users\//);
    assert.doesNotMatch(panelText, /service\.py/);

    const refs = new Map(view.references.map((item) => [item.referenceId, item]));
    for (const claim of allPanelClaims(view)) {
      for (const referenceId of claim.referenceIds) {
        const reference = refs.get(referenceId);
        assert.ok(reference, `27_ndvi: ${claim.claimId} 的 ${referenceId} 无法解析`);
        assert.ok(
          reference.supportedClaims.some((supported) => supported.claimId === claim.claimId),
          `27_ndvi: ${referenceId} 未标明支持 ${claim.claimId}`,
        );
        assert.ok(
          reference.supportedClaims.every((supported) => supported.title || supported.text),
          `27_ndvi: ${referenceId} 出现孤立引用`,
        );
      }
    }
    for (const reference of view.references) {
      assert.ok(reference.supportedClaims.length > 0, `${reference.referenceId}: 孤立引用`);
    }

    const definition = view.claims.find((claim) => claim.claimId === "definition");
    assert.ok(definition);
    assert.equal(definition.statusLabel, "已对照来源核验");
    assert.equal(definition.gradeLabel, "证据等级 A：原始论文、标准或官方资料直接支持核心方法");
    assert.ok(definition.sources.length > 0, "核验主张必须带上来源链接");
    assert.ok(definition.sources.every((source) => source.url.startsWith("https://")));
    assert.ok(
      definition.sources.some((source) =>
        source.url.includes("landsat-normalized-difference-vegetation-index"),
      ),
      "定义主张应能点开 USGS 官方 NDVI 页",
    );
    const formula = view.claims.find((claim) => claim.claimId === "formula");
    assert.ok(formula);
    assert.equal(formula.statusLabel, "已对照来源核验");
    const limitation = view.claims.find((claim) => claim.claimId === "limitation");
    assert.ok(limitation);
    assert.equal(limitation.statusLabel, "有条件成立");
    assert.equal(
      view.implementationClaims.some((claim) => claim.claimId === "input"),
      false,
    );
    assert.equal(
      view.implementationClaims.some((claim) => claim.claimId === "output"),
      false,
    );
    assert.equal(
      view.claims.some((claim) => claim.claimId === "input"),
      false,
    );
    assert.equal(view.method, "NDVI = (NIR − RED) / (NIR + RED)");
    assert.equal(view.implementationDiffs.length, 1);
    assert.match(view.implementationDiffs.join(" "), /1e-12/);
    assert.match(view.implementationDiffs.join(" "), /防除零/);
    assert.doesNotMatch(view.implementationDiffs.join(" "), /默认波段 2\/3/);
    assert.doesNotMatch(view.implementationDiffs.join(" "), /GeoTIFF/);
  } finally {
    await rm(workdir, { recursive: true, force: true });
  }
});

test("getSourcePanelView 覆盖 55 项，引用闭合且不含实现路径", async () => {
  const workdir = await mkdtemp(join(tmpdir(), "source-panel-view-"));
  try {
    const frontend = await bundleModule(
      new URL("../src/sources.ts", import.meta.url),
      join(workdir, "sources.mjs"),
    );
    assert.equal(typeof frontend.getSourcePanelView, "function");
    assert.equal(frontend.getSourcePanelView("not_registered"), undefined);

    const ndvi = frontend.getSourcePanelView("27_ndvi");
    assert.ok(ndvi);
    assert.equal(ndvi.method, "NDVI = (NIR − RED) / (NIR + RED)");
    assert.ok(ndvi.claims.length > 0);
    assert.ok(ndvi.references.length > 0);
    assert.ok(Array.isArray(ndvi.implementationDiffs));
    assert.ok(ndvi.implementationDiffs.length > 0);
    assert.match(ndvi.implementationDiffs.join(" "), /1e-12/);
    assert.doesNotMatch(ndvi.implementationDiffs.join(" "), /默认波段 2\/3/);
    assert.equal(
      ndvi.implementationClaims.some((claim) => ["input", "output"].includes(claim.claimId)),
      false,
    );

    const ndre = frontend.getSourcePanelView("28_ndre");
    assert.ok(ndre);
    assert.equal(ndre.gradeLabel, "证据等级 C：证据有限，须标明工程实现或边界");
    assert.ok(ndre.claims.some((claim) => claim.statusLabel === "有条件成立"));

    for (const row of rows) {
      const view = frontend.getSourcePanelView(row.algorithmId);
      assert.ok(view, `${row.algorithmId}: SourcePanel 无绑定数据`);
      const panelText = flattenPanelText(view);
      assert.doesNotMatch(panelText, /\/Users\//);
      assert.doesNotMatch(panelText, /[A-Za-z]:\\/);
      assert.doesNotMatch(panelText, /service\.py/);
      assert.doesNotMatch(panelText, /implementationRefs/);
      assert.ok(Array.isArray(view.implementationDiffs), `${row.algorithmId}: 实现差异必须是列表`);
      assert.ok(
        view.implementationDiffs.every((item) => typeof item === "string" && item.trim().length > 0),
        `${row.algorithmId}: 实现差异条目不能为空`,
      );
      const diffText = view.implementationDiffs.join(" ");
      assert.doesNotMatch(diffText, /GeoTIFF/);
      assert.doesNotMatch(diffText, /默认波段 2\/3/);

      const statusById = new Map(row.claims.map((claim) => [claim.claimId, claim.status]));
      const sourcePanelClaimIds = new Set(
        row.claims
          .filter(
            (claim) =>
              claim.targets.includes("source-panel") &&
              claim.status !== "rejected" &&
              claim.claimId !== "input" &&
              claim.claimId !== "output",
          )
          .map((claim) => claim.claimId),
      );
      assert.equal(
        view.implementationClaims.some((claim) => ["input", "output"].includes(claim.claimId)),
        false,
        `${row.algorithmId}: 实现差异混入了接口输入输出`,
      );
      const shownIds = new Set(allPanelClaims(view).map((claim) => claim.claimId));
      assert.deepEqual(shownIds, sourcePanelClaimIds, `${row.algorithmId}: 文献页主张集合不一致`);

      for (const claim of view.claims) {
        assert.notEqual(
          statusById.get(claim.claimId),
          "implementation-only",
          `${row.algorithmId}: claims 混入 implementation-only ${claim.claimId}`,
        );
      }
      for (const claim of view.implementationClaims) {
        assert.equal(
          statusById.get(claim.claimId),
          "implementation-only",
          `${row.algorithmId}: implementationClaims 混入非实现主张 ${claim.claimId}`,
        );
        assert.equal(claim.statusLabel, "本仓库实现依据");
        assert.doesNotMatch(claim.gradeLabel ?? "", /证据等级 [ABC]/);
        assert.doesNotMatch(claim.statusLabel, /文献证明/);
      }

      const refs = new Map(view.references.map((item) => [item.referenceId, item]));
      for (const claim of allPanelClaims(view)) {
        assert.ok(claim.statusLabel);
        if (statusById.get(claim.claimId) !== "implementation-only") {
          assert.ok(claim.gradeLabel.startsWith("证据等级 "));
          assert.doesNotMatch(claim.gradeLabel, /正确率/);
        }
        for (const referenceId of claim.referenceIds) {
          const reference = refs.get(referenceId);
          assert.ok(reference, `${row.algorithmId}: ${claim.claimId} 的 ${referenceId} 无法解析`);
          assert.ok(
            reference.supportedClaims.some((supported) => supported.claimId === claim.claimId),
          );
        }
        if (statusById.get(claim.claimId) !== "implementation-only") {
          assert.equal(
            claim.sources.length,
            claim.referenceIds.length,
            `${row.algorithmId}: ${claim.claimId} 核验来源未挂到主张上`,
          );
          for (const source of claim.sources) {
            assert.match(source.url, /^https:\/\//);
            assert.ok(source.title);
            assert.ok(source.authors);
          }
        }
      }
      for (const reference of view.references) {
        assert.ok(reference.supportedClaims.length > 0, `${row.algorithmId}: ${reference.referenceId} 孤立引用`);
        for (const supported of reference.supportedClaims) {
          assert.ok(shownIds.has(supported.claimId));
          assert.ok(supported.title.length > 0 || supported.text.length > 0);
        }
      }
    }
  } finally {
    await rm(workdir, { recursive: true, force: true });
  }
});
