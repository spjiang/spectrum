import { buildSourcePanelView, getAlgorithmEvidence } from "./evidence";
import type { SourcePanelView } from "./types";

/** 算法文献：每条都带可打开的 url，以及该文献自身内容的中文提要。 */

export interface Cite {
  authors: string;
  year: string;
  title: string;
  venue: string;
  url: string;
  /** 该文献实际写了什么，不是本仓库实现说明 */
  summary: string;
}

export interface AlgoSource {
  /** 本仓库实际采用的方法（与 service / METHODS 一致） */
  method: string;
  cites: Cite[];
  /** 源码计算过程相对文献算法的差异，按 1、2、3 列出；不含接口输入输出。implementation-only 契约不进此栏。 */
  diffs: string[];
}

function paper(
  authors: string,
  year: string,
  title: string,
  venue: string,
  url: string,
  summary: string,
): Cite {
  return { authors, year, title, venue, url, summary };
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
        "出版社页面核实该综述讨论无人机摄影测量与遥感中的飞行平台、传感器、导航定向及数据处理；摘要不直接规定本仓库 GSD、重叠率或航程公式。",
      ),
      paper(
        "Jiang Y.H., Zhang G., Tang X.M., Li D.R., Huang W.C., Pan H.B.（姜永华、张过、唐新明、李德仁等）",
        "2014",
        "Geometric Calibration and Accuracy Assessment of ZiYuan-3 Multispectral Images",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/tgrs.2013.2280134",
        "Crossref 核实李德仁、张过等发表资源三号多光谱几何检校与精度评估。证明国内把卫星摄影测量几何作为既有方法。题录不规定本仓库航线 GSD 或重叠率公式。",
      ),
    ],
    diffs: [
      "GSD 用航高×像元尺寸/焦距估算，不是实测地面分辨率。",
      "只在测区外包矩形上铺直线往返航点，不做 DEM、障碍或禁飞。",
      "航程按航点间距累加，不是飞控实测航迹。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "Crossref 与出版社摘要核实论文研究多相机系统、DGPS/惯导轨迹和影像外方位提取；公开摘要未给出本仓库的中位钟差、最近邻或插值容差。",
      ),
      paper(
        "Yuan X.X.（袁修孝）",
        "2000",
        "Principle, software and experiment of GPS-supported aerotriangulation",
        "Geo-spatial Information Science",
        "https://doi.org/10.1007/bf02826803",
        "Crossref 核实作者单位为武汉测绘科技大学。论文讨论 GPS 辅助空中三角测量的原理、软件与实验。公开题录未给出本仓库中位钟差或 RGB 最近邻容差。",
      ),
    ],
    diffs: [
      "中位数钟差是本仓库工程默认：取最近 RGB 时间差的中位数当作固定值，没有钟漂模型。",
      "位置线性插值、姿态最短弧插值；RGB 取最近邻，没有容差拒绝。",
      "这是软件后处理配对，不是 PPS/PTP 硬件同步。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "推导固定区间最大似然平滑，即后来所称的 RTS 平滑器：先正向卡尔曼滤波，再反向递推，用未来观测修正过去状态。适用于线性高斯动态系统。",
      ),
      paper(
        "Särkkä S.",
        "2016",
        "Lecture 7: Bayesian Smoother, Gaussian and Particle Smoothers",
        "Aalto University",
        "https://users.aalto.fi/~ssarkka/course_k2016/handout7.pdf",
        "官方课程讲义明确给出固定区间平滑、线性高斯模型和 Rauch–Tung–Striebel 后向递推公式，未涉及本仓库互补滤波与参数默认值。",
      ),
      paper(
        "Yuan X.X., Fu J.H., Sun H.X., Toth C.（袁修孝、付建红、孙红星等）",
        "2009",
        "The application of GPS precise point positioning technology in aerial triangulation",
        "ISPRS Journal of Photogrammetry and Remote Sensing",
        "https://doi.org/10.1016/j.isprsjprs.2009.03.006",
        "Crossref 核实袁修孝等把 GPS PPP 用于空中三角测量。证明国内把 GPS/POS 辅助航空定位作为既有方法。题录不是本仓库 RTS 平滑或杠杆臂公式出处。",
      ),
    ],
    diffs: [
      "位置融合是一阶互补滤波，不是 GNSS/IMU 紧组合 EKF。",
      "RTS 平滑按通道分开，过程噪声与量测噪声固定。",
      "粗差用 4×MAD 速度阈值标记。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "04_flight_qc": {
    method: "按位深判饱和 + 波段 SNR ≈ μ/σ",
    cites: [
      paper(
        "U.S. Geological Survey",
        "n.d.",
        "Landsat Collection 2 Quality Assessment Bands",
        "USGS Landsat Missions",
        "https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands",
        "USGS 官方页面说明 QA_RADSAT 指示各传感器波段是否饱和；它不规定本仓库按位深乘 0.98 或按全景比例判定复飞的阈值。",
      ),
      paper(
        "European Machine Vision Association",
        "2021",
        "EMVA Standard 1288 — Release 4.0 General",
        "EMVA",
        "https://www.emva.org/wp-content/uploads/EMVA1288General_4.0Release.pdf",
        "官方标准定义输出 SNR、信号饱和、暗信号与非均匀性，并要求均匀光源、多曝光步骤及时间/空间方差处理；不支持把任意场景全景 mean/std 当传感器 SNR。",
      ),
      paper(
        "Sun L., Hu X.Q., Xu N., Liu J.J., Zhang L.J., Rong Z.G.（孙凌、胡秀清等）",
        "2013",
        "Postlaunch Calibration of FengYun-3B MERSI Reflective Solar Bands",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/tgrs.2012.2217345",
        "Crossref 核实胡秀清等发表风云三号 MERSI 反射太阳波段发射后定标。证明国内把卫星辐射质量检校作为既有方法。题录不规定本仓库过曝阈值。",
      ),
    ],
    diffs: [
      "饱和电平由位深或数据最大值推断，不是实验室标定。",
      "过曝/欠曝用 0.98/0.02；全图均值/标准差是场景相对量，不是传感器 SNR。",
      "只按过曝比例 0.01 决定通过或复飞。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "05_cloud_shadow": {
    method: "受 Fmask 启发的简化光谱规则（无热红外与云影投影几何）",
    cites: [
      paper(
        "Zhu Z., Woodcock C. E.",
        "2012",
        "Object-based cloud and cloud shadow detection in Landsat imagery",
        "Remote Sensing of Environment, 118, 83–94",
        "https://doi.org/10.1016/j.rse.2011.10.028",
        "出版社摘要核实 Fmask 使用 Landsat TOA 反射率与亮温、云概率、云对象和云高，并按传感器观测角与太阳照明角预测和匹配云影位置。",
      ),
      paper(
        "Qiu S., He B.B., Zhu Z., Liao Z.M., Quan X.W.（邱实、何彬彬、朱哲等）",
        "2017",
        "Improving Fmask cloud and cloud shadow detection in mountainous area for Landsats 4–8 images",
        "Remote Sensing of Environment",
        "https://doi.org/10.1016/j.rse.2017.07.002",
        "Crossref 核实何彬彬等与朱哲合作改进山地 Landsat 的 Fmask 云和云影检测。证明国内把云/云影检测作为既有算法。不替代 Zhu & Woodcock 2012 作为 Fmask 原始出处，也不规定本仓库简化判据。",
      ),
    ],
    diffs: [
      "不是完整 Fmask：没有亮温，也没有云影几何匹配。",
      "云候选用可见光均值、NDVI、whiteness<0.7 等简化阈值。",
      "暗区用非云非水近红外的 15% 分位。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "06_dark_current": {
    method: "暗帧相减 + 列向固定模式噪声",
    cites: [
      paper(
        "European Machine Vision Association",
        "2021",
        "EMVA Standard 1288 — Release 4.0 General",
        "EMVA",
        "https://www.emva.org/wp-content/uploads/EMVA1288General_4.0Release.pdf",
        "官方标准分别定义暗电流、暗信号非均匀性和固定空间非均匀性，并要求记录曝光、温度与相机设置；它是表征标准，不规定场景最小值替代暗帧。",
      ),
      paper(
        "An L.P., Wang Y.H., Zhao H., Yu C., Wang Y.H., Wang S., Liu X.B.（安凌平、刘学斌等）",
        "2023",
        "Dynamic space–time dark level correction approach for lunar radiometric calibration of the Lunar Observation Imaging Spectrometer",
        "Applied Optics",
        "https://doi.org/10.1364/ao.476640",
        "Crossref 核实作者单位含中国科学院大学。论文讨论成像光谱仪暗电平时空校正。证明国内把暗场/暗电流校正作为既有步骤。题录不是本仓库逐波段最小值替代暗帧的工程默认。",
      ),
    ],
    diffs: [
      "无暗帧时用每波段全图最小值代替暗电流，没有温度或积分时间模型。",
      "列固定噪声用列均值相对全局均值扣除，并截到非负。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "07_bad_pixel": {
    method: "残差超 6σ 检测热/死像元后邻域填充",
    cites: [
      paper(
        "European Machine Vision Association",
        "2021",
        "EMVA Standard 1288 — Release 4.0 General",
        "EMVA",
        "https://www.emva.org/wp-content/uploads/EMVA1288General_4.0Release.pdf",
        "官方标准第 8.8 节表征缺陷像元，并要求受控测量和报告；它不规定本仓库 6σ/4σ 门限，也不规定 3×3 邻域均值修复。",
      ),
      paper(
        "Shen H.F., Zhang L.P.（沈焕锋、张良培）",
        "2009",
        "A MAP-Based Algorithm for Destriping and Inpainting of Remotely Sensed Images",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/tgrs.2008.2005780",
        "Crossref 核实沈焕锋、张良培发表遥感影像 MAP 去条带与填补。填补对应坏像元/缺失像元修复这一类问题。题录不是本仓库 6σ/4σ 检测阈值。",
      ),
    ],
    diffs: [
      "6σ/4σ 与邻域均值填充是本仓库工程默认，不是 EMVA 标准阈值。",
      "坏点用 3×3 邻域均值填充，没有出厂坏元表。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "08_destriping": {
    method: "列向矩匹配去条带",
    cites: [
      paper(
        "Gadallah F. L., Csillag F., Smith E. J. M.",
        "2000",
        "Destriping multisensor imagery with moment matching",
        "International Journal of Remote Sensing, 21(12), 2505–2511",
        "https://doi.org/10.1080/01431160050030592",
        "Taylor & Francis 页面核实作者、题名、年份及摘要：传感器间变化产生条带，所提算法匹配各传感器增益和偏置，并讨论统计相似假设与离群值。",
      ),
    ],
    diffs: [
      "沿列做矩匹配去条带；真实沿轨地物纹理可能被轻微改变。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "说明成像光谱仪关键石（keystone）畸变：同一空间列上不同波长落在不同像元。给出从飞行数据互相关估计空间错位、再重采样校正的方法。",
      ),
      paper(
        "Green R. O., et al.",
        "1998",
        "Imaging spectroscopy and the Airborne Visible/Infrared Imaging Spectrometer (AVIRIS)",
        "Remote Sensing of Environment, 65(3), 227–248",
        "https://doi.org/10.1016/S0034-4257(98)00064-9",
        "Crossref 与 NASA NTRS 核实题名、作者组和 1998 年；公开摘要说明 AVIRIS 的连续光谱成像与校准辐亮度背景，不作为本仓库 smile 互相关公式的依据。",
      ),
      paper(
        "Zhang X.L., Yu K., Zhang J.（张晓龙、于琨、张俊）",
        "2017",
        "Study on imaging spectrometer with smile and keystone eliminated",
        "Optics Communications",
        "https://doi.org/10.1016/j.optcom.2016.11.048",
        "Crossref 核实题名研究成像光谱仪 smile 与 keystone 消除。证明该方法在国内光学工程文献中作为既有问题处理。公开题录未列单位，也不能核对本仓库互相关估计公式。",
      ),
    ],
    diffs: [
      "用场景互相关估计微笑和关键石，没有实验室波长查找表。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "10_radiance_calibration": {
    method: "逐波段 L = gain × DN + offset",
    cites: [
      paper(
        "U.S. Geological Survey",
        "n.d.",
        "Using the USGS Landsat Level-1 Data Product",
        "USGS Landsat Missions",
        "https://www.usgs.gov/landsat-missions/using-usgs-landsat-level-1-data-product",
        "USGS 官方页面给出 Lλ=M_LQcal+A_L，并明确 M_L、A_L 是元数据中的逐波段辐射缩放系数，Qcal 是量化且已校准的 DN。",
      ),
    ],
    diffs: [
      "默认 gain=0.01、offset=0 是本仓库工程默认，只是演示缺省，成功运行不能证明系数来自实验室。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "11_relative_radiometric": {
    method: "逐波段直方图匹配",
    cites: [
      paper(
        "scikit-image developers",
        "n.d.",
        "Histogram matching",
        "scikit-image documentation",
        "https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_histogram_matching.html",
        "官方示例说明该操作调整输入像元以匹配参考直方图，多通道独立匹配，可作不同来源或照明条件下的轻量归一；未声称物理辐射定标。",
      ),
      paper(
        "Chen Y.P.（陈叶培）",
        "2018",
        "Improved relative radiometric normalization method of remote sensing images for change detection",
        "Journal of Applied Remote Sensing",
        "https://doi.org/10.1117/1.jrs.12.045018",
        "Crossref 核实作者单位为武汉大学测绘遥感信息工程国家重点实验室。论文改进相对辐射归一用于变化检测。题录不是直方图匹配文档，也不支持本仓库左上角裁切。",
      ),
    ],
    diffs: [
      "直方图匹配只为镶嵌观感一致，不能当定量反演前的辐射归一。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "12_panel_reflectance": {
    method: "经验线法（ELM）白板/灰板反射率定标",
    cites: [
      paper(
        "Smith G. M., Milton E. J.",
        "1999",
        "The use of the empirical line method to calibrate remotely sensed data to reflectance",
        "International Journal of Remote Sensing, 20(13), 2653–2662",
        "https://doi.org/10.1080/014311699211994",
        "用现场已知反射率的参考板，把遥感 DN 或辐亮度线性回归到地表反射率，即经验线法（ELM）。讨论最少需要几块板、线性假设何时失效。",
      ),
      paper(
        "Jia G.R., Xue Q., Zhao H.J.（贾国瑞、薛倩、赵慧洁）",
        "2018",
        "Uncertainty Analysis for Surface Reflectance Retrieved from Hyperspectral Remote Sensing Image using Empirical Line Method",
        "2018 9th Workshop on Hyperspectral Image and Signal Processing: Evolution in Remote Sensing (WHISPERS)",
        "https://doi.org/10.1109/whispers.2018.8747131",
        "Crossref 核实北航精密光电测试技术实验室用经验线性法从高光谱影像反演地表反射率并做不确定度分析。证明国内把经验线性/参考板定标作为既有方法。这是会议论文，不能当作 Smith & Milton 1999 的替代出处。",
      ),
    ],
    diffs: [
      "默认板反射率 0.6；没有板时用最亮百分位代替，可能不是真板。",
      "反射率截断到 0～1.5。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "改进基于影像的大气校正：用暗目标估路径辐射（DOS），再用太阳天顶角余弦近似透过率（COST/DOS2）。无需同步气象探空，适合历史 Landsat。",
      ),
      paper(
        "Liang S., Fang H., Chen M.（梁顺林等）",
        "2001",
        "Atmospheric correction of Landsat ETM+ land surface imagery. I. Methods",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/36.964986",
        "Crossref 核实梁顺林等发表 Landsat ETM+ 大气校正方法。梁顺林后在北京师范大学持续开展定量遥感。题录不是 Chavez DOS 公式出处，也不规定本仓库暗目标假设。",
      ),
    ],
    diffs: [
      "实现是 DOS2：暗目标估路径辐射，太阳天顶角余弦近似透过率，不是 6S/FLAASH。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出核驱动二向反射模型：把地表 BRDF 写成各向同性、体积散射（Ross）与几何光学（Li）核的线性组合，用于把观测几何归一到可比条件。",
      ),
      paper(
        "Schaaf C. B., et al.",
        "2002",
        "First operational BRDF, albedo nadir reflectance products from MODIS",
        "Remote Sensing of Environment, 83(1–2), 135–148",
        "https://doi.org/10.1016/S0034-4257(02)00091-3",
        "介绍 MODIS 业务化 BRDF/反照率产品：用核驱动模型拟合多角度观测，输出天底反射率与黑空/白空反照率。是后续 Ross-Thick / Li-Sparse 应用的产品依据。",
      ),
      paper(
        "Li X., Strahler A.H.（李小文、Strahler）",
        "1992",
        "Geometric-optical bidirectional reflectance modeling of the discrete crown vegetation canopy: effect of crown shape and mutual shadowing",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/36.134078",
        "Crossref 核实李小文与 Strahler 发表离散冠层几何光学双向反射模型。李小文为中国科学院/北京师范大学学者，该文是国内 BRDF 研究的经典贡献。不替代 Roujean 核驱动模型作为本仓库对照出处。",
      ),
    ],
    diffs: [
      "核系数固定、不反演；方位角不随航迹变化，只做天底归一（核系数固定）。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "出版社题录核实该文使用 DGPS/INS 完整平移与旋转轨迹、相机标定和影像外方位进行直接地理定位；它只作为完整方法背景，不支持本仓库中心点加 GSD 的粗仿射。",
      ),
    ],
    diffs: [
      "只用单个 POS 中心点和 GSD 写北向上仿射，不使用姿态。",
      "GSD 按航高×像元尺寸/焦距估算。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "综述无人机摄影测量与遥感：航高、地面采样间距（GSD）、航带重叠、直接地理定位与空中三角测量。给出测区规划时分辨率与覆盖如何由相机焦距、像元尺寸和飞行高度决定。",
      ),
      paper(
        "Belfiore O. R., Parente C.",
        "2016",
        "Comparison of Different Algorithms to Orthorectify WorldView-2 Satellite Imagery",
        "Algorithms, 9(4), 67",
        "https://doi.org/10.3390/a9040067",
        "出版社全文明确说明严格物理模型以共线方程连接像点和地面坐标，并比较结合 GCP、检查点与 DEM 的正射流程。",
      ),
      paper(
        "Zhang J.Q., Zhang Z.X., Wu X.L., Wang Z.H., Qiu T., Cao H.（张剑清、张祖勋等）",
        "1994",
        "Photogrammetric workstation from Wuhan Technical University of Surveying and Mapping (WTUSM)",
        "SPIE Proceedings",
        "https://doi.org/10.1117/12.182886",
        "Crossref 核实张祖勋、张剑清等介绍武汉测绘科技大学数字摄影测量工作站。证明国内把数字摄影测量与正射相关流程作为既有能力。这是会议文，不规定本仓库相机模型或 DEM 正射公式。",
      ),
    ],
    diffs: [
      "单组姿态加演示 DEM 反投影，未用 DEM 坐标系、真实地图格网或控制点。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "GDAL 重投影与重采样工具说明：按目标坐标系与分辨率把栅格 warp 到统一网格，可选重采样核与无数据值。正射镶嵌前常用它把各景落到同一参考。",
      ),
      paper(
        "Kang Y., Pan L., Chen Q., Zhang T., Zhang S., Liu Z.",
        "2016",
        "AUTOMATIC MOSAICKING OF SATELLITE IMAGERY CONSIDERING THE CLOUDS",
        "ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences, III-3, 415–421",
        "https://isprs-annals.copernicus.org/articles/III-3/415/2016/",
        "卫星影像自动镶嵌流程：顾及云量选片、重叠区处理，并写出 Wallis 匀光公式，使相邻景色调接近后再拼接。开放获取的会议全文。",
      ),
      paper(
        "Nie P., Cui Z., Wan Y.",
        "2023",
        "A Rapid Parallel Mosaicking Algorithm for Massive Remote Sensing Images Utilizing Read Filtering",
        "Remote Sensing, 15(19), 4863",
        "https://doi.org/10.3390/rs15194863",
        "出版社全文把重叠过渡区写成距离加权组合并给出余弦距离权重；仓库采用影像边缘距离，不是该文的接缝缓冲余弦权重。",
      ),
    ],
    diffs: [
      "只接受同一坐标系的两景，否则拒绝。",
      "用影像边缘距离羽化，不做接缝线、空值掩膜或辐射归一。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "针对大幅面遥感超分重建后的色调不均，改进 Wallis 匀光：用局部均值/方差把子块拉向全局目标，减少镶嵌接缝处的明暗跳变。",
      ),
      paper(
        "Kang Y., Pan L., Chen Q., Zhang T., Zhang S., Liu Z.",
        "2016",
        "AUTOMATIC MOSAICKING OF SATELLITE IMAGERY CONSIDERING THE CLOUDS",
        "ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences, III-3, 415–421",
        "https://isprs-annals.copernicus.org/articles/III-3/415/2016/",
        "卫星影像自动镶嵌流程：顾及云量选片、重叠区处理，并写出 Wallis 匀光公式，使相邻景色调接近后再拼接。开放获取的会议全文。",
      ),
      paper(
        "Wallis R. H.",
        "1976",
        "An Approach to the Space Variant Restoration and Enhancement of Images",
        "Symposium on Current Mathematical Problems in Image Science, Naval Postgraduate School, Monterey",
        "https://www.scirp.org/reference/referencespapers?referenceid=2051743",
        "可访问题录核实 Wallis 1976 方法名称、作者、年份和会议；公式支持以 Fan 2017 与 ISPRS 开放全文为准。",
      ),
    ],
    diffs: [
      "匀光用 Wallis 滤波；定量植被指数产品不应再过这一步。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "把相位相关从整像素推广到亚像素：利用归一化互功率谱在峰值附近的解析性质估计亚像元平移，用于多源影像配准。",
      ),
    ],
    diffs: [
      "相位相关只估计亚像元平移，不做非线性变形。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "20_bad_band_remove": {
    method: "场景像元均值/标准差比 + 大气吸收窗口 + 手动 drop_bands",
    cites: [
      paper(
        "Gordon I. E., et al.",
        "2017",
        "The HITRAN2016 molecular spectroscopic database",
        "Journal of Quantitative Spectroscopy and Radiative Transfer, 203, 3–69",
        "https://doi.org/10.1016/j.jqsrt.2017.06.038",
        "出版社页面核实 HITRAN2016 汇编分子谱线、吸收截面等参数；正确 DOI 年份段为 2017.06。它不直接规定仓库固定窗口或坏波段阈值。",
      ),
      paper(
        "HITRAN Project",
        "2024",
        "HITRAN — high-resolution transmission molecular absorption database",
        "hitran.org",
        "https://hitran.org/",
        "HITRAN 官方站点：可查询高分辨率分子吸收线，确认近红外/短波红外水汽吸收带（如约 940 nm、1400 nm）的位置与强度。",
      ),
      paper(
        "Li X., Zhang B., Tong Q.X., Zhang W.J.（李星、张兵、童庆禧等）",
        "2005",
        "Demand-oriented hyperspectral database and its applications",
        "Proceedings. 2005 IEEE International Geoscience and Remote Sensing Symposium",
        "https://doi.org/10.1109/igarss.2005.1526528",
        "Crossref 核实张兵、童庆禧等介绍面向需求的高光谱数据库及其应用。证明国内高光谱处理包含波段组织与取舍。这是 IGARSS 会议文，不是 HITRAN 吸收线数据库，也不规定本仓库坏波段规则。",
      ),
    ],
    diffs: [
      "名叫 snr_per_band，实际是场景像元均值除以标准差，不是传感器 SNR。",
      "按低于中位数 0.4 倍筛选，并至少保留两波段。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出 Savitzky–Golay：在滑动窗口内做多项式最小二乘，同时得到平滑值与导数。光谱学里用来压噪声、求红边一阶导，窗口须为奇数。",
      ),
      paper(
        "SciPy developers",
        "2024",
        "scipy.signal.savgol_filter",
        "SciPy documentation",
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html",
        "SciPy 对 SG 滤波的实现说明：参数 window_length、polyorder 及 deriv。本仓库光谱平滑直接调用这一接口。",
      ),
      paper(
        "Xie J., Pan T., Chen J.M., Chen H.Z., Ren X.H.（谢军、潘涛等）",
        "2010",
        "Joint Optimization of Savitzky-Golay Smoothing Models and Partial Least Squares Factors for Near-infrared Spectroscopic Analysis of Serum Glucose",
        "分析化学 / CHINESE JOURNAL OF ANALYTICAL CHEMISTRY",
        "https://doi.org/10.3724/sp.j.1096.2010.00342",
        "Crossref 核实《分析化学》发表近红外 Savitzky–Golay 平滑与 PLS 因子联合优化。证明 SG 平滑在国内光谱分析中作为既有预处理。不替代 Savitzky & Golay 1964 作为公式出处。",
      ),
    ],
    diffs: [
      "只做 Savitzky–Golay 平滑，不是包络线去除。",
      "窗口必须是奇数。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出标准正态变量变换（SNV）：每条近红外漫反射光谱减去自身均值再除以标准差，减轻光程与散射差异；并可与去趋势联用。",
      ),
    ],
    diffs: [
      "SNV 之外的 Z-score、MinMax、L2 是通用标准化。",
      "整景拟合后再切分会泄漏；归一化会改变物理量纲。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出按图像质量排序多光谱数据的变换（后称 MNF/最小噪声分数）：先用噪声协方差白化，再做主成分，使前面分量信噪比最高，用于降噪与降维。",
      ),
      paper(
        "Zhang B., Zhuang L.N., Gao L.R., Luo W.F., Ran Q., Du Q.（张兵、高连如、罗文斐等）",
        "2014",
        "PSO-EM: A Hyperspectral Unmixing Algorithm Based On Normal Compositional Model",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/tgrs.2014.2319337",
        "Crossref 核实张兵、高连如等发表高光谱解混算法。证明中科院团队把高光谱降维与分解作为既有方法。题录侧重解混，不能当作 Green 等 MNF 公式出处。",
      ),
    ],
    diffs: [
      "可选 PCA 或 MNF；PCA 不是 Green 的最小噪声分数本身。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "sklearn 文档：用类别标签对每个特征做 ANOVA F 检验，F 越大说明该波段在类间更可分。有监督波段选择的标准实现。",
      ),
      paper(
        "Su H.J., Du P.J., Du Q.（苏红军、杜培军、杜谦）",
        "2012",
        "Hierarchical band clustering for hyperspectral image analysis",
        "7th IAPR Workshop on Pattern Recognition in Remote Sensing (PRRS)",
        "https://doi.org/10.1109/pprs.2012.6398316",
        "Crossref 核实杜培军等发表高光谱分层波段聚集。证明国内把波段选择/聚集作为既有分析步骤。这是研讨会论文，不是 scikit-learn ANOVA 文档，也不规定本仓库默认波段数。",
      ),
    ],
    diffs: [
      "有标签用 ANOVA F，无标签或无效标签退回方差法。",
      "单变量准则不控制波段冗余。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "25_superpixel": {
    method: "SLIC",
    cites: [
      paper(
        "Achanta R., Shaji A., Smith K., Lucchi A., Fua P., Süsstrunk S.",
        "2012",
        "SLIC Superpixels Compared to State-of-the-Art Superpixel Methods",
        "IEEE Transactions on Pattern Analysis and Machine Intelligence, 34(11), 2274–2282",
        "https://doi.org/10.1109/TPAMI.2012.120",
        "提出 SLIC 超像素：在五维 CIELAB+xy 空间做局部 k-means，生成紧凑、近均匀的超像素，并与当时主流方法比边界贴合与速度。",
      ),
      paper(
        "EPFL IVRL",
        "2012",
        "SLIC Superpixels（作者实验室页面，含论文与代码）",
        "École Polytechnique Fédérale de Lausanne",
        "https://www.epfl.ch/labs/ivrl/research/slic-superpixels/",
        "作者实验室页面：提供 SLIC 论文、补充材料与参考实现入口，便于对照超像素算法而不是只看二次转述。",
      ),
      paper(
        "Fu W., Li S.T., Fang L.Y., Kang X.D., Benediktsson J.A.（付伟、李树涛、方乐缘等）",
        "2014",
        "Spectral-spatial hyperspectral classification via shape-adaptive sparse representation",
        "2014 IEEE Geoscience and Remote Sensing Symposium",
        "https://doi.org/10.1109/igarss.2014.6947219",
        "Crossref 核实李树涛、方乐缘等发表基于形状自适应稀疏表示的高光谱空谱分类。证明国内把空间对象/自适应邻域作为既有思路。题录不是 Achanta SLIC 公式出处。",
      ),
    ],
    diffs: [
      "原论文用 CIELAB 加平面坐标；本仓库取前三个原始光谱波段，并且 convert2lab=false。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出 HybridSN：先用 3-D 卷积提取空谱局部特征，再用 2-D 卷积压空间，输入是中心像素的邻域立方体。Indian Pines 等基准上高于当时纯 2-D/3-D CNN。",
      ),
      paper(
        "Hu W., Huang Y., Wei L., Zhang F., Li H.C.（胡伟、黄杨雨等）",
        "2015",
        "Deep Convolutional Neural Networks for Hyperspectral Image Classification",
        "Journal of Sensors, 2015, Article 258619",
        "https://doi.org/10.1155/2015/258619",
        "Crossref 核实作者单位为北京化工大学。论文用一维 CNN 对高光谱像元光谱分类。证明国内把像元/样本输入的深度学习分类作为既有方法。不替代 HybridSN 作为本仓库 3D 补丁对照。",
      ),
    ],
    diffs: [
      "只对标签大于 0 的像元切奇数窗口样本，边界用 edge 填充。",
      "这一项只构造训练块，不训练网络。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "27_ndvi": {
    method: "NDVI = (NIR − RED) / (NIR + RED)",
    cites: [
      paper(
        "Knipling E. B.",
        "1970",
        "Physical and physiological basis for the reflectance of visible and near-infrared radiation from vegetation",
        "Remote Sensing of Environment, 1(3), 155–159",
        "https://doi.org/10.1016/S0034-4257(70)80021-9",
        "说明叶片在可见光因叶绿素吸收而反射低，在近红外因内部散射、几乎无吸收而反射高；1.3 μm 以外则受水分吸收。冠层反射还受入射光、叶面积、阴影和背景影响。",
      ),
      paper(
        "Rouse J. W., Haas R. H., Schell J. A., Deering D. W.",
        "1973",
        "Monitoring the vernal advancement and retrogradation (green wave effect) of natural vegetation",
        "NASA-CR-132982（Texas A&M / NASA GSFC 项目报告，1973-04）",
        "https://ntrs.nasa.gov/api/citations/19730017588/downloads/19730017588.pdf",
        "NASA 项目报告：用 ERTS-1 MSS 监测北美大平原天然植被的春季推进与秋季消退（绿波）。比较多种红光/近红外波段组合，为后来的归一化差植被指数做实地铺垫。",
      ),
      paper(
        "Rouse J. W., Haas R. H., Schell J. A., Deering D. W.",
        "1974",
        "Monitoring vegetation systems in the Great Plains with ERTS",
        "Third ERTS-1 Symposium, NASA SP-351, Vol. 1, 309–317",
        "https://ntrs.nasa.gov/api/citations/19740022614/downloads/19740022614.pdf",
        "写出波段比参数 BRP=(MSS7−MSS5)/(MSS7+MSS5)，再开方加 0.5 得到 TVI。现在通称的 NDVI 即未变换的 BRP。MSS5 约 0.6–0.7 μm，MSS7 约 0.8–1.1 μm。",
      ),
      paper(
        "Tucker C. J.",
        "1979",
        "Red and photographic infrared linear combinations for monitoring vegetation",
        "Remote Sensing of Environment, 8(2), 127–150",
        "https://doi.org/10.1016/0034-4257(79)90013-0",
        "比较红光 0.63–0.69 μm 与摄影红外 0.75–0.80 μm 的差值、比值、归一化差等与绿叶生物量的关系。归一化差即 (IR−red)/(IR+red)。",
      ),
      paper(
        "Huete A. R.",
        "1988",
        "A soil-adjusted vegetation index (SAVI)",
        "Remote Sensing of Environment, 25(3), 295–309",
        "https://doi.org/10.1016/0034-4257(88)90106-X",
        "证明红–近红外植被指数受土壤亮度影响：同一覆盖度下不同土壤背景会改变 NDVI。因此不能把裸土 NDVI 写成固定接近零。",
      ),
      paper(
        "Carlson T. N., Ripley D. A.",
        "1997",
        "On the relation between NDVI, fractional vegetation cover, and leaf area index",
        "Remote Sensing of Environment, 62(3), 241–252",
        "https://doi.org/10.1016/S0034-4257(97)00104-1",
        "分析 NDVI 与植被覆盖度和叶面积指数的关系，说明高叶面积时 NDVI 对 LAI 增量不敏感（饱和）。",
      ),
      paper(
        "U.S. Geological Survey",
        "2024",
        "Landsat Normalized Difference Vegetation Index",
        "USGS Landsat Missions",
        "https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index",
        "官方产品说明：NDVI 用于量化植被绿度，并有助于理解覆盖密度和植物健康变化。公式为 (NIR−R)/(NIR+R)。产品由 Landsat Level-2 地表反射率生成，不是 DN。",
      ),
      paper(
        "U.S. Geological Survey",
        "2024",
        "What are the band designations for the Landsat satellites?",
        "USGS Landsat Missions",
        "https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites",
        "Landsat 4–5 TM：Band 3 红光 0.63–0.69 μm（630–690 nm），Band 4 近红外 0.76–0.90 μm（760–900 nm）。页上红光/近红外窗口与此对齐。",
      ),
      paper(
        "Piao S.L., Fang J.Y., Zhou L.M., Guo Q.H., Henderson M., Ji W., Li Y., Tao S.（朴世龙、方精云等）",
        "2003",
        "Interannual variations of monthly and seasonal normalized difference vegetation index (NDVI) in China from 1982 to 1999",
        "Journal of Geophysical Research: Atmospheres",
        "https://doi.org/10.1029/2002JD002848",
        "Crossref 核实朴世龙、方精云等（北京大学）用 NDVI 分析 1982–1999 年中国植被年际变化。证明国内把 NDVI 作为既有指数。不替代 Rouse/Tucker 作为公式出处。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零，不是 USGS 公式的一部分。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "Index Database 文献页：著录 Barnes 等 2000 年精准农业会议文。该文用地面多光谱同时探测作物水分胁迫、氮素与冠层密度，其中用到近红外与红边的归一化差。此处是题录，不是会议全文 PDF。",
      ),
      paper(
        "Gitelson A. A., Merzlyak M. N., Lichtenthaler H. K.",
        "1996",
        "Detection of Red Edge Position and Chlorophyll Content by Reflectance Measurements Near 700 nm",
        "Journal of Plant Physiology, 148(3–4), 501–508",
        "https://doi.org/10.1016/S0176-1617(96)80285-9",
        "用叶片高光谱反射证明红边（约 680–750 nm）位置与叶绿素含量相关：约 700 nm 反射对叶绿素变化敏感，近红外约 750 nm 相对稳定，并提出比值 R750/R700。为用红边代替红光提供光谱机制，不是 Barnes 的 NDRE 归一化差公式。",
      ),
      paper(
        "Index DataBase",
        "2000",
        "Normalized Difference NIR/Rededge (NDRE) — 公式与 Barnes 等 2000 出处",
        "IDB",
        "https://www.indexdatabase.de/db/i-single.php?id=223",
        "指数目录页：给出 NDRE=(NIR−RedEdge)/(NIR+RedEdge) 的公式、波段定义，并指向 Barnes 等 2000 为出处。用于核对名称与公式，不是方法推导论文。",
      ),
      paper(
        "Yao X., Zhu Y., Tian Y.C., Feng W., Cao W.X.（姚霞、朱艳、田永超、冯伟、曹卫星）",
        "2010",
        "Exploring hyperspectral bands and estimation indices for leaf nitrogen accumulation in wheat",
        "International Journal of Applied Earth Observation and Geoinformation",
        "https://doi.org/10.1016/j.jag.2009.11.008",
        "Crossref 核实南京农业大学姚霞等探索小麦叶片氮积累的高光谱波段与估算指数。证明国内把红边相关指数作为既有方法。公开题录不能核对本仓库 NDRE 公式是否与 Barnes 等完全相同。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零。",
      "Barnes 2000 原文未直接复核，当前公式保持 qualified，仅由 Index Database 辅助核对。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "29_evi_savi": {
    method: "EVI=2.5(N−R)/(N+6R−7.5B+1)；SAVI=(1+L)(N−R)/(N+R+L)；MSAVI=0.5(2N+1−√((2N+1)²−8(N−R)))",
    cites: [
      paper(
        "Huete A. R.",
        "1988",
        "A soil-adjusted vegetation index (SAVI)",
        "Remote Sensing of Environment, 25(3), 295–309",
        "https://doi.org/10.1016/0034-4257(88)90106-X",
        "提出土壤调节植被指数 SAVI：在 NDVI 分母中加入土壤调节因子 L，减轻裸土亮度对植被指数的影响。给出 L 的典型取值与田间验证。",
      ),
      paper(
        "Qi J., Chehbouni A., Huete A. R., Kerr Y. H., Sorooshian S.",
        "1994",
        "A modified soil adjusted vegetation index",
        "Remote Sensing of Environment, 48(2), 119–126",
        "https://doi.org/10.1016/0034-4257(94)90134-1",
        "提出修正土壤调节植被指数 MSAVI：让土壤调节项随植被覆盖自适应，减少 SAVI 中人为固定 L 的偏差，改善稀疏植被下的土壤噪声。",
      ),
      paper(
        "Huete A., Didan K., Miura T., Rodriguez E. P., Gao X., Ferreira L. G.",
        "2002",
        "Overview of the radiometric and biophysical performance of the MODIS vegetation indices",
        "Remote Sensing of Environment, 83(1–2), 195–213",
        "https://doi.org/10.1016/S0034-4257(02)00096-2",
        "评述 MODIS 植被指数产品：NDVI 与增强植被指数 EVI 的辐射性能与生物物理含义。EVI 引入蓝光项和增益系数，减轻大气与土壤背景，密冠层比 NDVI 晚饱和。",
      ),
    ],
    diffs: [
      "EVI 的增益和大气项系数沿用 MODIS 习惯，不是按本传感器重新标定。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "Gao 提出用近红外与短波红外的归一化差探测植被冠层液态水，原文也叫 NDWI。本仓库按后来习惯称其为 NDMI，避免与水体指数同名。",
      ),
      paper(
        "McFeeters S. K.",
        "1996",
        "The use of the Normalized Difference Water Index (NDWI) in the delineation of open water features",
        "International Journal of Remote Sensing, 17(7), 1425–1432",
        "https://doi.org/10.1080/01431169608948714",
        "McFeeters 用绿光与近红外的归一化差圈定开阔水体，即现在常用的水体 NDWI。与 Gao 的植被水分指数同名不同波段。",
      ),
      paper(
        "Xu H.",
        "2006",
        "Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery",
        "International Journal of Remote Sensing, 27(14), 3025–3033",
        "https://doi.org/10.1080/01431160600589179",
        "徐涵秋提出 MNDWI：把 McFeeters NDWI 的近红外换成短波红外，增强开阔水体、压制建筑物与阴影，适合城市周边水体提取。",
      ),
    ],
    diffs: [
      "Gao 的近红外与短波红外归一化差，本仓库叫 NDMI，不叫 NDWI。",
      "水体 NDWI 用 McFeeters 的绿光与近红外；MNDWI 用绿光与短波红外。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "Guyot 与 Baret 在 ESA 光谱特征讨论会上提出用红边四点线性内插估计红边位置（REP），以高光谱分辨率跟踪植被长势。ADS 页是题录与摘要入口。",
      ),
      paper(
        "ESA SNAP",
        "2024",
        "REIP Algorithm Specification（官方实现页，公式追溯 Guyot & Baret 1988）",
        "ESA STEP / SNAP help",
        "https://step.esa.int/main/wp-content/help/versions/10.0.0/snap-toolboxes/eu.esa.opt.opttbx.radiometric.indices.ui/reip/ReipAlgorithmSpecification.html",
        "ESA SNAP 的 REIP 算法说明：写出四点线性内插公式 REP=700+40×((R670+R780)/2−R700)/(R740−R700)，并注明追溯 Guyot & Baret 1988。",
      ),
      paper(
        "Tian Y.C., Yang J., Yao X., Zhu Y., Cao W.X.（田永超、杨杰、姚霞、朱艳、曹卫星）",
        "2009",
        "Quantitative Relationship between Hyper-Spectral Red Edge Position and Canopy Leaf Nitrogen Concentration in Rice（水稻高光谱红边位置与冠层叶片氮浓度的定量关系）",
        "作物学报 / ACTA AGRONOMICA SINICA, 35(9), 1681–1690",
        "https://doi.org/10.3724/sp.j.1006.2009.01681",
        "Crossref 核实：作物学报发表水稻高光谱红边位置与冠层叶片氮浓度的定量关系。参考文献包含 Horler、Dawson、Cho、Filella、Miller、Curran 等红边提取文献，说明国内把红边位置当作既有算法用于氮营养研究。公开题录未核全文公式，不能证明其采用本仓库 Guyot 四点。",
      ),
      paper(
        "Liu L.Y., Wang J.H., Huang W.J., Zhao C.J., Zhang B., Tong Q.X.（刘良云、王纪华、黄文江、赵春江、张兵、童庆禧）",
        "2004",
        "Estimating winter wheat plant water content using red edge parameters",
        "International Journal of Remote Sensing, 25(17), 3331–3342",
        "https://doi.org/10.1080/01431160310001654365",
        "Crossref 核实作者单位为国家农业信息化工程技术研究中心与中国科学院遥感应用研究所。论文题名用红边参数估算冬小麦植株水分，表明国内团队将红边参数作为作物监测算法。公开题录未给出与 Guyot 四点完全相同的公式。",
      ),
      paper(
        "Chen X.Y., Zhu J.J., Wu B.F., Du X., Meng J.H.（陈学洋、朱建军、吴炳方、杜鑫、蒙继华）",
        "2011",
        "基于HJ星高光谱数据红边参数的冬小麦叶面积指数反演",
        "中国科学：信息科学 / SCIENTIA SINICA Informationis",
        "https://doi.org/10.1360/zf2011-41-suppl-213",
        "Crossref 核实中文题名：用环境减灾星高光谱的红边参数反演冬小麦叶面积指数。表明国内把红边参数用于国产星数据的农情反演。题录不能核对本仓库三条输出公式。",
      ),
    ],
    diffs: [
      "红边位置用 670/700/740/780 nm 四点线性内插，不拟合整条红边。",
      "国内文献证明红边参数在国内农情遥感中被使用，不替代 Guyot 1988 作为四点公式出处。",
    ],
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
        "提出标准正态变量变换（SNV）：每条近红外漫反射光谱减去自身均值再除以标准差，减轻光程与散射差异；并可与去趋势联用。",
      ),
      paper(
        "Wold S., Sjöström M., Eriksson L.",
        "2001",
        "PLS-regression: a basic tool of chemometrics",
        "Chemometrics and Intelligent Laboratory Systems, 58(2), 109–130",
        "https://doi.org/10.1016/S0169-7439(01)00155-1",
        "综述偏最小二乘回归（PLS）：在光谱高度共线时把自变量投影到潜变量再回归，是化学计量学把近红外/高光谱映射到浓度或生化量的基本工具。",
      ),
      paper(
        "Xue L.H., Cao W.X., Luo W.H., Dai T.B., Zhu Y.（薛利红、曹卫星、罗卫红、戴廷波、朱艳）",
        "2004",
        "Monitoring Leaf Nitrogen Status in Rice with Canopy Spectral Reflectance",
        "Agronomy Journal",
        "https://doi.org/10.2134/agronj2004.0135",
        "Crossref 核实南京农业大学薛利红、曹卫星等用冠层光谱反射率监测水稻叶片氮素。证明国内把经验光谱反演作为既有方法。题录不是 PLS 公式出处。",
      ),
    ],
    diffs: [
      "这是经验回归，不是辐射传输反演。",
      "必须有同步实测真值。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "33_physical_inversion": {
    method: "PROSAIL LUT：默认 RMSE，对最优若干条的 LAI/Cab 取平均",
    cites: [
      paper(
        "Jacquemoud S., Baret F.",
        "1990",
        "PROSPECT: A model of leaf optical properties spectra",
        "Remote Sensing of Environment, 34(2), 75–91",
        "https://doi.org/10.1016/0034-4257(90)90100-Z",
        "提出叶片光学模型 PROSPECT：用叶绿素、水分、干物质等参数模拟叶片从可见光到短波红外的反射与透射光谱，是后续冠层反演的叶片模块。",
      ),
      paper(
        "Verhoef W.",
        "1984",
        "Light scattering by leaf layers with application to canopy reflectance modeling: The SAIL model",
        "Remote Sensing of Environment, 16(2), 125–141",
        "https://doi.org/10.1016/0034-4257(84)90057-9",
        "提出 SAIL 冠层反射模型：把叶片层散射与太阳/观测几何结合起来，模拟植被冠层二向反射。与 PROSPECT 耦合后即 PROSAIL。",
      ),
      paper(
        "Jacquemoud S., Verhoef W., Baret F., et al.",
        "2009",
        "PROSPECT + SAIL models: A review of use for vegetation characterization",
        "Remote Sensing of Environment, 113, S56–S66",
        "https://doi.org/10.1016/j.rse.2008.01.026",
        "综述 PROSPECT+SAIL 在植被参数反演中的用法：叶面积指数、叶绿素等如何通过查找表或优化从冠层光谱中估计，并讨论适用范围与不确定性。",
      ),
      paper(
        "Xiao Z.Q., Liang S.L., Wang J.D., Chen P., Yin X.J., Zhang L.Q.（肖志强、梁顺林、王锦地等）",
        "2014",
        "Use of General Regression Neural Networks for Generating the GLASS Leaf Area Index Product From Time-Series MODIS Surface Reflectance",
        "IEEE Transactions on Geoscience and Remote Sensing",
        "https://doi.org/10.1109/tgrs.2013.2237780",
        "Crossref 核实肖志强、梁顺林、王锦地等用广义回归神经网络从 MODIS 生成 GLASS LAI 产品。证明国内把 LAI 反演作为既有业务。题录不是本仓库 PROSAIL 查找表公式。",
      ),
      paper(
        "Weiss M., Baret F., Myneni R.B., Pragnère A., Knyazikhin Y.",
        "2000",
        "Investigation of a model inversion technique to estimate canopy biophysical variables from spectral and directional reflectance data",
        "Agronomie, 20(1), 3–22",
        "https://doi.org/10.1051/agro:2000105",
        "用辐射传输模型建查找表反演冠层变量，并对代价最优的一组解取平均，以减轻病态反演的非唯一性。是本仓库 LUT 多解平均的方法出处。",
      ),
      paper(
        "Darvishzadeh R., Skidmore A., Schlerf M., Atzberger C.",
        "2008",
        "Inversion of a radiative transfer model for estimating vegetation LAI and chlorophyll in a heterogeneous grassland",
        "Remote Sensing of Environment, 112(5), 2592–2604",
        "https://doi.org/10.1016/j.rse.2007.12.003",
        "用 PROSAIL 查找表反演草地叶面积指数与叶绿素，匹配代价采用实测与模拟光谱的均方根误差 RMSE。是本仓库默认 RMSE 代价的方法出处。",
      ),
      paper(
        "Combal B., Baret F., Weiss M., et al.",
        "2003",
        "Retrieval of canopy biophysical variables from bidirectional reflectance: Using prior information to solve the ill-posed inverse problem",
        "Remote Sensing of Environment, 84(1), 1–15",
        "https://doi.org/10.1016/S0034-4257(02)00035-4",
        "指出冠层参数反演是病态问题，并用先验信息约束解空间。本仓库未实现该先验，此条只支持限制主张，不支持已交付公式。",
      ),
    ],
    diffs: [
      "默认 25×16 的 LAI/Cab 网格，土壤、叶倾角、叶片水和干物质仍写死，不是 ARTMO 全维查找表。",
      "最优解集按 LUT 条数比例截取，不是 Weiss 原文按最小代价阈值截取。",
      "未实现 Combal 先验或迭代数值优化。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出支持向量机：用核函数把样本映射到高维，求最大间隔超平面做二分类。后续高光谱像素分类长期把它当作强基线。",
      ),
      paper(
        "Breiman L.",
        "2001",
        "Random Forests",
        "Machine Learning, 45, 5–32",
        "https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf",
        "提出随机森林：多棵决策树在自助样本与随机特征子集上训练，投票或平均得到分类/回归。给出袋外误差与变量重要性。开放 PDF。",
      ),
      paper(
        "Tan K.（谭琨）",
        "2008",
        "HYPERSPECTRAL REMOTE SENSING IMAGE CLASSIFICATION BASED ON SUPPORT VECTOR MACHINE",
        "红外与毫米波学报 / JOURNAL OF INFRARED AND MILLIMETER WAVES",
        "https://doi.org/10.3724/SP.J.1010.2008.00123",
        "Crossref 核实《红外与毫米波学报》发表基于支持向量机的高光谱遥感分类。证明国内把 SVM 高光谱分类作为既有算法。不替代 Cortes & Vapnik 或 Breiman 作为 SVM/随机森林原始出处。",
      ),
    ],
    diffs: [
      "用 sklearn 的 SVM 和随机森林，不是遥感专有分类器。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "介绍光谱图像处理系统 SIPS：交互可视化成像光谱数据，其中光谱角填图（SAM）用像元光谱与参考光谱的夹角衡量相似度，对亮度缩放不敏感。",
      ),
      paper(
        "Chang C.-I.",
        "2000",
        "An information-theoretic approach to spectral variability, similarity, and discrimination for hyperspectral image analysis",
        "IEEE Transactions on Information Theory, 46(5), 1927–1932",
        "https://www2.umbc.edu/rssipl/pdf/IT_2000.pdf",
        "从信息论定义光谱信息散度（SID）：用两条光谱作为概率分布的相对熵衡量差异，用于高光谱识别与判别。作者组开放 PDF。",
      ),
    ],
    diffs: [
      "同时计算光谱角 SAM 和光谱信息散度 SID。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "把一维卷积神经网络直接打在高光谱像元光谱上做地物分类，对比 SVM 等传统方法。是早期深度学习高光谱分类的常用对照结构。发表于 Journal of Sensors。",
      ),
    ],
    diffs: [
      "这是常用一维卷积对照结构，超参不是某篇论文的官方复现。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出 HybridSN：先用 3-D 卷积提取空谱局部特征，再用 2-D 卷积压空间，输入是中心像素的邻域立方体。Indian Pines 等基准上高于当时纯 2-D/3-D CNN。",
      ),
      paper(
        "Li Y., Zhang H.K., Shen Q.（李英、张浩奎、沈强）",
        "2017",
        "Spectral–Spatial Classification of Hyperspectral Imagery with 3D Convolutional Neural Network",
        "Remote Sensing",
        "https://doi.org/10.3390/rs9010067",
        "Crossref 核实作者单位为西北工业大学。论文用 3D 卷积做高光谱空谱分类。证明国内把 3D-CNN 作为既有方法。不替代 HybridSN 作为本仓库对照结构出处。",
      ),
    ],
    diffs: [
      "短训生产算法（页面样例为演示数据），数据和超参不是论文中 Indian Pines 全量实验。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出 SpectralFormer：把相邻波段编成 token，用 Transformer 捕获光谱序列依赖，并加跨层残差减轻过平滑。在高光谱分类基准上优于当时 CNN。开放预印本。",
      ),
    ],
    diffs: [
      "缩小了通道数和层数，不能当作论文官方实现复现。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出原型网络：每类用支撑集在嵌入空间的均值当原型，查询样本按到原型的距离分类。原文用欧氏距离，是少样本学习的经典度量方法。",
      ),
      paper(
        "Yang G., Wang Z.H.（杨甘、王兆晖）",
        "2025",
        "A Deep Transfer Contrastive Learning Network for Few-Shot Hyperspectral Image Classification",
        "Remote Sensing",
        "https://doi.org/10.3390/rs17162800",
        "Crossref 核实作者单位为海南大学。论文讨论高光谱少样本分类。证明国内把少样本高光谱分类作为既有研究方向。题录不是 Prototypical Networks 原始出处，也不规定本仓库 SAM 均值原型。",
      ),
    ],
    diffs: [
      "原型是支持集光谱均值，用最小光谱角分类。",
      "不是 Snell 原文在可学习嵌入空间、用欧氏距离训练的原型网络。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "40_detect_segment": {
    method: "ACE 自适应余弦估计（目标探测）",
    cites: [
      paper(
        "Scharf L. L., McWhorter L. T.",
        "1996",
        "Adaptive matched subspace detectors and adaptive coherence estimators",
        "Proceedings of the 30th Asilomar Conference on Signals, Systems and Computers",
        "https://doi.org/10.1109/ACSSC.1996.599116",
        "原始会议论文给出自适应匹配子空间检测器及 ACE 特例，只支持 ACE 检测器，不支持低 NDVI 种子构造、分位阈值或连通斑块策略。",
      ),
      paper(
        "Bai X.H., Li L., Xie X.M., Li W., Wu Y.F., Gao L.R.（白新华、李伟、高连如等）",
        "2019",
        "FPGA Implementation for Hyperspectral Target Detection with Adaptive Coherence Estimator",
        "2019 IEEE International Conference on Signal, Information and Data Processing (ICSIDP)",
        "https://doi.org/10.1109/icsidp47821.2019.9173104",
        "Crossref 核实北京化工大学与高连如等实现 ACE 高光谱目标检测。证明国内把 ACE 作为既有检测器。这是会议文，不替代 Scharf & McWhorter 1996，也不支持本仓库低 NDVI 种子策略。",
      ),
    ],
    diffs: [
      "ACE 检测器按文献；低 NDVI 种子策略、分位阈值和连通斑块是本仓库启发式。",
      "没有做深度学习语义分割。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出全约束最小二乘（FCLS）线性光谱混合分析：丰度非负且和为 1，把像元光谱分解为端元比例。用于高光谱物质定量。作者组开放 PDF。",
      ),
    ],
    diffs: [
      "丰度非负且和为 1；端元光谱由第二输入提供。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出多波段恒虚警检测（后称 RX/Reed–Xiaoli）：在未知目标光谱时，用背景协方差把像元马氏距离当作异常分数。是高光谱异常探测的标准检测器。",
      ),
      paper(
        "Zhao C.H., Deng W.W., Yan Y.M., Yao X.F.（赵春晖、邓伟伟等）",
        "2017",
        "Progressive Line Processing of Kernel RX Anomaly Detection Algorithm for Hyperspectral Imagery",
        "Sensors",
        "https://doi.org/10.3390/s17081815",
        "Crossref 核实作者单位为哈尔滨工程大学。论文讨论核 RX 高光谱异常检测。证明国内把 RX 一类异常检测作为既有算法。不替代 Reed–Yu 1990。",
      ),
    ],
    diffs: [
      "局部 RX 用外窗估计背景协方差；演示数据小，窗参数需相应缩小。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "提出正则化迭代加权 MAD（IR-MAD）：在多/高光谱双时相数据上找典型相关差异，迭代降权变化像元，用于变化检测。DTU 开放 PDF。",
      ),
      paper(
        "Chen J., Gong P., He C.Y., Pu R.L., Shi P.J.（陈晋、宫鹏、何春阳、史培军等）",
        "2003",
        "Land-Use/Land-Cover Change Detection Using Improved Change-Vector Analysis",
        "Photogrammetric Engineering & Remote Sensing",
        "https://doi.org/10.14358/pers.69.4.369",
        "Crossref 核实陈晋、宫鹏、史培军等用改进变化向量分析做土地利用/覆盖变化检测。证明国内把变化检测作为既有方法。题录不是 Nielsen IR-MAD 公式出处。",
      ),
    ],
    diffs: [
      "这是 IR-MAD 的生产算法（页面样例为演示数据），不是论文实验配置的完整复现。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
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
        "GDAL sieve 工具说明：剔除栅格分类图中小于给定像元数的连通斑块，并入邻域大类，用于去掉椒盐碎斑。",
      ),
      paper(
        "Esri",
        "2024",
        "Majority Filter (Spatial Analyst)",
        "ArcGIS Pro tool reference",
        "https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/majority-filter.htm",
        "ArcGIS 众数滤波工具说明：用邻域内出现次数最多的类别替换中心像元，平滑分类图边界、压孤立噪声。",
      ),
      paper(
        "Lu Q.K., Huang X., Liu T.T., Zhang L.P.（陆启凯、黄鑫、张良培等）",
        "2016",
        "A structural similarity-based label-smoothing algorithm for the post-processing of land-cover classification",
        "Remote Sensing Letters",
        "https://doi.org/10.1080/2150704x.2016.1149252",
        "Crossref 核实黄鑫、张良培等发表土地覆盖分类后处理的标签平滑。证明国内把分类后处理作为既有步骤。题录不是 GDAL sieve 或众数滤波工具说明。",
      ),
    ],
    diffs: [
      "先做窗口众数，再把小于阈值的小斑换成邻域众数；这次序是本仓库实现。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "45_parcel_zonal_stats": {
    method: "GeoJSON 栅格化后分区统计",
    cites: [
      paper(
        "GDAL/OGR contributors",
        "n.d.",
        "gdal_raster_zonal_stats — raster zonal statistics",
        "GDAL documentation",
        "https://gdal.org/en/latest/programs/gdal_raster_zonal_stats.html",
        "GDAL 分区统计工具说明提供按矢量或分区栅格汇总数值栅格的方法背景；页面未给出明确出版年份，也不支持本仓库具体 NaN/NoData、空区或分类整数化行为。",
      ),
      paper(
        "Wu B.F., Zhang M., Zeng H.W., Liu G.S., Chang S., Gommes R.（吴炳方等）",
        "2014",
        "New indicators for global crop monitoring in CropWatch -case study in North China Plain",
        "IOP Conference Series: Earth and Environmental Science",
        "https://doi.org/10.1088/1755-1315/17/1/012050",
        "Crossref 核实吴炳方等介绍 CropWatch 作物监测新指标及华北平原案例。证明国内把作物遥感监测与分区指标汇总作为既有业务。题录不是 GDAL 分区统计工具说明，也不规定本仓库 NoData 规则。",
      ),
    ],
    diffs: [
      "统计时排除 NaN 和栅格空值，空有效区不写成 0。",
      "分类模式会把连续值按整数类别计数。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "46_reci": {
    method: "RECI = NIR / RE − 1",
    cites: [
      paper(
        "Gitelson A. A., Gritz Y., Merzlyak M. N.",
        "2003",
        "Relationships between leaf chlorophyll content and spectral reflectance and algorithms for non-destructive chlorophyll assessment in higher plant leaves",
        "Journal of Plant Physiology, 160(3), 271–282",
        "https://doi.org/10.1078/0176-1617-00887",
        "提出用近红外与红边反射率比值减 1 的叶绿素指数，说明它对叶片叶绿素变化敏感，但论文给出的是叶片尺度关系，不是冠层毫克数产品。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零，不是文献公式的一部分。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "47_gndvi": {
    method: "GNDVI = (NIR − GREEN) / (NIR + GREEN)",
    cites: [
      paper(
        "Gitelson A. A., Kaufman Y. J., Merzlyak M. N.",
        "1996",
        "Use of a green channel in remote sensing of global vegetation from EOS-MODIS",
        "Remote Sensing of Environment, 58(3), 289–298",
        "https://doi.org/10.1016/S0034-4257(96)00072-7",
        "论证在 EOS-MODIS 中引入绿光通道，用绿光与近红外组合改进植被监测，为 GNDVI 一类绿光归一化指数提供方法来源。",
      ),
      paper(
        "Wang J.H., Liu L.Y., Huang W.J., Zhao C.J.（王纪华、刘良云、黄文江、赵春江）",
        "2003",
        "Estimating winter wheat yield from hyperspectral data",
        "IGARSS 2003 IEEE International Geoscience and Remote Sensing Symposium",
        "https://doi.org/10.1109/igarss.2003.1294399",
        "Crossref 核实王纪华、刘良云、黄文江、赵春江用高光谱估冬小麦产量。证明国内把冠层绿度/光谱指数作为既有方法。这是 IGARSS 会议文，不能核对本仓库 GNDVI 公式。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零，不是文献公式的一部分。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "48_osavi": {
    method: "OSAVI = (NIR − RED) / (NIR + RED + L)，默认 L=0.16",
    cites: [
      paper(
        "Rondeaux G., Steven M., Baret F.",
        "1996",
        "Optimization of soil-adjusted vegetation indices",
        "Remote Sensing of Environment, 55(2), 95–107",
        "https://doi.org/10.1016/0034-4257(95)00186-7",
        "比较多种土壤调节植被指数，给出 OSAVI = (NIR−RED)/(NIR+RED+0.16)，说明 0.16 是针对其实验条件优化的土壤项，不是任意传感器的现场标定。",
      ),
    ],
    diffs: [
      "允许改写 L，文献原文把 0.16 当作优化结果而不是可调参数面板。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "49_arvi": {
    method: "ARVI = (NIR − RB) / (NIR + RB)，RB = RED − γ(BLUE − RED)",
    cites: [
      paper(
        "Kaufman Y. J., Tanré D.",
        "1992",
        "Atmospherically resistant vegetation index (ARVI) for EOS-MODIS",
        "IEEE Transactions on Geoscience and Remote Sensing, 30(2), 261–270",
        "https://doi.org/10.1109/36.134076",
        "定义 ARVI，用蓝光通道构造自校正红光 RB = RED − γ(BLUE − RED)，常用 γ=1，说明它抵抗大气影响，但不是完整大气校正替代方案。",
      ),
      paper(
        "Yang L.Q., Jia K., Liang S.L., Liu J.C., Wang X.X.（杨林青、贾坤、梁顺林等）",
        "2016",
        "Comparison of Four Machine Learning Methods for Generating the GLASS Fractional Vegetation Cover Product from MODIS Data",
        "Remote Sensing",
        "https://doi.org/10.3390/rs8080682",
        "Crossref 核实作者单位为北京师范大学遥感科学国家重点实验室。论文比较机器学习生成 GLASS 植被覆盖度。证明国内把植被指数/覆盖度反演作为既有业务。题录不是 Kaufman ARVI 公式出处。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零。",
      "γ 做成请求参数，默认 1。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "50_vari": {
    method: "VARI = (GREEN − RED) / (GREEN + RED − BLUE)",
    cites: [
      paper(
        "Gitelson A. A., Kaufman Y. J., Stark R., Rundquist D.",
        "2002",
        "Novel algorithms for remote estimation of vegetation fraction",
        "Remote Sensing of Environment, 80(1), 76–87",
        "https://doi.org/10.1016/S0034-4257(01)00289-9",
        "提出在可见光空间用绿、红、蓝组合估计植被覆盖分数，给出 VARI = (GREEN−RED)/(GREEN+RED−BLUE)，并讨论大气与土壤背景影响。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零，不是文献公式的一部分。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "51_lai_index": {
    method: "LAI = max(3.618 × EVI − 0.118, 0)",
    cites: [
      paper(
        "Huete A., Didan K., Miura T., Rodriguez E. P., Gao X., Ferreira L. G.",
        "2002",
        "Overview of the radiometric and biophysical performance of the MODIS vegetation indices",
        "Remote Sensing of Environment, 83(1–2), 195–213",
        "https://doi.org/10.1016/S0034-4257(02)00096-2",
        "给出 MODIS EVI 公式与系数，说明 EVI 相对 NDVI 在密冠层更晚饱和；并不规定把 EVI 线性换成全球 LAI。",
      ),
      paper(
        "Carlson T. N., Ripley D. A.",
        "1997",
        "On the relation between NDVI, fractional vegetation cover, and leaf area index",
        "Remote Sensing of Environment, 62(3), 241–252",
        "https://doi.org/10.1016/S0034-4257(97)00104-1",
        "说明植被指数与叶面积指数关系在高叶面积时饱和，因此不能把某一个固定线性式当成普遍 LAI 产品。",
      ),
      paper(
        "Wang J., Wang J.D., Zhou H.M., Xiao Z.Q.（王健、王锦地、周红敏、肖志强）",
        "2017",
        "Detecting Forest Disturbance in Northeast China from GLASS LAI Time Series Data Using a Dynamic Model",
        "Remote Sensing",
        "https://doi.org/10.3390/rs9121293",
        "Crossref 核实作者单位为北京师范大学遥感科学国家重点实验室。论文用 GLASS LAI 时间序列检测东北森林扰动。证明国内把 LAI 作为既有产品。题录不是本仓库 NDVI 经验 LAI 公式。",
      ),
    ],
    diffs: [
      "线性系数 3.618/−0.118 是本仓库演示数据默认，不是 Huete 2002 给出的 LAI 产品。",
      "负值裁成 0。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "52_nbr": {
    method: "NBR = (NIR − SWIR) / (NIR + SWIR)",
    cites: [
      paper(
        "Key C. H., Benson N. C.",
        "2006",
        "Landscape Assessment (LA) Sampling and Analysis Methods",
        "USDA Forest Service General Technical Report RMRS-GTR-164-CD",
        "https://www.fs.usda.gov/rm/pubs_series/rmrs/gtr/rmrs_gtr164/rmrs_gtr164_13_land_assess.pdf",
        "FIREMON 景观评估方法给出 NBR = (NIR − SWIR)/(NIR + SWIR)，并说明 Landsat 上常用近红外与 SWIR2；差分 NBR 用于过火严重度，不是面积或金额。",
      ),
      paper(
        "Liu R.G., Liu J.Y., Lv X., Hou Y.（刘荣高、刘纪远等）",
        "2005",
        "Mapping forest burned area using MODIS data in China",
        "Proceedings. 2005 IEEE International Geoscience and Remote Sensing Symposium",
        "https://doi.org/10.1109/igarss.2005.1525883",
        "Crossref 核实刘荣高、刘纪远等用 MODIS 绘制中国森林过火区。证明国内把过火遥感作为既有方法。这是 IGARSS 会议文，不能核对本仓库 NBR 公式。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零。",
      "演示数据默认 SWIR 约 1600 nm，不是 Landsat SWIR2。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "53_sipi": {
    method: "SIPI = (NIR − BLUE) / (NIR − RED)",
    cites: [
      paper(
        "Peñuelas J., Baret F., Filella I.",
        "1995",
        "Semi-empirical indices to assess carotenoids/chlorophyll a ratio from leaf spectral reflectance",
        "Photosynthetica, 31(2), 221–230",
        "https://www.uv.es/jpenuela/Penuelas1995Photosynthetica.pdf",
        "给出 SIPI = (R800 − R445)/(R800 − R680) 一类半经验指数，用于估测类胡萝卜素与叶绿素 a 比值，并讨论冠层结构影响较小；不是冠层含量产品。",
      ),
      paper(
        "Cheng Q.（程乾）",
        "2003",
        "In situ hyperspectral data analysis for pigment content estimation of rice leaves",
        "Journal of Zhejiang University SCIENCE",
        "https://doi.org/10.1631/jzus.2003.0727",
        "Crossref 核实程乾用田间高光谱估水稻叶片色素含量。证明国内把色素相关光谱指数作为既有方法。题录不能核对本仓库 SIPI 公式。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零。",
      "波段用请求索引，不固定 800/445/680 nm。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "54_gci": {
    method: "GCI = NIR / GREEN − 1",
    cites: [
      paper(
        "Gitelson A. A., Viña A., Ciganda V., Rundquist D. C., Arkebauer T. J.",
        "2005",
        "Remote estimation of canopy chlorophyll content in crops",
        "Geophysical Research Letters, 32, L08403",
        "https://doi.org/10.1029/2005GL022688",
        "在冠层尺度使用绿色与红边叶绿素指数 CI = NIR/波段 − 1 估测作物叶绿素相关量，说明指数与含量相关但需本地关系，不是通用毫克数产品。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零，不是文献公式的一部分。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
  "55_ndsi": {
    method: "NDSI = (GREEN − SWIR) / (GREEN + SWIR)",
    cites: [
      paper(
        "Hall D. K., Riggs G. A., Salomonson V. V.",
        "1995",
        "Development of methods for mapping global snow cover using Moderate Resolution Imaging Spectroradiometer (MODIS) data",
        "Remote Sensing of Environment, 54(2), 127–140",
        "https://doi.org/10.1016/0034-4257(95)00137-P",
        "给出用绿光与短波红外计算 NDSI 并辅助全球积雪制图的方法，说明阈值与云、冰混淆需额外规则，NDSI 本身不是面积产品。",
      ),
    ],
    diffs: [
      "分母加 1e-12，只防除零。",
      "不输出积雪二值掩膜或云检测。",
      "国内文献只证明方法在国内被使用，不替代原有国外公式出处。",
    ],
  },
};

export function getAlgoSource(id: string): AlgoSource | undefined {
  return SOURCES[id];
}

/** 文献页适配层：把证据清单与已核验题录绑成三部分视图，不改写作者/题名/DOI。 */
export function getSourcePanelView(id: string): SourcePanelView | undefined {
  const evidence = getAlgorithmEvidence(id);
  if (evidence === undefined) {
    return undefined;
  }
  return buildSourcePanelView(evidence, getAlgoSource(id));
}
