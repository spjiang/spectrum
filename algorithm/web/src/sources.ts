/** 算法来源：每条文献都带可打开的 url（doi 落地页、官方文档或开放 PDF）。 */

export interface Cite {
  authors: string;
  year: string;
  title: string;
  venue: string;
  url: string;
}

export interface AlgoSource {
  /** 本仓库实际采用的方法（与 service / METHODS 一致） */
  method: string;
  cites: Cite[];
  /** 实现与原文的差异；工程项也挂官方/教科书级来源，不编造发明人 */
  note: string;
}

function paper(
  authors: string,
  year: string,
  title: string,
  venue: string,
  url: string,
): Cite {
  return { authors, year, title, venue, url };
}

const SOURCES: Record<string, AlgoSource> = {
  "01_flight_planning": {
    method: "摄影测量 GSD 与航带重叠公式",
    cites: [
      paper(
        "Colomina I., Molina P.",
        "2014",
        "Unmanned aerial systems for photogrammetry and remote sensing: A review",
        "ISPRS Journal of Photogrammetry and Remote Sensing, 92, 79–97",
        "https://doi.org/10.1016/j.isprsjprs.2014.02.013",
      ),
    ],
    note: "GSD = 航高 × 像元尺寸 / 焦距 是摄影测量几何关系。Colomina & Molina 综述了无人机摄影测量中的航高、地面分辨率与航带设计。本仓库在矩形测区上铺往返航点，未做禁飞区与飞控格式导出。",
  },
  "02_sync_timestamp": {
    method: "以 HSI 曝光时刻为基准的 POS 内插 + RGB 最近邻",
    cites: [
      paper(
        "Mostafa M. M. R., Schwarz K. P.",
        "2001",
        "Digital image georeferencing from a multiple camera system by GPS/INS",
        "ISPRS Journal of Photogrammetry and Remote Sensing, 56(1), 1–12",
        "https://doi.org/10.1016/S0924-2716(01)00030-2",
      ),
    ],
    note: "多传感器时间对齐是机载直接地理定位的前置步骤。Mostafa & Schwarz 讨论了 GPS/INS 轨迹与多相机曝光时刻的配准。本仓库按曝光时刻线性内插 POS、对 RGB 做最近邻匹配，不是 PPS/PTP 硬件同步。",
  },
  "03_pos_solution": {
    method: "位置互补滤波 + RTS 平滑 + 杠杆臂",
    cites: [
      paper(
        "Rauch H. E., Tung F., Striebel C. T.",
        "1965",
        "Maximum likelihood estimates of linear dynamic systems",
        "AIAA Journal, 3(8), 1445–1450",
        "https://doi.org/10.2514/3.3166",
      ),
      paper(
        "Särkkä S.",
        "2016",
        "Lecture 7: Bayesian Smoother, Gaussian and Particle Smoothers（含 RTS 递推公式）",
        "Aalto University",
        "https://users.aalto.fi/~ssarkka/course_k2016/handout7.pdf",
      ),
    ],
    note: "RTS 是 Rauch–Tung–Striebel 固定区间平滑。本仓库的位置融合是互补滤波，不是 GNSS/IMU 紧组合 EKF。",
  },
  "04_flight_qc": {
    method: "按位深判饱和 + 波段 SNR ≈ μ/σ",
    cites: [
      paper(
        "U.S. Geological Survey",
        "2024",
        "Landsat Collection 2 Quality Assessment Bands（饱和与像元质量标志）",
        "USGS Landsat Missions",
        "https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands",
      ),
      paper(
        "European Machine Vision Association",
        "2021",
        "EMVA Standard 1288 — Standard for Characterization of Image Sensors and Cameras",
        "EMVA",
        "https://www.emva.org/standards-technology/emva-1288/",
      ),
    ],
    note: "过曝/饱和质检对齐 USGS QA_RADSAT 一类产品说明；SNR 定义见 EMVA 1288。本仓库用全图统计，不是均匀区实验室 SNR。",
  },
  "05_cloud_shadow": {
    method: "Fmask 光谱规则的简化（无热红外）",
    cites: [
      paper(
        "Zhu Z., Woodcock C. E.",
        "2012",
        "Object-based cloud and cloud shadow detection in Landsat imagery",
        "Remote Sensing of Environment, 118, 83–94",
        "https://doi.org/10.1016/j.rse.2011.10.028",
      ),
    ],
    note: "完整 Fmask 使用 TOA 反射率、亮温与云影几何匹配。本仓库只有可见光/近红外光谱规则，低空树影易误报，不能等同于 Zhu & Woodcock 2012 全文算法。",
  },
  "06_dark_current": {
    method: "暗帧相减 + 列向固定模式噪声",
    cites: [
      paper(
        "European Machine Vision Association",
        "2021",
        "EMVA Standard 1288 — Standard for Characterization of Image Sensors and Cameras（暗电流与 FPN）",
        "EMVA",
        "https://www.emva.org/standards-technology/emva-1288/",
      ),
    ],
    note: "暗电流与固定模式噪声校正是成像传感器定标的标准步骤，EMVA 1288 给出测量定义。本仓库无温度/积分时间模型。",
  },
  "07_bad_pixel": {
    method: "残差超 6σ 检测热/死像元后邻域填充",
    cites: [
      paper(
        "European Machine Vision Association",
        "2021",
        "EMVA Standard 1288 — Standard for Characterization of Image Sensors and Cameras（缺陷像元）",
        "EMVA",
        "https://www.emva.org/standards-technology/emva-1288/",
      ),
    ],
    note: "σ 门限坏点检测是统计离群点做法，缺陷像元的工业定义见 EMVA 1288。本仓库不做沿轨方向插值，也无出厂坏元时序表。",
  },
  "08_destriping": {
    method: "列向矩匹配去条带",
    cites: [
      paper(
        "Gadallah F. L., Csillag F., Smith E. J.",
        "2000",
        "Destriping multisensor imagery with moment matching",
        "International Journal of Remote Sensing, 21(12), 2505–2511",
        "https://doi.org/10.1080/01431160050030592",
      ),
    ],
    note: "矩匹配是推扫条带校正的常用实现（ENVI 等软件亦提供）。沿列的真实地物纹理可能被轻微改变。",
  },
  "09_smile_keystone": {
    method: "场景内互相关估计 smile/keystone 后重采样",
    cites: [
      paper(
        "Neville R. A., Sun L., Staenz K.",
        "2004",
        "Detection of keystone in imaging spectrometer data",
        "Proc. SPIE 5425, Algorithms and Technologies for Multispectral, Hyperspectral, and Ultraspectral Imagery X",
        "https://doi.org/10.1117/12.542806",
      ),
      paper(
        "Green R. O., et al.",
        "1998",
        "Imaging spectroscopy and the Airborne Visible/Infrared Imaging Spectrometer (AVIRIS)",
        "Remote Sensing of Environment, 65(3), 227–248",
        "https://doi.org/10.1016/S0034-4257(98)00064-9",
      ),
    ],
    note: "光谱微笑与关键石畸变是推扫成像光谱仪的几何问题。Neville 等给出场景内检测方法；Green 等在 AVIRIS 综述中说明了该类畸变。本仓库用场景互相关估计，没有实验室波长查找表。",
  },
  "10_radiance_calibration": {
    method: "逐波段 L = gain × DN + offset",
    cites: [
      paper(
        "U.S. Geological Survey",
        "2024",
        "Using the USGS Landsat Level-1 Data Product（L = M_L·Qcal + A_L）",
        "USGS Landsat Missions",
        "https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product",
      ),
    ],
    note: "线性辐射定标是 USGS 等产品说明中的标准形式。本仓库默认增益仅为教学量级，不是某台真实相机的实验室系数。",
  },
  "11_relative_radiometric": {
    method: "逐波段直方图匹配",
    cites: [
      paper(
        "scikit-image developers",
        "2024",
        "Histogram matching（match_histograms）",
        "scikit-image documentation",
        "https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_histogram_matching.html",
      ),
    ],
    note: "直方图匹配是数字图像处理中的标准操作（Gonzalez & Woods《Digital Image Processing》亦专章讲述）。本仓库用于镶嵌观感一致，不适合作为定量反演前的科学辐射归一。",
  },
  "12_panel_reflectance": {
    method: "经验线法（ELM）白板/灰板反射率定标",
    cites: [
      paper(
        "Smith G. M., Milton E. J.",
        "1999",
        "The use of the empirical line method to calibrate remotely sensed data to reflectance",
        "International Journal of Remote Sensing, 20(13), 2653–2664",
        "https://doi.org/10.1080/014311699211994",
      ),
    ],
    note: "无人机高光谱常用现场参考板。本仓库默认 ρ板=0.6，无板时用最亮百分位代替，可能不是真板。",
  },
  "13_atmospheric_correction": {
    method: "Chavez DOS2 / COST 暗目标大气校正",
    cites: [
      paper(
        "Chavez P. S., Jr.",
        "1996",
        "Image-based atmospheric corrections — revisited and improved",
        "Photogrammetric Engineering & Remote Sensing, 62(9), 1025–1036",
        "https://static1.1.sqspcdn.com/static/f/891472/15133582/1321370214637/Chavez_P.S._1996.pdf",
      ),
    ],
    note: "DOS2 用暗目标估路径辐射，并用太阳天顶角余弦近似透过率。不是 6S/FLAASH。低空有白板时应优先走经验线（#12），不宜与 DOS2 重复扣除。",
  },
  "14_brdf_correction": {
    method: "Ross-Thick / Li-Sparse 核驱动，归一到天底（MODIS BRDF 一类）",
    cites: [
      paper(
        "Roujean J.-L., Leroy M., Deschamps P.-Y.",
        "1992",
        "A bidirectional reflectance model of the Earth's surface for the correction of remote sensing data",
        "Journal of Geophysical Research, 97(D18), 20455–20468",
        "https://doi.org/10.1029/92JD01411",
      ),
      paper(
        "Schaaf C. B., et al.",
        "2002",
        "First operational BRDF, albedo nadir reflectance products from MODIS",
        "Remote Sensing of Environment, 83(1–2), 135–148",
        "https://doi.org/10.1016/S0034-4257(02)00091-3",
      ),
    ],
    note: "本仓库核系数固定、不反演，方位角不随航迹变化，只做教学级天底归一。",
  },
  "15_geo_locate": {
    method: "POS 中心 + GSD 写入北向上仿射（粗地理定位）",
    cites: [
      paper(
        "Mostafa M. M. R., Schwarz K. P.",
        "2001",
        "Digital image georeferencing from a multiple camera system by GPS/INS",
        "ISPRS Journal of Photogrammetry and Remote Sensing, 56(1), 1–12",
        "https://doi.org/10.1016/S0924-2716(01)00030-2",
      ),
    ],
    note: "这是粗定位，忽略姿态旋转与地形。精确落图见 #16 共线方程正射。",
  },
  "16_orthorectify": {
    method: "共线方程 + DEM 直接地理定位",
    cites: [
      paper(
        "Colomina I., Molina P.",
        "2014",
        "Unmanned aerial systems for photogrammetry and remote sensing: A review",
        "ISPRS Journal of Photogrammetry and Remote Sensing, 92, 79–97",
        "https://doi.org/10.1016/j.isprsjprs.2014.02.013",
      ),
    ],
    note: "共线条件是摄影测量基本方程。Colomina & Molina 综述了无人机直接地理定位与正射。本仓库为单片路径，不是多视空三加密。",
  },
  "17_mosaic": {
    method: "按地理参考重投影，重叠区距离羽化",
    cites: [
      paper(
        "GDAL/OGR contributors",
        "2024",
        "gdalwarp — image reprojection and warping utility",
        "GDAL documentation",
        "https://gdal.org/en/stable/programs/gdalwarp.html",
      ),
      paper(
        "Li S., et al.",
        "2016",
        "Automatic mosaicking of satellite imagery considering the clouds",
        "ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences, III-3, 415–420",
        "https://isprs-annals.copernicus.org/articles/III-3/415/2016/isprs-annals-III-3-415-2016.pdf",
      ),
    ],
    note: "正射镶嵌与重投影是生产流程惯例，GDAL gdalwarp 是常用实现。本仓库不做接缝线优化。",
  },
  "18_color_balance": {
    method: "Wallis 局部自适应匀光",
    cites: [
      paper(
        "Fan C., Chen X., Zhong L., Zhou M., Shi Y., Duan Y.",
        "2017",
        "Improved Wallis Dodging Algorithm for Large-Scale Super-Resolution Reconstruction Remote Sensing Images",
        "Sensors, 17(3), 623",
        "https://doi.org/10.3390/s17030623",
      ),
      paper(
        "Li S., et al.",
        "2016",
        "Automatic mosaicking of satellite imagery considering the clouds（文中给出 Wallis 匀光公式）",
        "ISPRS Annals, III-3, 415–420",
        "https://isprs-annals.copernicus.org/articles/III-3/415/2016/isprs-annals-III-3-415-2016.pdf",
      ),
    ],
    note: "Wallis 滤波（Wallis 1976 会议文）是正射镶嵌匀光的常用手段；上列文献给出可核对的公式与改进。定量 NDVI 产品不应再过匀光。",
  },
  "19_multi_source_register": {
    method: "相位相关 + Foroosh 亚像元平移",
    cites: [
      paper(
        "Foroosh H., Zerubia J. B., Berthod M.",
        "2002",
        "Extension of phase correlation to subpixel registration",
        "IEEE Transactions on Image Processing, 11(3), 188–200",
        "https://doi.org/10.1109/83.988953",
      ),
    ],
    note: "相位相关由 Kuglin & Hines 1975 提出；本仓库按 Foroosh 等做亚像元估计，用于 HSI–RGB 平移配准。",
  },
  "20_bad_band_remove": {
    method: "SNR 阈值 + 大气吸收窗口 + 手动 drop_bands",
    cites: [
      paper(
        "Gordon I. E., et al.",
        "2017",
        "The HITRAN2016 molecular spectroscopic database",
        "Journal of Quantitative Spectroscopy and Radiative Transfer, 203, 3–69",
        "https://doi.org/10.1016/j.jqsrt.2016.06.038",
      ),
      paper(
        "HITRAN Project",
        "2024",
        "HITRAN — high-resolution transmission molecular absorption database",
        "hitran.org",
        "https://hitran.org/",
      ),
    ],
    note: "水汽吸收窗口（约 940 nm、1400 nm 等）来自大气分子光谱，HITRAN 是官方谱线库。本仓库另用相对中位 SNR 剔除坏波段。",
  },
  "21_savgol_smooth": {
    method: "Savitzky–Golay 多项式滑动平滑",
    cites: [
      paper(
        "Savitzky A., Golay M. J. E.",
        "1964",
        "Smoothing and differentiation of data by simplified least squares procedures",
        "Analytical Chemistry, 36(8), 1627–1639",
        "https://doi.org/10.1021/ac60214a047",
      ),
      paper(
        "SciPy developers",
        "2024",
        "scipy.signal.savgol_filter",
        "SciPy documentation",
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html",
      ),
    ],
    note: "光谱学经典平滑。窗口须为奇数。本仓库当前实现是 SG 平滑，不是包络线去除。",
  },
  "22_normalize": {
    method: "SNV / Z-score / MinMax / L2",
    cites: [
      paper(
        "Barnes R. J., Dhanoa M. S., Lister S. J.",
        "1989",
        "Standard Normal Variate Transformation and De-trending of Near-Infrared Diffuse Reflectance Spectra",
        "Applied Spectroscopy, 43(5), 772–777",
        "https://doi.org/10.1366/0003702894202201",
      ),
    ],
    note: "SNV 来自近红外光谱学。Z-score / MinMax / L2 是通用标准化，无单独遥感发明文。",
  },
  "23_pca": {
    method: "默认 MNF，可选 PCA",
    cites: [
      paper(
        "Green A. A., Berman M., Switzer P., Craig M. D.",
        "1988",
        "A transformation for ordering multispectral data in terms of image quality with implications for noise removal",
        "IEEE Transactions on Geoscience and Remote Sensing, 26(1), 65–74",
        "https://doi.org/10.1109/36.3001",
      ),
    ],
    note: "MNF（常称最小噪声分数）由 Green 等提出。PCA 本身是 Pearson/Hotelling 的经典线性代数方法。",
  },
  "24_band_select": {
    method: "有标签用 ANOVA F，否则用方差",
    cites: [
      paper(
        "scikit-learn developers",
        "2024",
        "sklearn.feature_selection.f_classif — ANOVA F-value",
        "scikit-learn documentation",
        "https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.f_classif.html",
      ),
    ],
    note: "方差选择与 Fisher 方差分析是统计教材内容。本仓库按是否有标签在 ANOVA F 与方差准则间切换，实现对应 sklearn 的 f_classif。",
  },
  "25_superpixel": {
    method: "SLIC",
    cites: [
      paper(
        "Achanta R., Shaji A., Smith K., Lucchi A., Fua P., Süsstrunk S.",
        "2012",
        "SLIC Superpixels Compared to State-of-the-Art Superpixel Methods",
        "IEEE Transactions on Pattern Analysis and Machine Intelligence, 34(11), 2274–2282",
        "https://doi.org/10.1109/TPAMI.2012.51",
      ),
      paper(
        "EPFL IVRL",
        "2012",
        "SLIC Superpixels（作者实验室页面，含论文与代码）",
        "École Polytechnique Fédérale de Lausanne",
        "https://www.epfl.ch/labs/ivrl/research/slic-superpixels/",
      ),
    ],
    note: "面向对象分割的常用超像素实现。",
  },
  "26_patch_build": {
    method: "按标注像素切邻域立方体",
    cites: [
      paper(
        "Roy S. K., Krishna G., Dubey S. R., Chaudhuri B. B.",
        "2020",
        "HybridSN: Exploring 3-D–2-D CNN Feature Hierarchy for Hyperspectral Image Classification",
        "IEEE Geoscience and Remote Sensing Letters, 17(2), 277–281",
        "https://arxiv.org/abs/1902.06701",
      ),
    ],
    note: "空谱 CNN 以中心像素邻域立方体为训练样本，样本构造方式见 HybridSN。这一项本身是数据准备步骤。",
  },
  "27_ndvi": {
    method: "NDVI = (NIR − RED) / (NIR + RED)",
    cites: [
      paper(
        "Rouse J. W., Haas R. H., Schell J. A., Deering D. W.",
        "1974",
        "Monitoring vegetation systems in the Great Plains with ERTS",
        "Third ERTS-1 Symposium, NASA SP-351, Vol. 1, 309–317",
        "https://ntrs.nasa.gov/citations/19740022614",
      ),
      paper(
        "Tucker C. J.",
        "1979",
        "Red and photographic infrared linear combinations for monitoring vegetation",
        "Remote Sensing of Environment, 8(2), 127–150",
        "https://doi.org/10.1016/0034-4257(79)90013-0",
      ),
    ],
    note: "Rouse 等给出 ERTS 红光/近红外比值与绿生物量的关系；Tucker 把 (NIR−RED)/(NIR+RED) 明确为植被指数并广泛使用。必须用反射率，不能用原始 DN。",
  },
  "28_ndre": {
    method: "NDRE = (NIR − RE) / (NIR + RE)",
    cites: [
      paper(
        "Barnes E. M., Clarke T. R., Richards S. E., et al.",
        "2000",
        "Coincident detection of crop water stress, nitrogen status and canopy density using ground-based multispectral data",
        "Proceedings of the 5th International Conference on Precision Agriculture, Bloomington, MN",
        "https://www.indexdatabase.de/db/r-single.php?id=642",
      ),
      paper(
        "Index DataBase",
        "2000",
        "Normalized Difference NIR/Rededge (NDRE) — 公式与 Barnes 等 2000 出处",
        "IDB",
        "https://www.indexdatabase.de/db/i-single.php?id=223",
      ),
    ],
    note: "NDRE 用红边代替红光，密冠层比 NDVI 晚饱和。公式与 NDVI 同型，波段必须是真红边，不能拿默认索引硬套。会议原文无 DOI，上列 Index Database 文献页与指数页均可打开。",
  },
  "29_evi_savi": {
    method: "EVI / SAVI / MSAVI 三指数栈",
    cites: [
      paper(
        "Huete A. R.",
        "1988",
        "A soil-adjusted vegetation index (SAVI)",
        "Remote Sensing of Environment, 25(3), 295–309",
        "https://doi.org/10.1016/0034-4257(88)90106-X",
      ),
      paper(
        "Qi J., Chehbouni A., Huete A. R., Kerr Y. H., Sorooshian S.",
        "1994",
        "A modified soil adjusted vegetation index",
        "Remote Sensing of Environment, 48(2), 119–126",
        "https://doi.org/10.1016/0034-4257(94)90134-1",
      ),
      paper(
        "Huete A., Didan K., Miura T., Rodriguez E. P., Gao X., Ferreira L. G.",
        "2002",
        "Overview of the radiometric and biophysical performance of the MODIS vegetation indices",
        "Remote Sensing of Environment, 83(1–2), 195–213",
        "https://doi.org/10.1016/S0034-4257(02)00096-2",
      ),
    ],
    note: "SAVI/MSAVI 针对土壤背景；EVI 为 MODIS 植被指数产品中的增强指数（含蓝光项）。本仓库 EVI 系数沿用 MODIS 习惯。",
  },
  "30_ndmi_ndwi": {
    method: "NDMI=(NIR−SWIR)/(NIR+SWIR)；NDWI 为 McFeeters；MNDWI 为 Xu",
    cites: [
      paper(
        "Gao B.-C.",
        "1996",
        "NDWI — A normalized difference water index for remote sensing of vegetation liquid water from space",
        "Remote Sensing of Environment, 58(3), 257–266",
        "https://doi.org/10.1016/S0034-4257(96)00067-3",
      ),
      paper(
        "McFeeters S. K.",
        "1996",
        "The use of the Normalized Difference Water Index (NDWI) in the delineation of open water features",
        "International Journal of Remote Sensing, 17(7), 1425–1432",
        "https://doi.org/10.1080/01431169608948714",
      ),
      paper(
        "Sentinel Hub",
        "2024",
        "NDWI Normalized Difference Water Index（绿光/近红外，追溯 McFeeters 1996）",
        "Sentinel Hub custom scripts",
        "https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/ndwi/",
      ),
      paper(
        "Xu H.",
        "2006",
        "Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery",
        "International Journal of Remote Sensing, 27(14), 3025–3033",
        "https://doi.org/10.1080/01431160600589179",
      ),
    ],
    note: "名称容易混：Gao 1996 的 (NIR−SWIR)/(NIR+SWIR) 在本仓库称为 NDMI；水体 NDWI 采用 McFeeters（绿光与近红外），不是 Gao 那条。MNDWI 用绿光与 SWIR。",
  },
  "31_red_edge_params": {
    method: "四点线性内插 REP + SG 一阶导数峰",
    cites: [
      paper(
        "Guyot G., Baret F.",
        "1988",
        "Utilisation de la haute résolution spectrale pour suivre l'état des couverts végétaux（红边四点线性内插）",
        "Proc. 4th International Colloquium on Spectral Signatures of Objects in Remote Sensing, ESA SP-287",
        "https://ui.adsabs.harvard.edu/abs/1988ESASP.287..279G/abstract",
      ),
      paper(
        "ESA SNAP",
        "2024",
        "REIP Algorithm Specification（官方实现页，公式追溯 Guyot & Baret 1988）",
        "ESA STEP / SNAP help",
        "https://step.esa.int/main/wp-content/help/versions/10.0.0/snap-toolboxes/eu.esa.opt.opttbx.radiometric.indices.ui/reip/ReipAlgorithmSpecification.html",
      ),
    ],
    note: "本仓库公式为 REP = 700 + 40×((R670+R780)/2 − R700)/(R740 − R700)，与 ESA SNAP REIP 页给出的 Guyot 线性内插一致。代码注释写「Guyot & Baret 1991」不准确：四点法追溯到 1988 年 ESA 会议文。",
  },
  "32_regression_inversion": {
    method: "SNV + PLS 把光谱映射为连续生化量",
    cites: [
      paper(
        "Barnes R. J., Dhanoa M. S., Lister S. J.",
        "1989",
        "Standard Normal Variate Transformation and De-trending of Near-Infrared Diffuse Reflectance Spectra",
        "Applied Spectroscopy, 43(5), 772–777",
        "https://doi.org/10.1366/0003702894202201",
      ),
      paper(
        "Wold S., Sjöström M., Eriksson L.",
        "2001",
        "PLS-regression: a basic tool of chemometrics",
        "Chemometrics and Intelligent Laboratory Systems, 58(2), 109–130",
        "https://doi.org/10.1016/S0169-7439(01)00155-1",
      ),
    ],
    note: "这是经验回归，不是辐射传输反演。需要同步实测真值。",
  },
  "33_physical_inversion": {
    method: "PROSPECT + SAIL（PROSAIL）查找表，按光谱角匹配 LAI/Cab",
    cites: [
      paper(
        "Jacquemoud S., Baret F.",
        "1990",
        "PROSPECT: A model of leaf optical properties spectra",
        "Remote Sensing of Environment, 34(2), 75–91",
        "https://doi.org/10.1016/0034-4257(90)90100-Z",
      ),
      paper(
        "Verhoef W.",
        "1984",
        "Light scattering by leaf layers with application to canopy reflectance modeling: The SAIL model",
        "Remote Sensing of Environment, 16(2), 125–141",
        "https://doi.org/10.1016/0034-4257(84)90057-9",
      ),
      paper(
        "Jacquemoud S., Verhoef W., Baret F., et al.",
        "2009",
        "PROSPECT + SAIL models: A review of use for vegetation characterization",
        "Remote Sensing of Environment, 113, S56–S66",
        "https://doi.org/10.1016/j.rse.2008.01.026",
      ),
    ],
    note: "本仓库用 PyPI `prosail` 建 LUT，再按光谱角取最近邻，不是数值优化反演全文。",
  },
  "34_svm_rf_classify": {
    method: "SVM / 随机森林像素分类",
    cites: [
      paper(
        "Cortes C., Vapnik V.",
        "1995",
        "Support-vector networks",
        "Machine Learning, 20, 273–297",
        "https://link.springer.com/article/10.1007/BF00994018",
      ),
      paper(
        "Breiman L.",
        "2001",
        "Random Forests",
        "Machine Learning, 45, 5–32",
        "https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf",
      ),
    ],
    note: "高光谱像素分类的常用基线。本仓库用 sklearn 实现，不是遥感专有分类器。",
  },
  "35_spectral_matching": {
    method: "SAM + SID",
    cites: [
      paper(
        "Kruse F. A., Lefkoff A. B., Boardman J. W., et al.",
        "1993",
        "The Spectral Image Processing System (SIPS)—interactive visualization and analysis of imaging spectrometer data",
        "Remote Sensing of Environment, 44(2–3), 145–163",
        "https://doi.org/10.1016/0034-4257(93)90013-N",
      ),
      paper(
        "Chang C.-I.",
        "2000",
        "An information-theoretic approach to spectral variability, similarity, and discrimination for hyperspectral image analysis",
        "IEEE Transactions on Information Theory, 46(5), 1927–1932",
        "https://www2.umbc.edu/rssipl/pdf/IT_2000.pdf",
      ),
    ],
    note: "SAM 用光谱角；SID 用光谱信息散度。本仓库两种都算。SID 原文 DOI 为 10.1109/18.857802；此处链接作者组开放 PDF。",
  },
  "36_cnn1d_classify": {
    method: "1-D CNN 光谱分类（Hu 2015 结构）",
    cites: [
      paper(
        "Hu W., Huang Y., Wei L., Zhang F., Li H.",
        "2015",
        "Deep Convolutional Neural Networks for Hyperspectral Image Classification",
        "Journal of Sensors, 2015, Article ID 258619",
        "https://www.semanticscholar.org/paper/Deep-Convolutional-Neural-Networks-for-Image-Hu-Huang/2369db9921078c4bb76072ef7d6426e9f1dbfdb5",
      ),
    ],
    note: "这是高光谱 1-D CNN 的常用对照结构。本仓库 model.py 注释曾写 IEEE JSTARS，经核对该文发表于 Journal of Sensors（Hindawi），DOI 为 10.1155/2015/258619。此处链接 Semantic Scholar 落地页。",
  },
  "37_cnn3d_classify": {
    method: "HybridSN（3D 卷积 + 2D 卷积）",
    cites: [
      paper(
        "Roy S. K., Krishna G., Dubey S. R., Chaudhuri B. B.",
        "2020",
        "HybridSN: Exploring 3-D–2-D CNN Feature Hierarchy for Hyperspectral Image Classification",
        "IEEE Geoscience and Remote Sensing Letters, 17(2), 277–281",
        "https://arxiv.org/abs/1902.06701",
      ),
    ],
    note: "本仓库为短训教学实现，数据与超参不是论文中的 Indian Pines 全量实验。开放预印本见 arXiv:1902.06701。",
  },
  "38_transformer_classify": {
    method: "SpectralFormer（邻域波段 token + 跨层残差）",
    cites: [
      paper(
        "Hong D., Han Z., Yao J., Gao L., Zhang B., Plaza A., Chanussot J.",
        "2022",
        "SpectralFormer: Rethinking Hyperspectral Image Classification with Transformers",
        "IEEE Transactions on Geoscience and Remote Sensing, 60, 5518615",
        "https://arxiv.org/abs/2107.02988",
      ),
    ],
    note: "本仓库是缩小通道与层数的教学结构，不能当作论文官方实现复现。期刊 DOI 为 10.1109/TGRS.2021.3130716，此处链接开放预印本。",
  },
  "39_few_shot_classify": {
    method: "原型网络 + 光谱角距离",
    cites: [
      paper(
        "Snell J., Swersky K., Zemel R.",
        "2017",
        "Prototypical Networks for Few-shot Learning",
        "Advances in Neural Information Processing Systems (NeurIPS)",
        "https://arxiv.org/abs/1703.05175",
      ),
    ],
    note: "度量用光谱角，是高光谱少样本分类的常见改法，不是 Snell 原文的欧氏距离设定。",
  },
  "40_detect_segment": {
    method: "ACE 自适应余弦估计（目标探测）",
    cites: [
      paper(
        "Kraut S., Scharf L. L.",
        "1999",
        "The CFAR adaptive subspace detector is a scale-invariant GLRT",
        "IEEE Transactions on Signal Processing, 47(9), 2538–2541",
        "https://doi.org/10.1109/78.782198",
      ),
    ],
    note: "ACE 是高光谱目标探测的标准检测器之一。本仓库清单标题含分割，实现是 ACE 得分图 + 阈值斑块，不是深度学习语义分割。",
  },
  "41_unmixing": {
    method: "FCLS 全约束最小二乘",
    cites: [
      paper(
        "Heinz D. C., Chang C.-I.",
        "2001",
        "Fully constrained least squares linear spectral mixture analysis method for material quantification in hyperspectral imagery",
        "IEEE Transactions on Geoscience and Remote Sensing, 39(3), 529–545",
        "https://www2.umbc.edu/rssipl/pdf/TGRS/01/tgrs.3_01.pdf",
      ),
    ],
    note: "丰度非负且和为 1。需要端元光谱（file2）。期刊 DOI 为 10.1109/36.911111；此处链接作者组开放 PDF。",
  },
  "42_anomaly_detect": {
    method: "Reed–Xiaoli（全局 RX）/ 局部 RX",
    cites: [
      paper(
        "Reed I. S., Yu X.",
        "1990",
        "Adaptive multiple-band CFAR detection of an optical pattern with unknown spectral distribution",
        "IEEE Transactions on Acoustics, Speech, and Signal Processing, 38(10), 1760–1770",
        "https://doi.org/10.1109/29.60107",
      ),
    ],
    note: "局部 RX 在外窗估计背景协方差。教学数据尺寸小，窗参数需相应缩小。",
  },
  "43_change_detect": {
    method: "IR-MAD",
    cites: [
      paper(
        "Nielsen A. A.",
        "2007",
        "The regularized iteratively reweighted MAD method for change detection in multi- and hyperspectral data",
        "IEEE Transactions on Image Processing, 16(2), 463–468",
        "https://www2.imm.dtu.dk/pubdb/edoc/imm4695.pdf",
      ),
    ],
    note: "需要两时相立方体。本仓库是 IR-MAD 的教学实现。期刊 DOI 为 10.1109/TIP.2006.888195；此处链接 DTU 开放 PDF。",
  },
  "44_postprocess_smooth": {
    method: "众数滤波 + 小斑剔除",
    cites: [
      paper(
        "GDAL/OGR contributors",
        "2024",
        "gdal_sieve.py — remove small raster polygons",
        "GDAL documentation",
        "https://gdal.org/en/stable/programs/gdal_sieve.html",
      ),
      paper(
        "Esri",
        "2024",
        "Majority Filter (Spatial Analyst)",
        "ArcGIS Pro tool reference",
        "https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/majority-filter.htm",
      ),
    ],
    note: "图斑整理（majority filter / sieve）是遥感数字图像处理的常规步骤。本仓库实现对应 GDAL sieve 与 ArcGIS Majority Filter 一类操作，不是某一篇指数论文。",
  },
  "45_parcel_zonal_stats": {
    method: "GeoJSON 栅格化后分区统计",
    cites: [
      paper(
        "GDAL/OGR contributors",
        "2024",
        "gdal_raster_zonal_stats — raster zonal statistics",
        "GDAL documentation",
        "https://gdal.org/en/latest/programs/gdal_raster_zonal_stats.html",
      ),
    ],
    note: "矢量转栅格再逐多边形统计是 GIS 标准操作。本仓库实现对应 GDAL zonal statistics。",
  },
};

export function getAlgoSource(id: string): AlgoSource | undefined {
  return SOURCES[id];
}
