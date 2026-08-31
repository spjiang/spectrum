import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { containedImageRect, rasterClickToCell } from "../.tmp-raster-click/rasterClick.js";

describe("rasterClickToCell", () => {
  it("宽盒子 contain 时，点彩色区左上角是 (0,0) 而不是被黑边偏移成 (0,5)", () => {
    const rect = { left: 0, top: 0, width: 400, height: 150 };
    const naturalW = 150;
    const naturalH = 150;
    const rasterW = 16;
    const rasterH = 16;
    const drawn = containedImageRect(rect.width, rect.height, naturalW, naturalH);
    assert.ok(drawn);
    // 旧逻辑：x = clientX / 400，点在图像左缘 125px 处会得到 col = 5
    const naiveCol = Math.floor((drawn.x / rect.width) * rasterW);
    assert.equal(naiveCol, 5);

    const cell = rasterClickToCell(drawn.x + 1, drawn.y + 1, rect, naturalW, naturalH, rasterW, rasterH);
    assert.deepEqual(cell, { row: 0, col: 0 });
  });

  it("点在左右黑边上不取像元", () => {
    const rect = { left: 0, top: 0, width: 400, height: 150 };
    assert.equal(rasterClickToCell(10, 10, rect, 150, 150, 16, 16), null);
  });

  it("点右下角落到最后一个像元", () => {
    const rect = { left: 0, top: 0, width: 400, height: 150 };
    const drawn = containedImageRect(400, 150, 150, 150);
    assert.ok(drawn);
    const cell = rasterClickToCell(
      drawn.x + drawn.w - 0.5,
      drawn.y + drawn.h - 0.5,
      rect,
      150,
      150,
      16,
      16,
    );
    assert.deepEqual(cell, { row: 15, col: 15 });
  });
});
