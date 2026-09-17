import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  readDataPath,
  resolveOutputValue,
  evaluateOutputStatus,
  extraUnregisteredFileKeys,
  fieldHelp,
  fieldTitle,
  flattenApiFields,
  groupApiFields,
  isInlineApiValue,
  knowledgeRowForPath,
  numericDomain,
  originalApiPayload,
  statusExplain,
  statusLabel,
} from "../.tmp-output-test/outputWorkbench.js";

/** 构造最小文件输出行 */
function fileRow(overrides = {}) {
  return {
    name: "files.ndvi_tif",
    parent: "files",
    apiKey: "ndvi_tif",
    label: "NDVI GeoTIFF",
    type: "file",
    description: "NDVI 栅格",
    vis: "raster_index",
    effect: "植被指数空间分布",
    businessMeaning: "反映植被覆盖与长势",
    interpretation: "按像元读取 NDVI",
    qualityCheck: "检查 NoData 比例",
    abnormalSigns: ["全 NaN"],
    downstreamUse: "时序分析",
    ...overrides,
  };
}

/** 构造最小 data 指标行 */
function dataRow(overrides = {}) {
  return {
    name: "data.mean",
    parent: "data",
    apiKey: "mean",
    label: "均值",
    type: "value",
    description: "场景 NDVI 均值",
    vis: "none",
    effect: "单一汇总数值",
    businessMeaning: "场景级植被状况",
    interpretation: "读取 data.mean",
    qualityCheck: "对照理论域",
    abnormalSigns: ["超出 [-1,1]"],
    downstreamUse: "报表汇总",
    ...overrides,
  };
}

const ndviRule = {
  kind: "between",
  min: -1,
  max: 1,
  passWhenInside: true,
  basis: "NDVI 理论定义域",
};

describe("resolveOutputValue", () => {
  it("files.ndvi_tif 从 result.files_http.ndvi_tif 绑定", () => {
    const httpEntry = {
      url: "http://example/ndvi.tif",
      vis: "raster_index",
      name: "ndvi_tif",
    };
    const value = resolveOutputValue(fileRow(), {
      success: true,
      files_http: { ndvi_tif: httpEntry },
    });
    assert.deepEqual(value, httpEntry);
  });

  it("data.mean 从 result.data.mean 绑定", () => {
    const value = resolveOutputValue(dataRow(), {
      success: true,
      data: { mean: 0.62 },
    });
    assert.equal(value, 0.62);
  });

  it("data.scene.mean 可读取嵌套对象", () => {
    const row = dataRow({
      name: "data.scene.mean",
      apiKey: "scene.mean",
    });
    const value = resolveOutputValue(row, {
      success: true,
      data: { scene: { mean: 0.41 } },
    });
    assert.equal(value, 0.41);
  });
});

describe("readDataPath", () => {
  it("可读取嵌套 data 路径", () => {
    assert.equal(
      readDataPath({ scene: { mean: 0.33 } }, "data.scene.mean"),
      0.33,
    );
  });

  it("null 根对象返回 undefined", () => {
    assert.equal(readDataPath(null, "data.mean"), undefined);
  });

  it("中间节点为数组时返回 undefined", () => {
    assert.equal(readDataPath({ scene: [1, 2] }, "data.scene.mean"), undefined);
  });

  it("不存在键返回 undefined", () => {
    assert.equal(readDataPath({ scene: {} }, "data.scene.mean"), undefined);
  });
});

describe("evaluateOutputStatus", () => {
  it("条件输出缺失返回 not-produced", () => {
    const row = fileRow({
      conditional: "仅提供标注/AOI 辅文件时产生",
      optional: true,
    });
    assert.equal(evaluateOutputStatus(row, undefined), "not-produced");
  });

  it("无 qualityRule 返回 unknown", () => {
    assert.equal(evaluateOutputStatus(dataRow(), 0.5), "unknown");
  });

  it("NDVI 超出 [-1, 1] 返回 attention", () => {
    const row = dataRow({ qualityRule: ndviRule });
    assert.equal(evaluateOutputStatus(row, 1.2), "attention");
  });

  it("NDVI 在 [-1, 1] 内返回 pass", () => {
    const row = dataRow({ qualityRule: ndviRule });
    assert.equal(evaluateOutputStatus(row, 0.5), "pass");
  });
});

