/** 算法页正文里的字母简称：英文全称 + 中文。按词长优先匹配，避免 1D-CNN 再拆出 CNN。 */

export interface Term {
  abbr: string;
  en: string;
  zh: string;
  /** 正文里可能出现的其它写法，展示仍用 abbr */
  aliases?: string[];
}

export const TERMS: Term[] = [
  { abbr: "OSAVI", en: "Optimized Soil-Adjusted Vegetation Index", zh: "优化土壤调节植被指数" },
  { abbr: "GNDVI", en: "Green Normalized Difference Vegetation Index", zh: "绿色归一化差值植被指数" },
  { abbr: "RECI", en: "Red-Edge Chlorophyll Index", zh: "红边叶绿素指数" },
  { abbr: "NDSI", en: "Normalized Difference Snow Index", zh: "归一化差值雪指数" },
  { abbr: "ARVI", en: "Atmospherically Resistant Vegetation Index", zh: "耐大气植被指数" },
  { abbr: "VARI", en: "Visible Atmospherically Resistant Index", zh: "可见大气阻力指数" },
  { abbr: "SIPI", en: "Structure Insensitive Pigment Index", zh: "结构不敏感色素指数" },
  { abbr: "GCI", en: "Green Chlorophyll Index", zh: "绿色叶绿素指数" },
  { abbr: "NBR", en: "Normalized Burn Ratio", zh: "标准化燃烧率" },
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
  { abbr: "INS", en: "Inertial Navigation System", zh: "惯性导航系统" },
  { abbr: "RTK", en: "Real-Time Kinematic", zh: "实时动态差分定位" },
  { abbr: "RTS", en: "Rauch–Tung–Striebel smoother", zh: "RTS 平滑器" },
  { abbr: "HSI", en: "Hyperspectral Imagery", zh: "高光谱影像" },
  { abbr: "RGB", en: "Red Green Blue", zh: "真彩色三通道影像" },
  { abbr: "DN", en: "Digital Number", zh: "数字计数值（仪器原始灰度）" },
  { abbr: "NIR", en: "Near-Infrared", zh: "近红外" },
  { abbr: "SWIR", en: "Short-Wave Infrared", zh: "短波红外" },
  { abbr: "VNIR", en: "Visible and Near-Infrared", zh: "可见光–近红外" },
  { abbr: "RED", en: "Red band", zh: "红光波段" },
  { abbr: "GREEN", en: "Green band", zh: "绿光波段" },
  { abbr: "BLUE", en: "Blue band", zh: "蓝光波段" },
  { abbr: "RE", en: "Red Edge", zh: "红边" },
  { abbr: "REP", en: "Red Edge Position", zh: "红边位置" },
  { abbr: "REIP", en: "Red Edge Inflection Point", zh: "红边拐点" },
  { abbr: "SNR", en: "Signal-to-Noise Ratio", zh: "信噪比" },
  { abbr: "FPN", en: "Fixed Pattern Noise", zh: "固定模式噪声" },
  { abbr: "DOS2", en: "Dark Object Subtraction 2", zh: "暗目标减法第二代" },
  { abbr: "DOS", en: "Dark Object Subtraction", zh: "暗目标减法" },
  { abbr: "COST", en: "Cosine of the Solar Zenith Angle", zh: "太阳天顶角余弦透过率近似" },
  { abbr: "TOA", en: "Top of Atmosphere", zh: "大气层顶" },
  { abbr: "ESUN", en: "Exoatmospheric Solar Irradiance", zh: "大气层外太阳辐照度" },
  { abbr: "ELM", en: "Empirical Line Method", zh: "经验线法" },
  { abbr: "ROI", en: "Region of Interest", zh: "感兴趣区" },
  { abbr: "DEM", en: "Digital Elevation Model", zh: "数字高程模型" },
  { abbr: "CRS", en: "Coordinate Reference System", zh: "坐标参考系" },
  { abbr: "EPSG", en: "European Petroleum Survey Group code", zh: "EPSG 坐标系代码" },
  { abbr: "WGS84", en: "World Geodetic System 1984", zh: "1984 世界大地测量系统" },
  { abbr: "GCP", en: "Ground Control Point", zh: "地面控制点" },
  { abbr: "RMSE", en: "Root Mean Square Error", zh: "均方根误差" },
  { abbr: "FFT", en: "Fast Fourier Transform", zh: "快速傅里叶变换" },
  { abbr: "SLIC", en: "Simple Linear Iterative Clustering", zh: "简单线性迭代聚类超像素" },
  { abbr: "CIELAB", en: "CIE L*a*b* color space", zh: "CIE Lab 颜色空间" },
  {
    abbr: "SG",
    en: "Savitzky–Golay filter",
    zh: "Savitzky–Golay 平滑滤波",
    aliases: ["Savitzky-Golay", "Savitzky–Golay"],
  },
  { abbr: "PROSAIL", en: "PROSPECT + SAIL", zh: "叶片+冠层辐射传输耦合模型" },
  { abbr: "PROSPECT", en: "PROSPECT leaf optical model", zh: "叶片光学辐射传输模型" },
  { abbr: "SAIL", en: "Scattering by Arbitrarily Inclined Leaves", zh: "任意倾角叶片散射冠层模型" },
  { abbr: "LUT", en: "Look-Up Table", zh: "查找表" },
  { abbr: "LAI", en: "Leaf Area Index", zh: "叶面积指数" },
  { abbr: "Cab", en: "Chlorophyll a+b content", zh: "叶绿素含量" },
  { abbr: "ACE", en: "Adaptive Coherence Estimator", zh: "自适应余弦估计（目标探测）" },
  { abbr: "GLRT", en: "Generalized Likelihood Ratio Test", zh: "广义似然比检验" },
  { abbr: "CFAR", en: "Constant False Alarm Rate", zh: "恒虚警率" },
  { abbr: "FCLS", en: "Fully Constrained Least Squares", zh: "全约束最小二乘解混" },
  { abbr: "NNLS", en: "Non-Negative Least Squares", zh: "非负最小二乘" },
  { abbr: "LRX", en: "Local Reed–Xiaoli detector", zh: "局部 RX 异常检测" },
  { abbr: "RX", en: "Reed–Xiaoli anomaly detector", zh: "RX 异常检测（马氏距离）" },
  { abbr: "IR-MAD", en: "Iteratively Reweighted Multivariate Alteration Detection", zh: "迭代重加权多元变化检测" },
  { abbr: "MAD", en: "Multivariate Alteration Detection", zh: "多元变化检测" },
  { abbr: "CCA", en: "Canonical Correlation Analysis", zh: "典型相关分析" },
  { abbr: "OA", en: "Overall Accuracy", zh: "总体精度" },
  { abbr: "AA", en: "Average Accuracy", zh: "平均精度（各类召回均值）" },
  { abbr: "Kappa", en: "Cohen's Kappa", zh: "卡帕系数" },
  { abbr: "ANOVA", en: "Analysis of Variance", zh: "方差分析" },
  { abbr: "MinMax", en: "Min-max normalization", zh: "最小-最大归一化" },
  { abbr: "Z-score", en: "Standard score", zh: "标准化分数" },
  { abbr: "GeoTIFF", en: "Georeferenced Tagged Image File Format", zh: "带地理参考的 TIFF 栅格" },
  { abbr: "GeoJSON", en: "Geographic JSON", zh: "地理要素 JSON 矢量" },
  { abbr: "JSON", en: "JavaScript Object Notation", zh: "JSON 数据交换格式" },
  { abbr: "TIFF", en: "Tagged Image File Format", zh: "标签图像文件格式" },
  { abbr: "CSV", en: "Comma-Separated Values", zh: "逗号分隔值表格" },
  { abbr: "NoData", en: "No Data", zh: "无效值 / 无数据像元" },
  { abbr: "Fmask", en: "Function of mask", zh: "云与云影检测算法" },
  { abbr: "HITRAN", en: "High-Resolution Transmission molecular absorption database", zh: "高分辨率分子吸收数据库" },
  { abbr: "GDAL", en: "Geospatial Data Abstraction Library", zh: "地理空间数据抽象库" },
  { abbr: "GIS", en: "Geographic Information System", zh: "地理信息系统" },
  { abbr: "EMVA", en: "European Machine Vision Association", zh: "欧洲机器视觉协会" },
  { abbr: "USGS", en: "United States Geological Survey", zh: "美国地质调查局" },
  { abbr: "MODIS", en: "Moderate Resolution Imaging Spectroradiometer", zh: "中分辨率成像光谱仪" },
  { abbr: "LCTF", en: "Liquid Crystal Tunable Filter", zh: "液晶可调谐滤光片" },
  { abbr: "FLAASH", en: "Fast Line-of-sight Atmospheric Analysis of Spectral Hypercubes", zh: "快速视线大气校正" },
  { abbr: "ENVI", en: "Environment for Visualizing Images", zh: "ENVI 遥感处理软件" },
  { abbr: "AVIRIS", en: "Airborne Visible/Infrared Imaging Spectrometer", zh: "机载可见光/红外成像光谱仪" },
  { abbr: "PPS", en: "Pulse Per Second", zh: "秒脉冲硬件对时" },
  { abbr: "PTP", en: "Precision Time Protocol", zh: "精密时钟同步协议" },
  { abbr: "API", en: "Application Programming Interface", zh: "应用程序接口" },
  { abbr: "BRP", en: "Band Ratio Parameter", zh: "波段比参数" },
  { abbr: "TVI", en: "Transformed Vegetation Index", zh: "变换植被指数" },
  { abbr: "MSS", en: "Multispectral Scanner", zh: "多光谱扫描仪" },
  { abbr: "ERTS", en: "Earth Resources Technology Satellite", zh: "地球资源技术卫星" },
  { abbr: "L0", en: "Level 0", zh: "0 级：采集与质检" },
  { abbr: "L1", en: "Level 1", zh: "1 级：辐亮度" },
  { abbr: "L2", en: "Level 2", zh: "2 级：反射率与正射" },
  { abbr: "L3", en: "Level 3", zh: "3 级：指数与识别" },
  { abbr: "L4", en: "Level 4", zh: "4 级：地块统计" },
];

