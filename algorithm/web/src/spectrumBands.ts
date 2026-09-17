/** 控制台顶栏光谱说明：典型中心波长，供对照用，不是某台相机的固定窗口。 */

export type SpectrumBandId = "blue" | "green" | "red" | "re" | "nir" | "swir";

export interface SpectrumBand {
  id: SpectrumBandId;
  name: string;
  abbr: string;
  nm: number;
  nmLabel: string;
  color: string;
  region: string;
}

export const SPECTRUM_BANDS: SpectrumBand[] = [
  { id: "blue", name: "蓝", abbr: "B", nm: 480, nmLabel: "480 nm", color: "#5b8dff", region: "可见光" },
  { id: "green", name: "绿", abbr: "G", nm: 560, nmLabel: "560 nm", color: "#3dbe5a", region: "可见光" },
  { id: "red", name: "红", abbr: "R", nm: 660, nmLabel: "660 nm", color: "#e24a38", region: "可见光" },
  { id: "re", name: "红边", abbr: "RE", nm: 720, nmLabel: "720 nm", color: "#d89a28", region: "红边" },
  { id: "nir", name: "近红外", abbr: "NIR", nm: 800, nmLabel: "800 nm", color: "#c45a68", region: "近红外" },
  { id: "swir", name: "短波红外", abbr: "SWIR", nm: 1600, nmLabel: "1600 nm", color: "#8b7ac4", region: "短波红外" },
];

export interface SpectrumRegion {
  id: string;
  label: string;
  fromNm: number;
  toNm: number;
}

export const SPECTRUM_REGIONS: SpectrumRegion[] = [
  { id: "vis", label: "可见光", fromNm: 400, toNm: 700 },
  { id: "nir", label: "近红外", fromNm: 750, toNm: 1000 },
  { id: "swir", label: "短波红外", fromNm: 1050, toNm: 2200 },
];

export const AXIS_TICKS_NM = [400, 500, 600, 700, 800, 1000, 1600];

/** 当前算法原理页明确用到的波段；未列入则不打高亮。 */
export const ALGORITHM_SPECTRUM_BANDS: Partial<Record<string, SpectrumBandId[]>> = {
  "27_ndvi": ["red", "nir"],
  "28_ndre": ["re", "nir"],
  "29_evi_savi": ["blue", "red", "nir"],
  "30_ndmi_ndwi": ["green", "nir", "swir"],
  "31_red_edge_params": ["red", "re", "nir"],
  "46_reci": ["re", "nir"],
  "47_gndvi": ["green", "nir"],
  "48_osavi": ["red", "nir"],
  "49_arvi": ["blue", "red", "nir"],
  "50_vari": ["blue", "green", "red"],
  "51_lai_index": ["blue", "red", "nir"],
  "52_nbr": ["nir", "swir"],
  "53_sipi": ["blue", "red", "nir"],
  "54_gci": ["green", "nir"],
  "55_ndsi": ["green", "swir"],
};

export const AXIS_LEFT = 36;
export const AXIS_RIGHT = 712;
export const SPLIT_NM = 1000;
export const SPLIT_RATIO = 0.74;
export const AXIS_GAP = 11;
export const BAR_Y = 30;
export const BAR_H = 11;

/** 可见–近红外拉宽，短波红外压缩；1000 nm 处为轴断开。 */
export function nmToX(nm: number): number {
  const span = AXIS_RIGHT - AXIS_LEFT;
  if (nm <= SPLIT_NM) {
    return AXIS_LEFT + ((nm - 400) / 600) * span * SPLIT_RATIO;
  }
  return (
    AXIS_LEFT +
    span * SPLIT_RATIO +
    ((Math.min(nm, 2200) - SPLIT_NM) / 1200) * span * (1 - SPLIT_RATIO)
  );
}

export function visBar(): { x: number; width: number } {
  const x = AXIS_LEFT;
  const width = nmToX(SPLIT_NM) - AXIS_LEFT - AXIS_GAP / 2;
  return { x, width };
}

export function swirBar(): { x: number; width: number } {
  const x = nmToX(SPLIT_NM) + AXIS_GAP / 2;
  return { x, width: AXIS_RIGHT - x };
}

export function visOffset(nm: number): string {
  const bar = visBar();
  return `${(((nmToX(Math.min(nm, SPLIT_NM)) - bar.x) / bar.width) * 100).toFixed(2)}%`;
}

export function swirOffset(nm: number): string {
  const bar = swirBar();
  return `${(((nmToX(Math.max(nm, SPLIT_NM)) - bar.x) / bar.width) * 100).toFixed(2)}%`;
}

export function bandsForAlgorithm(algorithmId: string | undefined): Set<SpectrumBandId> {
  if (!algorithmId) return new Set();
  return new Set(ALGORITHM_SPECTRUM_BANDS[algorithmId] ?? []);
}

export function bracketPath(fromNm: number, toNm: number, y: number, rise = 5): string {
  const x1 = nmToX(fromNm);
  const x2 = nmToX(toNm);
  return `M ${x1.toFixed(2)} ${y} V ${y - rise} H ${x2.toFixed(2)} V ${y}`;
}