describe("statusLabel", () => {
  it("四态均说明是否对照门槛，且 unknown 不写成合格", () => {
    assert.equal(statusLabel("pass"), "符合门槛");
    assert.equal(statusLabel("attention"), "超出门槛");
    assert.equal(statusLabel("unknown"), "未设门槛");
    assert.equal(statusLabel("not-produced"), "未产生");
  });
});

describe("statusExplain", () => {
  it("有 between 规则时写出对照区间", () => {
    const row = dataRow({ qualityRule: ndviRule });
    assert.match(statusExplain("pass", row), /落在登记门槛 -1～1 内/);
    assert.match(statusExplain("attention", row), /未落在登记门槛 -1～1 内/);
  });

  it("无规则时说明不能自动判合格", () => {
    assert.match(statusExplain("unknown", dataRow()), /没有可机器执行的统一门槛/);
  });
});

describe("extraUnregisteredFileKeys", () => {
  it("列出结果中未登记的文件键", () => {
    const keys = extraUnregisteredFileKeys([fileRow()], {
      success: true,
      files_http: {
        ndvi_tif: { url: "/ndvi.tif", vis: "raster_index", name: "ndvi.tif" },
        extra_tif: { url: "/extra.tif", vis: "none", name: "extra.tif" },
      },
    });
    assert.deepEqual(keys, ["extra_tif"]);
  });

  it("无结果时返回空数组", () => {
    assert.deepEqual(extraUnregisteredFileKeys([fileRow()], null), []);
  });
});

describe("originalApiPayload", () => {
  it("只保留算法服务信封，剔除控制台派生字段", () => {
    const payload = originalApiPayload({
      success: true,
      algorithm_id: "27_ndvi",
      algorithm: "NDVI植被指数",
      implemented: true,
      message: "已计算 NDVI",
      data: { min: -0.1, max: 0.9, mean: 0.6 },
      files: { ndvi_tif: "/tmp/ndvi.tif" },
      files_http: { ndvi_tif: { url: "/preview", vis: "raster_index", name: "ndvi.tif" } },
      job_id: "job-1",
    });
    assert.deepEqual(payload, {
      success: true,
      algorithm_id: "27_ndvi",
      algorithm: "NDVI植被指数",
      implemented: true,
      message: "已计算 NDVI",
      data: { min: -0.1, max: 0.9, mean: 0.6 },
      files: { ndvi_tif: "/tmp/ndvi.tif" },
    });
    assert.equal("files_http" in payload, false);
    assert.equal("job_id" in payload, false);
  });

  it("无结果时返回 null", () => {
    assert.equal(originalApiPayload(null), null);
  });
});

describe("flattenApiFields", () => {
  it("按信封、data、files 顺序逐项展开，嵌套对象拆成路径", () => {
    const fields = flattenApiFields({
      success: true,
      algorithm_id: "27_ndvi",
      algorithm: "NDVI植被指数",
      implemented: true,
      message: "已计算 NDVI",
      data: { min: -0.1, max: 0.9, mean: 0.6, shape: [16, 16] },
      files: { ndvi_tif: "/tmp/ndvi.tif", preview_png: "/tmp/ndvi.png" },
    });
    assert.deepEqual(
      fields.map((item) => item.path),
      [
        "success",
        "algorithm_id",
        "algorithm",
        "implemented",
        "message",
        "data.min",
        "data.max",
        "data.mean",
        "data.shape",
        "files.ndvi_tif",
        "files.preview_png",
      ],
    );
    assert.equal(fields.find((item) => item.path === "data.mean")?.value, 0.6);
    assert.deepEqual(fields.find((item) => item.path === "data.shape")?.value, [16, 16]);
  });

  it("无载荷时返回空数组", () => {
    assert.deepEqual(flattenApiFields(null), []);
  });
});

