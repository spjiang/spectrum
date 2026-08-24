import type { WayhoProduct } from "./types";

/** 官网首页。 */
export const WAYHO_HOME = "https://www.wayho.cn/";
/** 官网产品中心。 */
export const WAYHO_CATALOG = "https://www.wayho.cn/pr.jsp";

/** 官网现网型号详情页（新站 SEO 路径，旧 PHP ProductDetail 已下线）。 */
export function wayhoPage(path: string): string {
  return `https://www.wayho.cn/${path}`;
}

export const WAYHO_PRODUCTS: WayhoProduct[] = [
  {
    id: "sky-w417",
    name: "SKY-W417",
    series: "机载高光谱",
    band: "400–1700 nm · 1200 通道 · 2.4 nm",
    mode: "推扫",
    scene: "大疆 M300/M350，低空遥感普查",
    url: wayhoPage("airborne-hyperspectral/sky-w417.html"),
    family: "air-hsi",
  },
  {
    id: "max-s810",
    name: "MAX-S810",
    series: "机载多光谱",
    band: "400–1000 nm · 7 光谱 + RGB",
    mode: "分立滤光云台",
    scene: "农林水生态巡飞，实时指数与处方图",
    url: wayhoPage("airborne-multispectral/max-s810.html"),
    family: "air-msi",
  },
  {
    id: "max-g800",
    name: "MAX-G800",
    series: "视频多光谱",
    band: "7+RGB（标配含 720/750 nm 红边）",
    mode: "视频多光谱",
    scene: "挂载、便携、室内近距",
    url: wayhoPage("multispectral/max-g800.html"),
    family: "air-msi",
  },
  {
    id: "shis-v220",
    name: "SHIS-V220",
    series: "凝视型高光谱",
    band: "420–750 nm · LCTF",
    mode: "凝采",
    scene: "实验室可见光、颜色与材料",
    url: wayhoPage("staring-hyperspectral/shis-v220.html"),
    family: "lab-hsi",
  },
  {
    id: "shis-n220",
    name: "SHIS-N220",
    series: "凝视型高光谱",
    band: "400–1000 nm · LCTF",
    mode: "凝采",
    scene: "实验室 VNIR、物证、表型",
    url: wayhoPage("staring-hyperspectral/shis-n220.html"),
    family: "lab-hsi",
  },
  {
    id: "shis-s260",
    name: "SHIS-S260",
    series: "凝视型高光谱",
    band: "920–1700 nm · InGaAs",
    mode: "凝采",
    scene: "SWIR 材料、水分、工业近距",
    url: wayhoPage("staring-hyperspectral/shis-s260.html"),
    family: "lab-hsi",
  },
  {
    id: "vix-n320",
    name: "VIX-N320",
    series: "内置推扫高光谱",
    band: "400–1000 nm · 2.5 nm",
    mode: "内置推扫",
    scene: "便携室内外采集，约 6 s 全谱",
    url: wayhoPage("built-in-push-broom/vix-n320.html"),
    family: "line-hsi",
  },
  {
    id: "vix-s230",
    name: "VIX-S230",
    series: "外置推扫 SWIR",
    band: "900–1700 nm · 512 通道 · 最高 1800 fps",
    mode: "外置推扫",
    scene: "工业分选、材料在线",
    url: wayhoPage("external-push-broom/vix-s230.html"),
    family: "line-hsi",
  },
  {
    id: "vix-w330",
    name: "VIX-W330",
    series: "全波段便携推扫",
    band: "400–1700 nm · ≤2.4 nm",
    mode: "内置推扫 + 同轴 RGB",
    scene: "野外勘察、高校表型、近距全谱",
    url: wayhoPage("built-in-push-broom/vix-w330.html"),
    family: "line-hsi",
  },
  {
    id: "svc-2p4m30",
    name: "SVC-2P4M30",
    series: "光谱智能摄像机",
    band: "5 光谱 + RGB（含 720/850 nm）",
    mode: "云台视频",
    scene: "24 h 定点监测，岸线/农田/漏油",
    url: wayhoPage("pr.jsp"),
    family: "ptz",
  },
  {
    id: "hsc-sc035",
    name: "HSC-SC035",
    series: "光谱成像芯片",
    band: "450–900 nm · 8 通道 · 180 fps",
    mode: "像元级快照",
    scene: "机器视觉嵌入、消费与工业模组",
    url: wayhoPage("spectral-imaging-chip/hsc-sc035.html"),
    family: "chip",
  },
  {
    id: "lctf",
    name: "LCTF-N20",
    series: "液晶可调谐滤波器",
    band: "450–950 nm · 电控窄带",
    mode: "电控窄带滤波",
    scene: "自组光路，不是成像产品",
    url: wayhoPage("lctf/lctf-n20.html"),
    family: "optic",
  },
  {
    id: "iriscube",
    name: "IrisCube",
    series: "光谱分析软件",
    band: "—",
    mode: "PC 端曲线 / PCA / 分类",
    scene: "实验室与近距数据回放",
    url: wayhoPage("spectral-analysis-software/iriscube.html"),
    family: "software",
  },
  {
    id: "cloud",
    name: "IrisCube Cloud",
    series: "光谱云平台",
    band: "—",
    mode: "存储 / 标注 / 训练 / 部署",
    scene: "宣称第三方算法接入",
    url: wayhoPage("spectral-analysis-software/iriscube-cloud.html"),
    family: "software",
  },
];

const BY_ID = new Map(WAYHO_PRODUCTS.map((p) => [p.id, p]));

export function getWayhoProduct(id: string): WayhoProduct | undefined {
  return BY_ID.get(id);
}
