/** 与中达瑞和产品的适配程度。 */
export type FitLevel = "direct" | "adapt" | "no";

export type ProductFamily =
  | "air-hsi"
  | "air-msi"
  | "lab-hsi"
  | "line-hsi"
  | "ptz"
  | "chip"
  | "optic"
  | "software";

export interface WayhoProduct {
  id: string;
  name: string;
  series: string;
  band: string;
  mode: string;
  scene: string;
  /** 中达瑞和官网现网型号详情页。 */
  url: string;
  family: ProductFamily;
}

export interface ProductFit {
  productId: string;
  level: FitLevel;
  why: string;
}

/** 单条算法面向中达瑞和合作的产品 / 业务 / 应用分析。 */
export interface AlgoWayhoDoc {
  id: string;
  /** 一句话合作判断。 */
  verdict: string;
  /** 产品维度：吃什么数据、对上哪款机。 */
  product: string;
  /** 业务维度：帮对方卖什么、补哪段能力。 */
  business: string;
  /** 应用维度：落在官网哪些行业场景。 */
  application: string;
  /** 建议的合作切入方式。 */
  hook: string;
  fits: ProductFit[];
}
