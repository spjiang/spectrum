/** 算法名称与原理文案里的简称：英文全称 + 中文译名。按词长优先匹配。 */

export interface Term {
  abbr: string;
  en: string;
  zh: string;
}

export const TERMS: Term[] = [
  { abbr: "MSAVI", en: "Modified Soil-Adjusted Vegetation Index", zh: "修正土壤调节植被指数" },
  { abbr: "MNDWI", en: "Modified Normalized Difference Water Index", zh: "改进归一化差值水体指数" },
  { abbr: "NDRE", en: "Normalized Difference Red Edge Index", zh: "归一化差值红边指数" },
  { abbr: "NDVI", en: "Normalized Difference Vegetation Index", zh: "归一化差值植被指数" },
  { abbr: "NDMI", en: "Normalized Difference Moisture Index", zh: "归一化差值水分指数" },
  { abbr: "NDWI", en: "Normalized Difference Water Index", zh: "归一化差值水体指数" },
  { abbr: "SAVI", en: "Soil-Adjusted Vegetation Index", zh: "土壤调节植被指数" },
  { abbr: "EVI", en: "Enhanced Vegetation Index", zh: "增强型植被指数" },
  { abbr: "1D-CNN", en: "One-Dimensional Convolutional Neural Network", zh: "一维卷积神经网络" },
  { abbr: "2D-CNN", en: "Two-Dimensional Convolutional Neural Network", zh: "二维卷积神经网络" },
  { abbr: "3D-CNN", en: "Three-Dimensional Convolutional Neural Network", zh: "三维卷积神经网络" },
  { abbr: "CNN", en: "Convolutional Neural Network", zh: "卷积神经网络" },
  { abbr: "RNN", en: "Recurrent Neural Network", zh: "循环神经网络" },
  { abbr: "GCN", en: "Graph Convolutional Network", zh: "图卷积网络" },
  { abbr: "Transformer", en: "Transformer", zh: "变换器网络（自注意力模型）" },
  { abbr: "SpectralFormer", en: "SpectralFormer", zh: "光谱 Transformer 分类网络" },
  { abbr: "HybridSN", en: "Hybrid Spectral Network", zh: "混合空谱卷积网络" },
  { abbr: "SVM", en: "Support Vector Machine", zh: "支持向量机" },
  { abbr: "RF", en: "Random Forest", zh: "随机森林" },
  { abbr: "SAM", en: "Spectral Angle Mapper", zh: "光谱角制图 / 光谱角匹配" },
  { abbr: "SID", en: "Spectral Information Divergence", zh: "光谱信息散度" },
  { abbr: "PCA", en: "Principal Component Analysis", zh: "主成分分析" },
  { abbr: "MNF", en: "Minimum Noise Fraction", zh: "最小噪声分离变换" },
  { abbr: "ICA", en: "Independent Component Analysis", zh: "独立成分分析" },
  { abbr: "PLS", en: "Partial Least Squares", zh: "偏最小二乘" },
  { abbr: "SNV", en: "Standard Normal Variate", zh: "标准正态变量变换" },
  { abbr: "BRDF", en: "Bidirectional Reflectance Distribution Function", zh: "双向反射分布函数" },
  { abbr: "GSD", en: "Ground Sample Distance", zh: "地面采样距离" },
  { abbr: "POS", en: "Position and Orientation System", zh: "定位定姿系统" },
  { abbr: "GPS", en: "Global Positioning System", zh: "全球定位系统" },
  { abbr: "GNSS", en: "Global Navigation Satellite System", zh: "全球卫星导航系统" },
  { abbr: "IMU", en: "Inertial Measurement Unit", zh: "惯性测量单元" },
  { abbr: "RTK", en: "Real-Time Kinematic", zh: "实时动态差分定位" },
  { abbr: "RTS", en: "Rauch–Tung–Striebel smoother", zh: "RTS 平滑器" },
  { abbr: "HSI", en: "Hyperspectral Imagery", zh: "高光谱影像" },
  { abbr: "RGB", en: "Red Green Blue", zh: "真彩色三通道影像" },
  { abbr: "DN", en: "Digital Number", zh: "数字计数值（仪器原始灰度）" },
  { abbr: "NIR", en: "Near-Infrared", zh: "近红外" },
  { abbr: "SWIR", en: "Short-Wave Infrared", zh: "短波红外" },
  { abbr: "RE", en: "Red Edge", zh: "红边" },
  { abbr: "REP", en: "Red Edge Position", zh: "红边位置" },
  { abbr: "SNR", en: "Signal-to-Noise Ratio", zh: "信噪比" },
  { abbr: "FPN", en: "Fixed Pattern Noise", zh: "固定模式噪声" },
  { abbr: "DOS2", en: "Dark Object Subtraction 2", zh: "暗目标减法（Chavez 第二代）" },
  { abbr: "DOS", en: "Dark Object Subtraction", zh: "暗目标减法" },
  { abbr: "ESUN", en: "Exoatmospheric Solar Irradiance", zh: "大气层外太阳辐照度" },
  { abbr: "ELM", en: "Empirical Line Method", zh: "经验线法" },
  { abbr: "ROI", en: "Region of Interest", zh: "感兴趣区" },
  { abbr: "DEM", en: "Digital Elevation Model", zh: "数字高程模型" },
  { abbr: "CRS", en: "Coordinate Reference System", zh: "坐标参考系" },
  { abbr: "EPSG", en: "European Petroleum Survey Group code", zh: "EPSG 坐标系代码" },
  { abbr: "GCP", en: "Ground Control Point", zh: "地面控制点" },
  { abbr: "FFT", en: "Fast Fourier Transform", zh: "快速傅里叶变换" },
  { abbr: "SLIC", en: "Simple Linear Iterative Clustering", zh: "简单线性迭代聚类超像素" },
  { abbr: "SG", en: "Savitzky–Golay filter", zh: "Savitzky–Golay 平滑滤波" },
  { abbr: "Savitzky-Golay", en: "Savitzky–Golay filter", zh: "萨维茨基–戈莱滤波（多项式滑动平滑）" },
  { abbr: "Savitzky–Golay", en: "Savitzky–Golay filter", zh: "萨维茨基–戈莱滤波（多项式滑动平滑）" },
  { abbr: "PROSAIL", en: "PROSPECT + SAIL", zh: "叶片+冠层辐射传输耦合模型" },
  { abbr: "PROSPECT", en: "PROSPECT leaf optical model", zh: "叶片光学辐射传输模型" },
  { abbr: "SAIL", en: "Scattering by Arbitrarily Inclined Leaves", zh: "任意倾角叶片散射冠层模型" },
  { abbr: "LUT", en: "Look-Up Table", zh: "查找表" },
  { abbr: "LAI", en: "Leaf Area Index", zh: "叶面积指数" },
  { abbr: "Cab", en: "Chlorophyll a+b content", zh: "叶绿素含量" },
  { abbr: "ACE", en: "Adaptive Coherence Estimator", zh: "自适应余弦估计（目标探测）" },
  { abbr: "FCLS", en: "Fully Constrained Least Squares", zh: "全约束最小二乘解混" },
  { abbr: "LRX", en: "Local Reed–Xiaoli detector", zh: "局部 RX 异常检测" },
  { abbr: "RX", en: "Reed–Xiaoli anomaly detector", zh: "RX 异常检测（马氏距离）" },
  { abbr: "IR-MAD", en: "Iteratively Reweighted Multivariate Alteration Detection", zh: "迭代重加权多元变化检测" },
  { abbr: "MAD", en: "Multivariate Alteration Detection", zh: "多元变化检测" },
  { abbr: "CCA", en: "Canonical Correlation Analysis", zh: "典型相关分析" },
  { abbr: "OA", en: "Overall Accuracy", zh: "总体精度" },
  { abbr: "AA", en: "Average Accuracy", zh: "平均精度（各类召回均值）" },
  { abbr: "Kappa", en: "Cohen's Kappa", zh: "卡帕系数" },
  { abbr: "ANOVA", en: "Analysis of Variance", zh: "方差分析" },
  { abbr: "GeoTIFF", en: "Georeferenced Tagged Image File Format", zh: "带地理参考的 TIFF 栅格" },
  { abbr: "GeoJSON", en: "Geographic JSON", zh: "地理要素 JSON 矢量" },
];