describe("knowledgeRowForPath", () => {
  it("按完整路径匹配知识库行", () => {
    const row = knowledgeRowForPath([fileRow(), dataRow()], "data.mean");
    assert.equal(row?.label, "均值");
  });

  it("无匹配时返回 undefined", () => {
    assert.equal(knowledgeRowForPath([dataRow()], "data.shape"), undefined);
  });
});

describe("fieldHelp / fieldTitle", () => {
  it("信封字段使用固定说明，不假装有产物知识", () => {
    const help = fieldHelp("success", undefined);
    assert.equal(help.source, "envelope");
    assert.match(help.text, /算法服务是否按协议返回成功/);
    assert.equal(fieldTitle("success", undefined), "调用成功");
  });

  it("无知识库的返回键标记说明待补充", () => {
    const help = fieldHelp("data.shape", undefined);
    assert.equal(help.source, "pending");
    assert.match(help.text, /说明待补充/);
  });
});

describe("groupApiFields", () => {
  it("按调用状态、计算结果、产物文件分组", () => {
    const groups = groupApiFields([
      { path: "success", value: true },
      { path: "data.mean", value: 0.42 },
      { path: "files.ndvi_tif", value: "/tmp/ndvi.tif" },
    ]);
    assert.deepEqual(
      groups.map((group) => group.id),
      ["status", "data", "files"],
    );
    assert.equal(groups[0].fields[0].path, "success");
    assert.equal(groups[1].label, "计算结果");
  });
});

describe("isInlineApiValue", () => {
  it("布尔、数字和单行字符串内联，对象用代码块", () => {
    assert.equal(isInlineApiValue(true), true);
    assert.equal(isInlineApiValue(0.42), true);
    assert.equal(isInlineApiValue("27_ndvi"), true);
    assert.equal(isInlineApiValue({ min: 0 }), false);
  });
});

describe("numericDomain", () => {
  it("优先使用知识库 between 定义域", () => {
    const domain = numericDomain("data.mean", 0.3, dataRow({ qualityRule: ndviRule }), []);
    assert.deepEqual(domain, { min: -1, max: 1, marker: 0.3 });
  });

  it("波段索引不会借用同级 min/max 当数轴", () => {
    const domain = numericDomain("data.red_band", 2, undefined, [
      { path: "data.min", value: -0.6 },
      { path: "data.max", value: 0.8 },
      { path: "data.red_band", value: 2 },
    ]);
    assert.equal(domain, null);
  });
});

describe("OutputWorkbench 实际渲染契约", () => {
  it("可见文本含字段解读/补充说明/判定依据，并暴露 tab 角色", async () => {
    const { html, visibleByTab } = await renderOutputWorkbenchFixture();
    assert.match(html, /role="tablist"/);
    assert.match(html, /role="tab"/);
    assert.match(html, /role="tabpanel"/);
    assert.match(visibleByTab.fields, /字段解读/);
    assert.match(visibleByTab.fields, /补充说明/);
    assert.match(visibleByTab.analysis, /判定依据/);
    assert.match(visibleByTab.analysis, /补充说明/);
    assert.doesNotMatch(html, /aria-hidden="true"[^>]*>字段解读/);
    assert.doesNotMatch(html, /hidden[^>]*>字段解读/);
  });
});

function createHostNode(kind, tag = "") {
  return {
    kind,
    tag,
    parent: null,
    children: [],
    props: {},
    handlers: {},
    text: "",
    style: { display: "" },
    className: "",
    setAttribute(key, value) {
      this.props[key] = value;
    },
    removeAttribute(key) {
      delete this.props[key];
    },
    getAttribute(key) {
      return this.props[key];
    },
  };
}