const BY_ABBR = new Map(TERMS.map((t) => [t.abbr, t]));

/** 某算法除正文匹配外也应展示的简称。 */
export const ALGO_EXTRA: Record<string, string[]> = {
  "01_flight_planning": ["GSD"],
  "02_sync_timestamp": ["HSI", "RGB", "POS"],
  "03_pos_solution": ["POS", "GPS", "IMU", "GNSS", "RTS"],
  "04_flight_qc": ["DN", "SNR"],
  "05_cloud_shadow": ["NDVI", "NIR", "Fmask"],
  "06_dark_current": ["DN", "FPN"],
  "07_bad_pixel": ["DN"],
  "08_destriping": ["DN", "FPN"],
  "09_smile_keystone": ["VNIR"],
  "10_radiance_calibration": ["DN"],
  "11_relative_radiometric": ["DN"],
  "12_panel_reflectance": ["ELM", "ROI"],
  "13_atmospheric_correction": ["DOS2", "ESUN"],
  "14_brdf_correction": ["BRDF"],
  "15_geo_locate": ["POS", "GSD", "EPSG"],
  "16_orthorectify": ["DEM", "GSD"],
  "17_mosaic": ["GeoTIFF", "CRS"],
  "18_color_balance": ["RGB"],
  "19_multi_source_register": ["HSI", "RGB", "FFT"],
  "20_bad_band_remove": ["NIR"],
  "21_savgol_smooth": ["SG"],
  "22_normalize": ["SNV"],
  "23_pca": ["PCA", "MNF"],
  "24_band_select": ["ANOVA"],
  "25_superpixel": ["SLIC"],
  "26_patch_build": ["CNN"],
  "27_ndvi": ["NDVI", "NIR", "RED"],
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
  "44_postprocess_smooth": ["GeoTIFF"],
  "45_parcel_zonal_stats": ["GeoJSON", "JSON"],
  "46_reci": ["RECI", "NIR", "RE"],
  "47_gndvi": ["GNDVI", "NIR"],
  "48_osavi": ["OSAVI", "NIR"],
  "49_arvi": ["ARVI", "NIR"],
  "50_vari": ["VARI"],
  "51_lai_index": ["LAI", "EVI", "NIR"],
  "52_nbr": ["NBR", "NIR", "SWIR"],
  "53_sipi": ["SIPI", "NIR"],
  "54_gci": ["GCI", "NIR"],
  "55_ndsi": ["NDSI", "SWIR"],
};

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function namesOf(term: Term): string[] {
  return [term.abbr, ...(term.aliases || [])];
}

