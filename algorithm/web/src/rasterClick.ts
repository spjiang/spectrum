/** 把预览图点击换算成栅格行列（需考虑 object-fit: contain 的留白）。 */

export type BoxRect = { left: number; top: number; width: number; height: number };

export type RasterCell = { row: number; col: number };

/** 计算 contain 模式下实际图像在盒子里的位置。 */
export function containedImageRect(
  boxW: number,
  boxH: number,
  naturalW: number,
  naturalH: number,
): { x: number; y: number; w: number; h: number } | null {
  if (boxW <= 0 || boxH <= 0 || naturalW <= 0 || naturalH <= 0) return null;
  const scale = Math.min(boxW / naturalW, boxH / naturalH);
  const w = naturalW * scale;
  const h = naturalH * scale;
  return { x: (boxW - w) / 2, y: (boxH - h) / 2, w, h };
}

/** 将鼠标点击映射为像元 (row, col)；点在黑边上返回 null。 */
export function rasterClickToCell(
  clientX: number,
  clientY: number,
  rect: BoxRect,
  naturalW: number,
  naturalH: number,
  rasterW: number,
  rasterH: number,
): RasterCell | null {
  const drawn = containedImageRect(rect.width, rect.height, naturalW, naturalH);
  if (!drawn || rasterW < 1 || rasterH < 1) return null;
  const lx = clientX - rect.left - drawn.x;
  const ly = clientY - rect.top - drawn.y;
  if (lx < 0 || ly < 0 || lx >= drawn.w || ly >= drawn.h) return null;
  const col = Math.min(rasterW - 1, Math.max(0, Math.floor((lx / drawn.w) * rasterW)));
  const row = Math.min(rasterH - 1, Math.max(0, Math.floor((ly / drawn.h) * rasterH)));
  return { row, col };
}