function hostNodeOps() {
  const ops = {
    patchProp(el, key, _prev, next) {
      if (key.startsWith("on") && typeof next === "function") {
        el.handlers[key.toLowerCase()] = next;
        return;
      }
      if (key === "style") {
        const incoming = typeof next === "object" && next ? next : {};
        Object.assign(el.style, incoming);
        el.props.style = el.style;
        return;
      }
      if (next == null || next === false) {
        delete el.props[key];
        return;
      }
      el.props[key] = next;
    },
    insert(child, parent, anchor) {
      if (child.parent) ops.remove(child);
      child.parent = parent;
      const index = anchor ? parent.children.indexOf(anchor) : -1;
      if (index >= 0) parent.children.splice(index, 0, child);
      else parent.children.push(child);
    },
    remove(child) {
      const parent = child.parent;
      if (!parent) return;
      const index = parent.children.indexOf(child);
      if (index >= 0) parent.children.splice(index, 1);
      child.parent = null;
    },
    createElement(tag) {
      return createHostNode("element", tag);
    },
    createText(text) {
      const node = createHostNode("text");
      node.text = String(text);
      return node;
    },
    createComment(text) {
      const node = createHostNode("comment");
      node.text = String(text);
      return node;
    },
    setText(node, text) {
      node.text = String(text);
    },
    setElementText(el, text) {
      for (const child of [...el.children]) ops.remove(child);
      if (text) ops.insert(ops.createText(text), el, null);
    },
    parentNode(node) {
      return node.parent;
    },
    nextSibling(node) {
      const parent = node.parent;
      if (!parent) return null;
      return parent.children[parent.children.indexOf(node) + 1] || null;
    },
    setScopeId(el, id) {
      el.props[id] = "";
    },
    insertStaticContent(content, parent, anchor) {
      const start = ops.createComment("static-start");
      const text = ops.createText(
        typeof content === "string" ? content.replace(/<[^>]*>/g, " ") : "",
      );
      const end = ops.createComment("static-end");
      ops.insert(start, parent, anchor);
      ops.insert(text, parent, anchor);
      ops.insert(end, parent, anchor);
      return [start, end];
    },
  };
  return ops;
}

function isHostHidden(node) {
  if (node.kind !== "element") return false;
  if (node.props.hidden != null && node.props.hidden !== false) return true;
  if (node.props["aria-hidden"] === true || node.props["aria-hidden"] === "true") return true;
  if (node.style && node.style.display === "none") return true;
  const style = node.props.style;
  if (typeof style === "string" && /display\s*:\s*none/i.test(style)) return true;
  if (style && typeof style === "object" && style.display === "none") return true;
  return false;
}

function hostVisibleText(node) {
  if (node.kind === "comment") return "";
  if (node.kind === "text") return node.text;
  if (node.kind === "element") {
    if (isHostHidden(node)) return "";
    return node.children.map(hostVisibleText).join("");
  }
  return "";
}

function hostToHtml(node) {
  if (node.kind === "comment") return `<!--${node.text}-->`;
  if (node.kind === "text") return node.text;
  const attrs = Object.entries(node.props)
    .map(([key, value]) => {
      if (value === true) return ` ${key}`;
      if (typeof value === "object") {
        if (key === "style") {
          const css = Object.entries(value)
            .map(([prop, item]) => `${prop}: ${item}`)
            .join("; ");
          return css ? ` style="${css}"` : "";
        }
        if (key === "class" && !Array.isArray(value)) {
          const names = Object.entries(value)
            .filter(([, on]) => on)
            .map(([name]) => name)
            .join(" ");
          return names ? ` class="${names}"` : "";
        }
        return "";
      }
      return ` ${key}="${String(value)}"`;
    })
    .join("");
  const inner = node.children.map(hostToHtml).join("");
  return `<${node.tag}${attrs}>${inner}</${node.tag}>`;
}

function findHost(node, predicate, acc = []) {
  if (node.kind === "element" && predicate(node)) acc.push(node);
  for (const child of node.children || []) findHost(child, predicate, acc);
  return acc;
}

