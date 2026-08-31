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
  knowledgeRowForPath,
  numericDomain,
  originalApiPayload,
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
  it("四态均有独立中文标签，且 unknown 不写成通过", () => {
    assert.equal(statusLabel("pass"), "通过");
    assert.equal(statusLabel("attention"), "需关注");
    assert.equal(statusLabel("unknown"), "不可判定");
    assert.equal(statusLabel("not-produced"), "未产生");
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