const BY_ABBR = new Map(TERMS.map((t) => [t.abbr, t]));

/** 某算法除标题外也应展示的简称。 */
export const ALGO_EXTRA: Record<string, string[]> = {
  "01_flight_planning": ["GSD"],
  "02_sync_timestamp": ["HSI", "RGB", "POS"],
  "03_pos_solution": ["POS", "GPS", "IMU", "GNSS", "RTS"],
  "04_flight_qc": ["DN", "SNR"],
  "06_dark_current": ["DN", "FPN"],
  "10_radiance_calibration": ["DN"],
  "12_panel_reflectance": ["ELM", "ROI"],
  "13_atmospheric_correction": ["DOS2", "ESUN"],
  "14_brdf_correction": ["BRDF"],
  "15_geo_locate": ["POS", "GSD", "EPSG"],
  "16_orthorectify": ["DEM", "GSD"],
  "19_multi_source_register": ["HSI", "RGB", "FFT"],
  "21_savgol_smooth": ["Savitzky-Golay", "SG"],
  "22_normalize": ["SNV"],
  "23_pca": ["PCA", "MNF"],
  "25_superpixel": ["SLIC"],
  "27_ndvi": ["NDVI", "NIR"],
  "28_ndre": ["NDRE", "NIR", "RE"],
  "29_evi_savi": ["EVI", "SAVI", "MSAVI", "NIR"],
  "30_ndmi_ndwi": ["NDMI", "NDWI", "MNDWI", "NIR", "SWIR"],
  "31_red_edge_params": ["REP", "SG"],
  "32_regression_inversion": ["PLS", "SNV"],
  "33_physical_inversion": ["PROSAIL", "LUT", "LAI", "Cab"],
  "34_svm_rf_classify": ["SVM", "RF", "OA", "AA", "Kappa"],
  "35_spectral_matching": ["SAM", "SID"],
  "36_cnn1d_classify": ["1D-CNN", "CNN", "RNN"],
  "37_cnn3d_classify": ["3D-CNN", "2D-CNN", "CNN", "HybridSN", "PCA"],
  "38_transformer_classify": ["Transformer", "GCN", "SpectralFormer"],
  "39_few_shot_classify": ["SAM"],
  "40_detect_segment": ["ACE", "NDVI"],
  "41_unmixing": ["FCLS"],
  "42_anomaly_detect": ["RX", "LRX"],
  "43_change_detect": ["IR-MAD", "MAD", "CCA"],
  "45_parcel_zonal_stats": ["GeoJSON", "JSON"],
};

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function findInText(text: string): Term[] {
  const hit: Term[] = [];
  const seen = new Set<string>();
  for (const t of TERMS) {
    const re = new RegExp(`(^|[^A-Za-z0-9])${escapeRegExp(t.abbr)}(?![A-Za-z0-9])`);
    if (re.test(text) && !seen.has(t.abbr)) {
      seen.add(t.abbr);
      hit.push(t);
    }
  }
  return hit;
}

export function termsFromText(...parts: Array<string | undefined | null>): Term[] {
  const text = parts.filter(Boolean).join(" \n ");
  return findInText(text);
}

export function termsForAlgorithm(
  id: string,
  ...parts: Array<string | undefined | null>
): Term[] {
  const byAbbr = new Map<string, Term>();
  for (const t of termsFromText(...parts)) byAbbr.set(t.abbr, t);
  for (const abbr of ALGO_EXTRA[id] || []) {
    const t = BY_ABBR.get(abbr);
    if (t) byAbbr.set(t.abbr, t);
  }
  const order = TERMS.map((t) => t.abbr);
  return [...byAbbr.values()].sort((a, b) => order.indexOf(a.abbr) - order.indexOf(b.abbr));
}

export function tooltipForTerms(terms: Term[]): string {
  return terms.map((t) => `${t.abbr}：${t.zh}（${t.en}）`).join("\n");
}

export function navZhLine(terms: Term[]): string {
  const zh = [...new Set(terms.map((t) => t.zh))];
  if (zh.length <= 3) return zh.join(" · ");
  return zh.slice(0, 3).join(" · ") + " 等";
}