function workbenchFixture() {
  const meanRow = dataRow({
    qualityRule: ndviRule,
    unit: "无量纲",
    range: "[-1, 1]",
  });
  return {
    algo: {
      id: "27_ndvi",
      title: "NDVI植被指数",
      level: "L3",
      group: "index",
      implemented: true,
      purpose: "计算 NDVI",
      scenario: "植被相对绿度",
      method: "归一化差分",
      endpoint: "/api/v1/27_ndvi/run",
      console_run: "/run/27_ndvi",
      compare: "single",
      testdata: { file: "input.tif", file2: null, params: {}, exists: true },
      output_summary: {
        what: "NDVI 栅格与场景统计",
        value: "相对绿度",
        caution: "不是处方",
      },
      fields: {
        inputs: [],
        outputs: [fileRow(), meanRow],
      },
    },
    result: {
      success: true,
      algorithm_id: "27_ndvi",
      algorithm: "NDVI植被指数",
      implemented: true,
      message: "已计算 NDVI",
      data: { mean: 0.62 },
      files: { ndvi_tif: "/tmp/ndvi.tif" },
      files_http: {
        ndvi_tif: { url: "/preview/ndvi.tif", vis: "raster_index", name: "ndvi.tif" },
      },
    },
  };
}

async function renderOutputWorkbenchFixture() {
  const { mkdir, writeFile, rm, readFile } = await import("node:fs/promises");
  const { join, dirname } = await import("node:path");
  const { fileURLToPath, pathToFileURL } = await import("node:url");
  const { parse, compileScript } = await import("vue/compiler-sfc");
  const { createRenderer, h, nextTick } = await import("@vue/runtime-core");
  const { execFile } = await import("node:child_process");
  const { promisify } = await import("node:util");

  const webRoot = dirname(fileURLToPath(new URL("../src/main.ts", import.meta.url)));
  const vuePath = join(webRoot, "components/OutputWorkbench.vue");
  const source = await readFile(vuePath, "utf8");
  const { descriptor } = parse(source, { filename: vuePath });
  const compiled = compileScript(descriptor, {
    id: "output-workbench",
    inlineTemplate: true,
  });
  const workdir = join(webRoot, "..", ".tmp-owb-render");
  await rm(workdir, { recursive: true, force: true });
  await mkdir(workdir, { recursive: true });
  const visStub = join(workdir, "VisPanel.mjs");
  const compiledFile = join(workdir, "OutputWorkbench.ts");
  const bundled = join(workdir, "OutputWorkbench.mjs");
  const outputWorkbenchTs = join(webRoot, "outputWorkbench.ts");
  await writeFile(
    visStub,
    "export default { name: 'VisPanel', props: ['title', 'asset', 'algorithmId'], setup() { return () => null; } };\n",
    "utf8",
  );
  const rewritten = compiled.content
    .replaceAll("./VisPanel.vue", "./VisPanel.mjs")
    .replaceAll("../outputWorkbench", outputWorkbenchTs);
  await writeFile(compiledFile, rewritten, "utf8");
  try {
    await promisify(execFile)(
      new URL("../node_modules/.bin/esbuild", import.meta.url).pathname,
      [
        compiledFile,
        "--bundle",
        "--platform=node",
        "--format=esm",
        `--outfile=${bundled}`,
        "--external:vue",
        "--external:@vue/runtime-core",
      ],
    );
    const mod = await import(`${pathToFileURL(bundled).href}?t=${Date.now()}`);
    const ops = hostNodeOps();
    const { createApp } = createRenderer(ops);
    const root = createHostNode("element", "div");
    const fixture = workbenchFixture();
    const app = createApp({
      render: () => h(mod.default, fixture),
    });
    app.mount(root);
    await nextTick();

    const tabs = findHost(root, (node) => node.props.role === "tab");
    const visibleByTab = {};
    for (const tab of tabs) {
      const click = tab.handlers.onclick || tab.handlers.onClick;
      if (typeof click === "function") click({});
      await nextTick();
      const label = hostVisibleText(tab).trim();
      const key = label.includes("字段解读")
        ? "fields"
        : label.includes("综合分析")
          ? "analysis"
          : "api";
      visibleByTab[key] = hostVisibleText(root);
    }
    return { html: hostToHtml(root), visibleByTab };
  } finally {
    await rm(workdir, { recursive: true, force: true });
  }
}
