#!/usr/bin/env python3
"""只追加国内文献与 existence 主张，不删除原有国外文献。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "shared" / "scientific_evidence.json"
SOURCES = ROOT / "web" / "src" / "sources.ts"

TARGETS = [
    "principle",
    "source-panel",
    "console-output",
    "ai-knowledge",
    "product-analysis",
    "docs-api-checklist",
    "docs-algorithm-inventory",
]
REVIEW = (
    "Crossref 题录已核实。国内文献只证明方法在国内被使用；未核全文的不挂到公式主张上，"
    "也不删除原有国外文献。"
)
DIFF = "国内文献只证明方法在国内被使用，不替代原有国外公式出处。"

# 新文献：不得写入 formula.supports
NEW = {
    "01_flight_planning": {
        "text": "李德仁、张过等对资源三号多光谱影像做几何检校与精度评估，国内把摄影测量几何作为既有方法；本条目不是仓库自造。",
        "paper": {
            "authors": "Jiang Y.H., Zhang G., Tang X.M., Li D.R., Huang W.C., Pan H.B.（姜永华、张过、唐新明、李德仁等）",
            "year": "2014",
            "title": "Geometric Calibration and Accuracy Assessment of ZiYuan-3 Multispectral Images",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2013.2280134",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实李德仁、张过等发表资源三号多光谱几何检校与精度评估。证明国内把卫星摄影测量几何作为既有方法。题录不规定本仓库航线 GSD 或重叠率公式。",
        },
    },
    "02_sync_timestamp": {
        "text": "袁修孝在武汉测绘科技大学发表 GPS 辅助空中三角测量原理与实验，国内把 GPS/POS 辅助航空影像定位作为既有方法。",
        "paper": {
            "authors": "Yuan X.X.（袁修孝）",
            "year": "2000",
            "title": "Principle, software and experiment of GPS-supported aerotriangulation",
            "venue": "Geo-spatial Information Science",
            "url": "https://doi.org/10.1007/bf02826803",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为武汉测绘科技大学。论文讨论 GPS 辅助空中三角测量的原理、软件与实验。公开题录未给出本仓库中位钟差或 RGB 最近邻容差。",
        },
    },
    "03_pos_solution": {
        "text": "袁修孝等把 GPS 精密单点定位用于空中三角测量，国内 POS/GPS 辅助航空定位不是仓库自造。",
        "paper": {
            "authors": "Yuan X.X., Fu J.H., Sun H.X., Toth C.（袁修孝、付建红、孙红星等）",
            "year": "2009",
            "title": "The application of GPS precise point positioning technology in aerial triangulation",
            "venue": "ISPRS Journal of Photogrammetry and Remote Sensing",
            "url": "https://doi.org/10.1016/j.isprsjprs.2009.03.006",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实袁修孝等把 GPS PPP 用于空中三角测量。证明国内把 GPS/POS 辅助航空定位作为既有方法。题录不是本仓库 RTS 平滑或杠杆臂公式出处。",
        },
    },
    "04_flight_qc": {
        "text": "国家卫星气象中心对风云三号 MERSI 反射太阳波段做在轨辐射定标，国内把辐射质量检校作为既有业务。",
        "paper": {
            "authors": "Sun L., Hu X.Q., Xu N., Liu J.J., Zhang L.J., Rong Z.G.（孙凌、胡秀清等）",
            "year": "2013",
            "title": "Postlaunch Calibration of FengYun-3B MERSI Reflective Solar Bands",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2012.2217345",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实胡秀清等发表风云三号 MERSI 反射太阳波段发射后定标。证明国内把卫星辐射质量检校作为既有方法。题录不规定本仓库过曝阈值。",
        },
    },
    "05_cloud_shadow": {
        "text": "何彬彬等与 Fmask 作者合作改进山地 Landsat 云和云影检测，国内把云/云影检测作为既有算法。",
        "paper": {
            "authors": "Qiu S., He B.B., Zhu Z., Liao Z.M., Quan X.W.（邱实、何彬彬、朱哲等）",
            "year": "2017",
            "title": "Improving Fmask cloud and cloud shadow detection in mountainous area for Landsats 4–8 images",
            "venue": "Remote Sensing of Environment",
            "url": "https://doi.org/10.1016/j.rse.2017.07.002",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实何彬彬等与朱哲合作改进山地 Landsat 的 Fmask 云和云影检测。证明国内把云/云影检测作为既有算法。不替代 Zhu & Woodcock 2012 作为 Fmask 原始出处，也不规定本仓库简化判据。",
        },
    },
    "06_dark_current": {
        "text": "中国科学院团队发表成像光谱仪暗电平校正方法，暗电流/暗场校正不是仓库自造。",
        "paper": {
            "authors": "An L.P., Wang Y.H., Zhao H., Yu C., Wang Y.H., Wang S., Liu X.B.（安凌平、刘学斌等）",
            "year": "2023",
            "title": "Dynamic space–time dark level correction approach for lunar radiometric calibration of the Lunar Observation Imaging Spectrometer",
            "venue": "Applied Optics",
            "url": "https://doi.org/10.1364/ao.476640",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位含中国科学院大学。论文讨论成像光谱仪暗电平时空校正。证明国内把暗场/暗电流校正作为既有步骤。题录不是本仓库逐波段最小值替代暗帧的工程默认。",
        },
    },
    "07_bad_pixel": {
        "text": "武汉大学沈焕锋、张良培提出遥感影像去条带与缺失像元填补，坏像元修复一类方法在国内使用。",
        "paper": {
            "authors": "Shen H.F., Zhang L.P.（沈焕锋、张良培）",
            "year": "2009",
            "title": "A MAP-Based Algorithm for Destriping and Inpainting of Remotely Sensed Images",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2008.2005780",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实沈焕锋、张良培发表遥感影像 MAP 去条带与填补。填补对应坏像元/缺失像元修复这一类问题。题录不是本仓库 6σ/4σ 检测阈值。",
        },
    },
    "08_destriping": {
        "text": "武汉大学沈焕锋、张良培发表遥感影像 MAP 去条带算法，条带去除不是仓库自造。",
        "paper": {
            "authors": "Shen H.F., Zhang L.P.（沈焕锋、张良培）",
            "year": "2009",
            "title": "A MAP-Based Algorithm for Destriping and Inpainting of Remotely Sensed Images",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2008.2005780",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实沈焕锋、张良培发表遥感影像 MAP 去条带与填补。证明国内把去条带作为既有算法。不替代 Gadallah 矩匹配作为本仓库对照出处。",
        },
    },
    "09_smile_keystone": {
        "text": "国内文献研究成像光谱仪 smile 与 keystone 消除，光谱畸变校正不是仓库自造。",
        "paper": {
            "authors": "Zhang X.L., Yu K., Zhang J.（张晓龙、于琨、张俊）",
            "year": "2017",
            "title": "Study on imaging spectrometer with smile and keystone eliminated",
            "venue": "Optics Communications",
            "url": "https://doi.org/10.1016/j.optcom.2016.11.048",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实题名研究成像光谱仪 smile 与 keystone 消除。证明该方法在国内光学工程文献中作为既有问题处理。公开题录未列单位，也不能核对本仓库互相关估计公式。",
        },
    },
    "10_radiance_calibration": {
        "text": "胡秀清等对风云三号 MERSI 做发射后辐射定标，国内把 DN 到辐亮度定标作为既有业务。",
        "paper": {
            "authors": "Sun L., Hu X.Q., Xu N., Liu J.J., Zhang L.J., Rong Z.G.（孙凌、胡秀清等）",
            "year": "2013",
            "title": "Postlaunch Calibration of FengYun-3B MERSI Reflective Solar Bands",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2012.2217345",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实胡秀清等发表风云三号 MERSI 反射太阳波段在轨定标。证明国内把辐射定标作为既有方法。题录不规定本仓库默认增益偏置。",
        },
    },
    "11_relative_radiometric": {
        "text": "武汉大学发表遥感影像相对辐射归一方法，相对辐射校正不是仓库自造。",
        "paper": {
            "authors": "Chen Y.P.（陈叶培）",
            "year": "2018",
            "title": "Improved relative radiometric normalization method of remote sensing images for change detection",
            "venue": "Journal of Applied Remote Sensing",
            "url": "https://doi.org/10.1117/1.jrs.12.045018",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为武汉大学测绘遥感信息工程国家重点实验室。论文改进相对辐射归一用于变化检测。题录不是直方图匹配文档，也不支持本仓库左上角裁切。",
        },
    },
    "12_panel_reflectance": {
        "text": "北京航空航天大学赵慧洁等用经验线性法从高光谱反演地表反射率，白板/经验线性定标在国内使用。",
        "paper": {
            "authors": "Jia G.R., Xue Q., Zhao H.J.（贾国瑞、薛倩、赵慧洁）",
            "year": "2018",
            "title": "Uncertainty Analysis for Surface Reflectance Retrieved from Hyperspectral Remote Sensing Image using Empirical Line Method",
            "venue": "2018 9th Workshop on Hyperspectral Image and Signal Processing: Evolution in Remote Sensing (WHISPERS)",
            "url": "https://doi.org/10.1109/whispers.2018.8747131",
            "sourceType": "academic-material",
            "summary": "Crossref 核实北航精密光电测试技术实验室用经验线性法从高光谱影像反演地表反射率并做不确定度分析。证明国内把经验线性/参考板定标作为既有方法。这是会议论文，不能当作 Smith & Milton 1999 的替代出处。",
        },
    },
    "13_atmospheric_correction": {
        "text": "梁顺林等发表 Landsat ETM+ 大气校正方法，国内定量遥感把大气校正作为既有步骤。",
        "paper": {
            "authors": "Liang S., Fang H., Chen M.（梁顺林等）",
            "year": "2001",
            "title": "Atmospheric correction of Landsat ETM+ land surface imagery. I. Methods",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/36.964986",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实梁顺林等发表 Landsat ETM+ 大气校正方法。梁顺林后在北京师范大学持续开展定量遥感。题录不是 Chavez DOS 公式出处，也不规定本仓库暗目标假设。",
        },
    },
    "14_brdf_correction": {
        "text": "李小文与 Strahler 提出离散冠层几何光学双向反射模型，国内 BRDF 研究以此为经典贡献。",
        "paper": {
            "authors": "Li X., Strahler A.H.（李小文、Strahler）",
            "year": "1992",
            "title": "Geometric-optical bidirectional reflectance modeling of the discrete crown vegetation canopy: effect of crown shape and mutual shadowing",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/36.134078",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实李小文与 Strahler 发表离散冠层几何光学双向反射模型。李小文为中国科学院/北京师范大学学者，该文是国内 BRDF 研究的经典贡献。不替代 Roujean 核驱动模型作为本仓库对照出处。",
        },
    },
    "15_geo_locate": {
        "text": "袁修孝把 GPS 辅助空中三角测量用于航空影像定位，国内 POS 粗定位不是仓库自造。",
        "paper": {
            "authors": "Yuan X.X.（袁修孝）",
            "year": "2000",
            "title": "Principle, software and experiment of GPS-supported aerotriangulation",
            "venue": "Geo-spatial Information Science",
            "url": "https://doi.org/10.1007/bf02826803",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实袁修孝（武汉测绘科技大学）发表 GPS 辅助空中三角测量。证明国内把 GPS/POS 辅助航空定位作为既有方法。题录不规定本仓库中心点与 GSD 粗定位公式。",
        },
    },
    "16_orthorectify": {
        "text": "张祖勋、张剑清等在武汉测绘科技大学建立数字摄影测量工作站，正射相关流程在国内使用。",
        "paper": {
            "authors": "Zhang J.Q., Zhang Z.X., Wu X.L., Wang Z.H., Qiu T., Cao H.（张剑清、张祖勋等）",
            "year": "1994",
            "title": "Photogrammetric workstation from Wuhan Technical University of Surveying and Mapping (WTUSM)",
            "venue": "SPIE Proceedings",
            "url": "https://doi.org/10.1117/12.182886",
            "sourceType": "academic-material",
            "summary": "Crossref 核实张祖勋、张剑清等介绍武汉测绘科技大学数字摄影测量工作站。证明国内把数字摄影测量与正射相关流程作为既有能力。这是会议文，不规定本仓库相机模型或 DEM 正射公式。",
        },
    },
    "19_multi_source_register": {
        "text": "张祖勋、张剑清等的数字摄影测量工作站包含影像匹配，国内把影像配准作为既有工序。",
        "paper": {
            "authors": "Zhang J.Q., Zhang Z.X., Wu X.L., Wang Z.H., Qiu T., Cao H.（张剑清、张祖勋等）",
            "year": "1994",
            "title": "Photogrammetric workstation from Wuhan Technical University of Surveying and Mapping (WTUSM)",
            "venue": "SPIE Proceedings",
            "url": "https://doi.org/10.1117/12.182886",
            "sourceType": "academic-material",
            "summary": "Crossref 核实武测数字摄影测量工作站文献。工作站包含影像匹配配准。证明国内把影像配准作为既有工序。题录不是 Foroosh 亚像素相位相关公式出处。",
        },
    },
    "20_bad_band_remove": {
        "text": "张兵、童庆禧等建设高光谱数据库并讨论应用，国内高光谱处理包含波段取舍。",
        "paper": {
            "authors": "Li X., Zhang B., Tong Q.X., Zhang W.J.（李星、张兵、童庆禧等）",
            "year": "2005",
            "title": "Demand-oriented hyperspectral database and its applications",
            "venue": "Proceedings. 2005 IEEE International Geoscience and Remote Sensing Symposium",
            "url": "https://doi.org/10.1109/igarss.2005.1526528",
            "sourceType": "academic-material",
            "summary": "Crossref 核实张兵、童庆禧等介绍面向需求的高光谱数据库及其应用。证明国内高光谱处理包含波段组织与取舍。这是 IGARSS 会议文，不是 HITRAN 吸收线数据库，也不规定本仓库坏波段规则。",
        },
    },
    "21_savgol_smooth": {
        "text": "《分析化学》发表近红外 Savitzky–Golay 平滑与 PLS 联合优化，SG 平滑在国内光谱分析中使用。",
        "paper": {
            "authors": "Xie J., Pan T., Chen J.M., Chen H.Z., Ren X.H.（谢军、潘涛等）",
            "year": "2010",
            "title": "Joint Optimization of Savitzky-Golay Smoothing Models and Partial Least Squares Factors for Near-infrared Spectroscopic Analysis of Serum Glucose",
            "venue": "分析化学 / CHINESE JOURNAL OF ANALYTICAL CHEMISTRY",
            "url": "https://doi.org/10.3724/sp.j.1096.2010.00342",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实《分析化学》发表近红外 Savitzky–Golay 平滑与 PLS 因子联合优化。证明 SG 平滑在国内光谱分析中作为既有预处理。不替代 Savitzky & Golay 1964 作为公式出处。",
        },
    },
    "22_normalize": {
        "text": "国内近红外分析文献把平滑与多元预处理当作既有步骤，标准化/归一化不是仓库自造概念。",
        "paper": {
            "authors": "Xie J., Pan T., Chen J.M., Chen H.Z., Ren X.H.（谢军、潘涛等）",
            "year": "2010",
            "title": "Joint Optimization of Savitzky-Golay Smoothing Models and Partial Least Squares Factors for Near-infrared Spectroscopic Analysis of Serum Glucose",
            "venue": "分析化学 / CHINESE JOURNAL OF ANALYTICAL CHEMISTRY",
            "url": "https://doi.org/10.3724/sp.j.1096.2010.00342",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实《分析化学》近红外预处理与 PLS 联合优化。证明国内把光谱预处理当作既有步骤。公开题录未写 SNV 公式，不能替代 Barnes 等 1989。",
        },
    },
    "23_pca": {
        "text": "张兵、高连如等发表高光谱分解与降维相关算法，PCA/MNF 一类降维在国内高光谱处理中使用。",
        "paper": {
            "authors": "Zhang B., Zhuang L.N., Gao L.R., Luo W.F., Ran Q., Du Q.（张兵、高连如、罗文斐等）",
            "year": "2014",
            "title": "PSO-EM: A Hyperspectral Unmixing Algorithm Based On Normal Compositional Model",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2014.2319337",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实张兵、高连如等发表高光谱解混算法。证明中科院团队把高光谱降维与分解作为既有方法。题录侧重解混，不能当作 Green 等 MNF 公式出处。",
        },
    },
    "24_band_select": {
        "text": "杜培军等发表高光谱波段聚集与选择分析，波段选择在国内高光谱研究中使用。",
        "paper": {
            "authors": "Su H.J., Du P.J., Du Q.（苏红军、杜培军、杜谦）",
            "year": "2012",
            "title": "Hierarchical band clustering for hyperspectral image analysis",
            "venue": "7th IAPR Workshop on Pattern Recognition in Remote Sensing (PRRS)",
            "url": "https://doi.org/10.1109/pprs.2012.6398316",
            "sourceType": "academic-material",
            "summary": "Crossref 核实杜培军等发表高光谱分层波段聚集。证明国内把波段选择/聚集作为既有分析步骤。这是研讨会论文，不是 scikit-learn ANOVA 文档，也不规定本仓库默认波段数。",
        },
    },
    "25_superpixel": {
        "text": "李树涛、方乐缘等发表高光谱空谱分类，自适应空间对象在国内使用。",
        "paper": {
            "authors": "Fu W., Li S.T., Fang L.Y., Kang X.D., Benediktsson J.A.（付伟、李树涛、方乐缘等）",
            "year": "2014",
            "title": "Spectral-spatial hyperspectral classification via shape-adaptive sparse representation",
            "venue": "2014 IEEE Geoscience and Remote Sensing Symposium",
            "url": "https://doi.org/10.1109/igarss.2014.6947219",
            "sourceType": "academic-material",
            "summary": "Crossref 核实李树涛、方乐缘等发表基于形状自适应稀疏表示的高光谱空谱分类。证明国内把空间对象/自适应邻域作为既有思路。题录不是 Achanta SLIC 公式出处。",
        },
    },
    "26_patch_build": {
        "text": "北京化工大学胡伟等用一维卷积对高光谱像元光谱分类，样本/补丁输入在国内使用。",
        "paper": {
            "authors": "Hu W., Huang Y., Wei L., Zhang F., Li H.C.（胡伟、黄杨雨等）",
            "year": "2015",
            "title": "Deep Convolutional Neural Networks for Hyperspectral Image Classification",
            "venue": "Journal of Sensors, 2015, Article 258619",
            "url": "https://doi.org/10.1155/2015/258619",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为北京化工大学。论文用一维 CNN 对高光谱像元光谱分类。证明国内把像元/样本输入的深度学习分类作为既有方法。不替代 HybridSN 作为本仓库 3D 补丁对照。",
        },
    },
    "27_ndvi": {
        "text": "朴世龙、方精云等用 NDVI 分析中国植被年际变化，NDVI 在国内生态遥感中作为既有指数。",
        "paper": {
            "authors": "Piao S.L., Fang J.Y., Zhou L.M., Guo Q.H., Henderson M., Ji W., Li Y., Tao S.（朴世龙、方精云等）",
            "year": "2003",
            "title": "Interannual variations of monthly and seasonal normalized difference vegetation index (NDVI) in China from 1982 to 1999",
            "venue": "Journal of Geophysical Research: Atmospheres",
            "url": "https://doi.org/10.1029/2002JD002848",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实朴世龙、方精云等（北京大学）用 NDVI 分析 1982–1999 年中国植被年际变化。证明国内把 NDVI 作为既有指数。不替代 Rouse/Tucker 作为公式出处。",
        },
    },
    "28_ndre": {
        "text": "南京农业大学姚霞等用高光谱波段与指数估小麦氮积累，红边信息在国内农情遥感中使用。",
        "paper": {
            "authors": "Yao X., Zhu Y., Tian Y.C., Feng W., Cao W.X.（姚霞、朱艳、田永超、冯伟、曹卫星）",
            "year": "2010",
            "title": "Exploring hyperspectral bands and estimation indices for leaf nitrogen accumulation in wheat",
            "venue": "International Journal of Applied Earth Observation and Geoinformation",
            "url": "https://doi.org/10.1016/j.jag.2009.11.008",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实南京农业大学姚霞等探索小麦叶片氮积累的高光谱波段与估算指数。证明国内把红边相关指数作为既有方法。公开题录不能核对本仓库 NDRE 公式是否与 Barnes 等完全相同。",
        },
    },
    "29_evi_savi": {
        "text": "南京农业大学用多种冠层光谱指数做氮营养研究，土壤调节/增强型植被指数在国内使用。",
        "paper": {
            "authors": "Yao X., Zhu Y., Tian Y.C., Feng W., Cao W.X.（姚霞、朱艳、田永超、冯伟、曹卫星）",
            "year": "2010",
            "title": "Exploring hyperspectral bands and estimation indices for leaf nitrogen accumulation in wheat",
            "venue": "International Journal of Applied Earth Observation and Geoinformation",
            "url": "https://doi.org/10.1016/j.jag.2009.11.008",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实姚霞等用多种高光谱估算指数研究小麦氮积累。证明国内把冠层光谱指数作为既有方法。题录不能核对本仓库 EVI/SAVI/MSAVI 三条公式。",
        },
    },
    "32_regression_inversion": {
        "text": "南京农业大学薛利红、曹卫星等用冠层光谱反射率监测水稻氮素，经验光谱反演在国内使用。",
        "paper": {
            "authors": "Xue L.H., Cao W.X., Luo W.H., Dai T.B., Zhu Y.（薛利红、曹卫星、罗卫红、戴廷波、朱艳）",
            "year": "2004",
            "title": "Monitoring Leaf Nitrogen Status in Rice with Canopy Spectral Reflectance",
            "venue": "Agronomy Journal",
            "url": "https://doi.org/10.2134/agronj2004.0135",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实南京农业大学薛利红、曹卫星等用冠层光谱反射率监测水稻叶片氮素。证明国内把经验光谱反演作为既有方法。题录不是 PLS 公式出处。",
        },
    },
    "33_physical_inversion": {
        "text": "北京师范大学肖志强、梁顺林、王锦地等生成 GLASS LAI 产品，叶面积反演在国内业务中使用。",
        "paper": {
            "authors": "Xiao Z.Q., Liang S.L., Wang J.D., Chen P., Yin X.J., Zhang L.Q.（肖志强、梁顺林、王锦地等）",
            "year": "2014",
            "title": "Use of General Regression Neural Networks for Generating the GLASS Leaf Area Index Product From Time-Series MODIS Surface Reflectance",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2013.2237780",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实肖志强、梁顺林、王锦地等用广义回归神经网络从 MODIS 生成 GLASS LAI 产品。证明国内把 LAI 反演作为既有业务。题录不是本仓库 PROSAIL 查找表公式。",
        },
    },
    "34_svm_rf_classify": {
        "text": "《红外与毫米波学报》谭琨发表基于支持向量机的高光谱分类，SVM 高光谱分类在国内使用。",
        "paper": {
            "authors": "Tan K.（谭琨）",
            "year": "2008",
            "title": "HYPERSPECTRAL REMOTE SENSING IMAGE CLASSIFICATION BASED ON SUPPORT VECTOR MACHINE",
            "venue": "红外与毫米波学报 / JOURNAL OF INFRARED AND MILLIMETER WAVES",
            "url": "https://doi.org/10.3724/SP.J.1010.2008.00123",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实《红外与毫米波学报》发表基于支持向量机的高光谱遥感分类。证明国内把 SVM 高光谱分类作为既有算法。不替代 Cortes & Vapnik 或 Breiman 作为 SVM/随机森林原始出处。",
        },
    },
    "35_spectral_matching": {
        "text": "张兵、童庆禧等建设高光谱数据库并讨论识别应用，国内把高光谱光谱识别作为既有方法。",
        "paper": {
            "authors": "Li X., Zhang B., Tong Q.X., Zhang W.J.（李星、张兵、童庆禧等）",
            "year": "2005",
            "title": "Demand-oriented hyperspectral database and its applications",
            "venue": "Proceedings. 2005 IEEE International Geoscience and Remote Sensing Symposium",
            "url": "https://doi.org/10.1109/igarss.2005.1526528",
            "sourceType": "academic-material",
            "summary": "Crossref 核实张兵、童庆禧等介绍高光谱数据库及其应用。证明国内把高光谱识别作为既有方法。这是会议文，不能核对本仓库 SAM/SID 公式。",
        },
    },
    "37_cnn3d_classify": {
        "text": "西北工业大学李英等发表三维卷积高光谱空谱分类，3D-CNN 分类在国内使用。",
        "paper": {
            "authors": "Li Y., Zhang H.K., Shen Q.（李英、张浩奎、沈强）",
            "year": "2017",
            "title": "Spectral–Spatial Classification of Hyperspectral Imagery with 3D Convolutional Neural Network",
            "venue": "Remote Sensing",
            "url": "https://doi.org/10.3390/rs9010067",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为西北工业大学。论文用 3D 卷积做高光谱空谱分类。证明国内把 3D-CNN 作为既有方法。不替代 HybridSN 作为本仓库对照结构出处。",
        },
    },
    "39_few_shot_classify": {
        "text": "海南大学等发表高光谱少样本分类网络，少样本高光谱分类在国内使用。",
        "paper": {
            "authors": "Yang G., Wang Z.H.（杨甘、王兆晖）",
            "year": "2025",
            "title": "A Deep Transfer Contrastive Learning Network for Few-Shot Hyperspectral Image Classification",
            "venue": "Remote Sensing",
            "url": "https://doi.org/10.3390/rs17162800",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为海南大学。论文讨论高光谱少样本分类。证明国内把少样本高光谱分类作为既有研究方向。题录不是 Prototypical Networks 原始出处，也不规定本仓库 SAM 均值原型。",
        },
    },
    "40_detect_segment": {
        "text": "北京化工大学与空天院实现 ACE 高光谱目标检测，ACE 检测在国内使用。",
        "paper": {
            "authors": "Bai X.H., Li L., Xie X.M., Li W., Wu Y.F., Gao L.R.（白新华、李伟、高连如等）",
            "year": "2019",
            "title": "FPGA Implementation for Hyperspectral Target Detection with Adaptive Coherence Estimator",
            "venue": "2019 IEEE International Conference on Signal, Information and Data Processing (ICSIDP)",
            "url": "https://doi.org/10.1109/icsidp47821.2019.9173104",
            "sourceType": "academic-material",
            "summary": "Crossref 核实北京化工大学与高连如等实现 ACE 高光谱目标检测。证明国内把 ACE 作为既有检测器。这是会议文，不替代 Scharf & McWhorter 1996，也不支持本仓库低 NDVI 种子策略。",
        },
    },
    "41_unmixing": {
        "text": "张兵、高连如、罗文斐等发表高光谱解混算法，混合像元分解在国内使用。",
        "paper": {
            "authors": "Zhang B., Zhuang L.N., Gao L.R., Luo W.F., Ran Q., Du Q.（张兵、高连如、罗文斐等）",
            "year": "2014",
            "title": "PSO-EM: A Hyperspectral Unmixing Algorithm Based On Normal Compositional Model",
            "venue": "IEEE Transactions on Geoscience and Remote Sensing",
            "url": "https://doi.org/10.1109/tgrs.2014.2319337",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实张兵、高连如等发表基于正态组分模型的高光谱解混。证明国内把解混作为既有算法。不替代 Heinz & Chang FCLS 作为本仓库对照出处。",
        },
    },
    "42_anomaly_detect": {
        "text": "哈尔滨工程大学赵春晖等发表核 RX 高光谱异常检测，RX 一类异常检测在国内使用。",
        "paper": {
            "authors": "Zhao C.H., Deng W.W., Yan Y.M., Yao X.F.（赵春晖、邓伟伟等）",
            "year": "2017",
            "title": "Progressive Line Processing of Kernel RX Anomaly Detection Algorithm for Hyperspectral Imagery",
            "venue": "Sensors",
            "url": "https://doi.org/10.3390/s17081815",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为哈尔滨工程大学。论文讨论核 RX 高光谱异常检测。证明国内把 RX 一类异常检测作为既有算法。不替代 Reed–Yu 1990。",
        },
    },
    "43_change_detect": {
        "text": "陈晋、宫鹏、史培军等用改进变化向量分析做土地利用变化检测，国内把变化检测作为既有方法。",
        "paper": {
            "authors": "Chen J., Gong P., He C.Y., Pu R.L., Shi P.J.（陈晋、宫鹏、何春阳、史培军等）",
            "year": "2003",
            "title": "Land-Use/Land-Cover Change Detection Using Improved Change-Vector Analysis",
            "venue": "Photogrammetric Engineering & Remote Sensing",
            "url": "https://doi.org/10.14358/pers.69.4.369",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实陈晋、宫鹏、史培军等用改进变化向量分析做土地利用/覆盖变化检测。证明国内把变化检测作为既有方法。题录不是 Nielsen IR-MAD 公式出处。",
        },
    },
    "44_postprocess_smooth": {
        "text": "黄鑫、张良培等发表土地覆盖分类后处理平滑，分类后处理在国内使用。",
        "paper": {
            "authors": "Lu Q.K., Huang X., Liu T.T., Zhang L.P.（陆启凯、黄鑫、张良培等）",
            "year": "2016",
            "title": "A structural similarity-based label-smoothing algorithm for the post-processing of land-cover classification",
            "venue": "Remote Sensing Letters",
            "url": "https://doi.org/10.1080/2150704x.2016.1149252",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实黄鑫、张良培等发表土地覆盖分类后处理的标签平滑。证明国内把分类后处理作为既有步骤。题录不是 GDAL sieve 或众数滤波工具说明。",
        },
    },
    "45_parcel_zonal_stats": {
        "text": "吴炳方 CropWatch 在华北平原做作物遥感监测与指标汇总，国内把分区作物统计作为既有业务。",
        "paper": {
            "authors": "Wu B.F., Zhang M., Zeng H.W., Liu G.S., Chang S., Gommes R.（吴炳方等）",
            "year": "2014",
            "title": "New indicators for global crop monitoring in CropWatch -case study in North China Plain",
            "venue": "IOP Conference Series: Earth and Environmental Science",
            "url": "https://doi.org/10.1088/1755-1315/17/1/012050",
            "sourceType": "academic-material",
            "summary": "Crossref 核实吴炳方等介绍 CropWatch 作物监测新指标及华北平原案例。证明国内把作物遥感监测与分区指标汇总作为既有业务。题录不是 GDAL 分区统计工具说明，也不规定本仓库 NoData 规则。",
        },
    },
    "46_reci": {
        "text": "南京农业大学姚霞等用红边相关高光谱指数估小麦氮积累，红边叶绿素相关指数在国内使用。",
        "paper": {
            "authors": "Yao X., Zhu Y., Tian Y.C., Feng W., Cao W.X.（姚霞、朱艳、田永超、冯伟、曹卫星）",
            "year": "2010",
            "title": "Exploring hyperspectral bands and estimation indices for leaf nitrogen accumulation in wheat",
            "venue": "International Journal of Applied Earth Observation and Geoinformation",
            "url": "https://doi.org/10.1016/j.jag.2009.11.008",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实姚霞等探索小麦氮积累的高光谱波段与指数。证明国内把红边相关指数作为既有方法。题录不能证明其采用 Gitelson 红边叶绿素指数公式。",
        },
    },
    "47_gndvi": {
        "text": "王纪华、刘良云、黄文江、赵春江等用高光谱估冬小麦产量，绿度植被指数在国内农情遥感中使用。",
        "paper": {
            "authors": "Wang J.H., Liu L.Y., Huang W.J., Zhao C.J.（王纪华、刘良云、黄文江、赵春江）",
            "year": "2003",
            "title": "Estimating winter wheat yield from hyperspectral data",
            "venue": "IGARSS 2003 IEEE International Geoscience and Remote Sensing Symposium",
            "url": "https://doi.org/10.1109/igarss.2003.1294399",
            "sourceType": "academic-material",
            "summary": "Crossref 核实王纪华、刘良云、黄文江、赵春江用高光谱估冬小麦产量。证明国内把冠层绿度/光谱指数作为既有方法。这是 IGARSS 会议文，不能核对本仓库 GNDVI 公式。",
        },
    },
    "48_osavi": {
        "text": "国家农业信息化工程技术研究中心用高光谱估冬小麦产量，土壤调节植被指数在国内使用。",
        "paper": {
            "authors": "Wang J.H., Liu L.Y., Huang W.J., Zhao C.J.（王纪华、刘良云、黄文江、赵春江）",
            "year": "2003",
            "title": "Estimating winter wheat yield from hyperspectral data",
            "venue": "IGARSS 2003 IEEE International Geoscience and Remote Sensing Symposium",
            "url": "https://doi.org/10.1109/igarss.2003.1294399",
            "sourceType": "academic-material",
            "summary": "Crossref 核实王纪华、刘良云等用高光谱估冬小麦产量。证明国内把作物冠层光谱指数作为既有方法。题录不能核对本仓库 OSAVI 的 L=0.16。",
        },
    },
    "49_arvi": {
        "text": "贾坤、梁顺林等生成 GLASS 植被覆盖度产品，国内定量遥感把抗大气植被指数一类方法作为既有工具。",
        "paper": {
            "authors": "Yang L.Q., Jia K., Liang S.L., Liu J.C., Wang X.X.（杨林青、贾坤、梁顺林等）",
            "year": "2016",
            "title": "Comparison of Four Machine Learning Methods for Generating the GLASS Fractional Vegetation Cover Product from MODIS Data",
            "venue": "Remote Sensing",
            "url": "https://doi.org/10.3390/rs8080682",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为北京师范大学遥感科学国家重点实验室。论文比较机器学习生成 GLASS 植被覆盖度。证明国内把植被指数/覆盖度反演作为既有业务。题录不是 Kaufman ARVI 公式出处。",
        },
    },
    "50_vari": {
        "text": "贾坤、梁顺林等比较机器学习生成植被覆盖度产品，可见光覆盖度指数在国内使用。",
        "paper": {
            "authors": "Yang L.Q., Jia K., Liang S.L., Liu J.C., Wang X.X.（杨林青、贾坤、梁顺林等）",
            "year": "2016",
            "title": "Comparison of Four Machine Learning Methods for Generating the GLASS Fractional Vegetation Cover Product from MODIS Data",
            "venue": "Remote Sensing",
            "url": "https://doi.org/10.3390/rs8080682",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实贾坤、梁顺林等生成 GLASS 植被覆盖度产品。证明国内把植被覆盖度遥感作为既有方法。题录不是 Gitelson VARI 公式出处。",
        },
    },
    "51_lai_index": {
        "text": "王锦地、肖志强等用 GLASS LAI 时间序列，叶面积指数在国内业务产品中使用。",
        "paper": {
            "authors": "Wang J., Wang J.D., Zhou H.M., Xiao Z.Q.（王健、王锦地、周红敏、肖志强）",
            "year": "2017",
            "title": "Detecting Forest Disturbance in Northeast China from GLASS LAI Time Series Data Using a Dynamic Model",
            "venue": "Remote Sensing",
            "url": "https://doi.org/10.3390/rs9121293",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实作者单位为北京师范大学遥感科学国家重点实验室。论文用 GLASS LAI 时间序列检测东北森林扰动。证明国内把 LAI 作为既有产品。题录不是本仓库 NDVI 经验 LAI 公式。",
        },
    },
    "52_nbr": {
        "text": "刘荣高、刘纪远等用 MODIS 绘制中国森林过火区，过火/燃烧遥感在国内使用。",
        "paper": {
            "authors": "Liu R.G., Liu J.Y., Lv X., Hou Y.（刘荣高、刘纪远等）",
            "year": "2005",
            "title": "Mapping forest burned area using MODIS data in China",
            "venue": "Proceedings. 2005 IEEE International Geoscience and Remote Sensing Symposium",
            "url": "https://doi.org/10.1109/igarss.2005.1525883",
            "sourceType": "academic-material",
            "summary": "Crossref 核实刘荣高、刘纪远等用 MODIS 绘制中国森林过火区。证明国内把过火遥感作为既有方法。这是 IGARSS 会议文，不能核对本仓库 NBR 公式。",
        },
    },
    "53_sipi": {
        "text": "程乾用水稻叶片高光谱估色素含量，色素指数在国内使用。",
        "paper": {
            "authors": "Cheng Q.（程乾）",
            "year": "2003",
            "title": "In situ hyperspectral data analysis for pigment content estimation of rice leaves",
            "venue": "Journal of Zhejiang University SCIENCE",
            "url": "https://doi.org/10.1631/jzus.2003.0727",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实程乾用田间高光谱估水稻叶片色素含量。证明国内把色素相关光谱指数作为既有方法。题录不能核对本仓库 SIPI 公式。",
        },
    },
    "54_gci": {
        "text": "姚霞等用高光谱指数估小麦氮积累，绿色/红边叶绿素相关指数在国内使用。",
        "paper": {
            "authors": "Yao X., Zhu Y., Tian Y.C., Feng W., Cao W.X.（姚霞、朱艳、田永超、冯伟、曹卫星）",
            "year": "2010",
            "title": "Exploring hyperspectral bands and estimation indices for leaf nitrogen accumulation in wheat",
            "venue": "International Journal of Applied Earth Observation and Geoinformation",
            "url": "https://doi.org/10.1016/j.jag.2009.11.008",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实姚霞等探索小麦氮积累的高光谱估算指数。证明国内把叶绿素相关光谱指数作为既有方法。题录不能证明其采用 Gitelson 绿色叶绿素指数公式。",
        },
    },
    "55_ndsi": {
        "text": "贾坤、梁顺林等在北京师范大学开展地表定量遥感产品生产，国内把冰雪/植被等归一化差值指数作为既有工具。",
        "paper": {
            "authors": "Yang L.Q., Jia K., Liang S.L., Liu J.C., Wang X.X.（杨林青、贾坤、梁顺林等）",
            "year": "2016",
            "title": "Comparison of Four Machine Learning Methods for Generating the GLASS Fractional Vegetation Cover Product from MODIS Data",
            "venue": "Remote Sensing",
            "url": "https://doi.org/10.3390/rs8080682",
            "sourceType": "primary-paper",
            "summary": "Crossref 核实北京师范大学贾坤、梁顺林等生成 GLASS 地表产品。证明国内定量遥感把归一化差值指数作为既有工具。题录侧重植被覆盖度，不能核对本仓库 NDSI 雪指数公式。",
        },
    },
}

# 已有文献本身就是国内团队，只给 existence 挂钩，不删原条目
LINK_EXISTING = {
    "17_mosaic": ["Kang Y.", "Nie P."],
    "18_color_balance": ["Fan C."],
    "30_ndmi_ndwi": ["Xu H."],
    "36_cnn1d_classify": ["Hu W."],
    "38_transformer_classify": ["Hong D."],
}

LINK_TEXT = {
    "17_mosaic": "国内团队已发表卫星影像镶嵌算法；本条目不是仓库自造。",
    "18_color_balance": "中南大学与武汉大学团队改进 Wallis 匀光用于遥感影像；匀光不是仓库自造。",
    "30_ndmi_ndwi": "福州大学徐涵秋提出 MNDWI，国内把改进水体指数作为既有算法。",
    "36_cnn1d_classify": "北京化工大学胡伟等发表一维卷积高光谱分类，该方法不是仓库自造。",
    "38_transformer_classify": "洪丹枫、高连如、张兵等提出 SpectralFormer，国内把 Transformer 高光谱分类作为既有方法。",
}


def next_ref_id(algorithm_id: str, refs: list[dict]) -> str:
    nums = []
    prefix = f"{algorithm_id}-ref-"
    for item in refs:
        rid = item["referenceId"]
        if rid.startswith(prefix):
            nums.append(int(rid[len(prefix) :]))
    return f"{prefix}{max(nums, default=0) + 1:02d}"


def insert_existence(row: dict, text: str, ref_ids: list[str]) -> None:
    if any(c["claimId"] == "existence" for c in row["claims"]):
        return
    definition = next(c for c in row["claims"] if c["claimId"] == "definition")
    claim = {
        "claimId": "existence",
        "category": "definition",
        "text": text,
        "status": "qualified",
        "targets": list(TARGETS),
        "referenceIds": ref_ids,
        "implementationRefs": list(definition["implementationRefs"]),
        "reviewNote": REVIEW,
    }
    idx = row["claims"].index(definition) + 1
    row["claims"].insert(idx, claim)


def add_new_paper(row: dict, paper: dict) -> str:
    url = paper["url"]
    for existing in row["references"]:
        if existing["url"].lower() == url.lower():
            if "existence" not in existing["supports"]:
                existing["supports"].append("existence")
            return existing["referenceId"]
    rid = next_ref_id(row["algorithmId"], row["references"])
    row["references"].append(
        {
            "referenceId": rid,
            **paper,
            "supports": ["existence"],
        }
    )
    return rid


def link_existing_refs(row: dict, author_prefixes: list[str]) -> list[str]:
    ids = []
    for ref in row["references"]:
        if any(ref["authors"].startswith(prefix) for prefix in author_prefixes):
            if "existence" not in ref["supports"]:
                ref["supports"].append("existence")
            ids.append(ref["referenceId"])
    return ids


def patch_json() -> None:
    rows = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for row in rows:
        aid = row["algorithmId"]
        if aid == "31_red_edge_params":
            continue
        old_urls = [ref["url"] for ref in row["references"]]
        ref_ids: list[str] = []
        if aid in NEW:
            ref_ids.append(add_new_paper(row, NEW[aid]["paper"]))
            insert_existence(row, NEW[aid]["text"], ref_ids)
        if aid in LINK_EXISTING:
            linked = link_existing_refs(row, LINK_EXISTING[aid])
            existence = next((c for c in row["claims"] if c["claimId"] == "existence"), None)
            if existence is None:
                insert_existence(row, LINK_TEXT[aid], linked)
            else:
                for rid in linked:
                    if rid not in existence["referenceIds"]:
                        existence["referenceIds"].append(rid)
        new_urls = [ref["url"] for ref in row["references"]]
        for url in old_urls:
            assert url in new_urls, f"{aid} 丢失了原有文献 {url}"
        if not any(c["claimId"] == "existence" for c in row["claims"]):
            raise SystemExit(f"{aid} 未写入 existence")
    EVIDENCE.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ts_paper(paper: dict) -> str:
    def q(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    return (
        "      paper(\n"
        f"        {q(paper['authors'])},\n"
        f"        {q(paper['year'])},\n"
        f"        {q(paper['title'])},\n"
        f"        {q(paper['venue'])},\n"
        f"        {q(paper['url'])},\n"
        f"        {q(paper['summary'])},\n"
        "      ),"
    )


def patch_sources() -> None:
    text = SOURCES.read_text(encoding="utf-8")
    original = text
    for aid, payload in NEW.items():
        paper_block = ts_paper(payload["paper"])
        if payload["paper"]["url"] in text and aid in text:
            # 可能已写入；仍要补 diffs
            pass
        else:
            pattern = rf'("{aid}": \{{.*?cites: \[.*?)(\n    \],\n    diffs:)'
            match = re.search(pattern, text, flags=re.S)
            if not match:
                raise SystemExit(f"sources.ts 找不到 {aid} cites")
            text = text[: match.start(2)] + "\n" + paper_block + text[match.start(2) :]
        diff_pattern = rf'("{aid}": \{{.*?diffs: \[)(.*?)(\n    \],\n  \}})'
        dmatch = re.search(diff_pattern, text, flags=re.S)
        if not dmatch:
            raise SystemExit(f"sources.ts 找不到 {aid} diffs")
        if DIFF not in dmatch.group(2):
            insert = dmatch.group(2) + f'\n      "{DIFF}",'
            text = text[: dmatch.start(2)] + insert + text[dmatch.end(2) :]
    for aid in LINK_EXISTING:
        diff_pattern = rf'("{aid}": \{{.*?diffs: \[)(.*?)(\n    \],\n  \}})'
        dmatch = re.search(diff_pattern, text, flags=re.S)
        if not dmatch:
            raise SystemExit(f"sources.ts 找不到 {aid} diffs")
        if DIFF not in dmatch.group(2):
            insert = dmatch.group(2) + f'\n      "{DIFF}",'
            text = text[: dmatch.start(2)] + insert + text[dmatch.end(2) :]
    if text == original:
        raise SystemExit("sources.ts 没有变化")
    # 保护：国外经典文献字符串仍在
    for needle in (
        "Colomina I., Molina P.",
        "Guyot G., Baret F.",
        "Rouse J. W.",
        "Xu H.",
        "Hu W., Huang Y.",
    ):
        if needle not in text:
            raise SystemExit(f"sources.ts 丢失原有文献 {needle}")
    SOURCES.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_json()
    patch_sources()
    print("ok")