/** 去掉链接和 DOI，避免把 HTTP、PDF 等网页噪声当成算法简称。 */
export function flattenText(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") {
    return value.replace(/https?:\/\/\S+/gi, " ").replace(/\b10\.\d{4,}\/\S+/g, " ");
  }
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return value.map(flattenText).join("\n");
  if (typeof value === "object") return Object.values(value).map(flattenText).join("\n");
  return "";
}

function findInText(text: string): Term[] {
  const catalog = [...TERMS].sort((a, b) => {
    const la = Math.max(...namesOf(a).map((n) => n.length));
    const lb = Math.max(...namesOf(b).map((n) => n.length));
    return lb - la;
  });
  const occupied: Array<[number, number]> = [];
  const kept: Term[] = [];
  const seen = new Set<string>();

  for (const term of catalog) {
    if (seen.has(term.abbr)) continue;
    for (const name of namesOf(term)) {
      const re = new RegExp(`(^|[^A-Za-z0-9])(${escapeRegExp(name)})(?![A-Za-z0-9])`, "g");
      let match: RegExpExecArray | null = re.exec(text);
      while (match) {
        const start = match.index + match[1].length;
        const end = start + name.length;
        const overlap = occupied.some(([s, e]) => start < e && end > s);
        match = re.exec(text);
        if (overlap) continue;
        seen.add(term.abbr);
        occupied.push([start, end]);
        kept.push(term);
        break;
      }
      if (seen.has(term.abbr)) break;
    }
  }
  return kept;
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

/** 扫描算法页实际展示的对象，收录其中出现的字母简称。 */
export function termsForPage(id: string, ...docs: unknown[]): Term[] {
  return termsForAlgorithm(id, ...docs.map(flattenText));
}

export function tooltipForTerms(terms: Term[]): string {
  return terms.map((t) => `${t.abbr}：${t.zh}（${t.en}）`).join("\n");
}

export function navZhLine(terms: Term[]): string {
  const zh = [...new Set(terms.map((t) => t.zh))];
  if (zh.length <= 3) return zh.join(" · ");
  return zh.slice(0, 3).join(" · ") + " 等";
}
