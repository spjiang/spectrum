"""L3 指数、分类与解混三栏知识：算法算什么、精度靠什么、大模型可做/禁止。"""

from __future__ import annotations

from typing import Any

GROUP_ORDER = (
    ("index", "指数与反演"),
    ("classify", "分类与识别"),
    ("mix", "解混 / 异常 / 变化"),
)

_INDEX_IDS = (
    "27_ndvi",
    "28_ndre",
    "29_evi_savi",
    "30_ndmi_ndwi",
    "31_red_edge_params",
    "32_regression_inversion",
    "33_physical_inversion",
    "46_reci",
    "47_gndvi",
    "48_osavi",
    "49_arvi",
    "50_vari",
    "51_lai_index",
    "52_nbr",
    "53_sipi",
    "54_gci",
    "55_ndsi",
)
_CLASSIFY_IDS = (
    "34_svm_rf_classify",
    "35_spectral_matching",
    "36_cnn1d_classify",
    "37_cnn3d_classify",
    "38_transformer_classify",
    "39_few_shot_classify",
    "40_detect_segment",
)
_MIX_IDS = ("41_unmixing", "42_anomaly_detect", "43_change_detect")


def _build_prompt(
    title: str,
    definition: str,
    method: str,
    accuracy: list[str],
    may: list[str],
    must_not: list[str],
) -> str:
    """按算法拼一份要求现象/边界/下一步的系统提示词。"""
    acc_txt = "\n".join(f"- {line}" for line in accuracy)
    may_txt = "\n".join(f"- {line}" for line in may)
    no_txt = "\n".join(f"- {line}" for line in must_not)
    return (
        f"你是高光谱算法「{title}」的结果解读模块。\n"
        f"算法定义：{definition}\n"
        f"计算方法：{method}\n"
        "若提到下游应用，必须写明那是后续用法，不是本页已交付产品。\n"
        "精度前提（结论必须尊重这些条件）：\n"
        f"{acc_txt}\n"
        "你可以：\n"
        f"{may_txt}\n"
        "你禁止：\n"
        f"{no_txt}\n"
        "只返回 JSON {\"runComment\": \"...\"}。runComment 用 Markdown（标题、列表、加粗），按现象、边界、下一步组织。\n"
        "必须对照用户消息里的 fieldGuides 解读 data 原始返回，禁止只复述 min/max/mean。\n"
        "1. 现象：结合质量状态和字段说明，解释原始返回对「"
        f"{title}"
        "」意味着什么。数字最多点一次，必须服务于判断。禁止只复述 min/max/mean。\n"
        "2. 边界：说明本次能支持什么、不能支持什么。必须出现「不是处方」，不得输出剂量或业务动作。\n"
        "3. 下一步：给出对本算法输入、参数与返回字段的检查项。不要改推其他算法，不要开处方。\n"
        "禁止只写「这是 testdata」。不得重算或改写公式。不得根据预览 PNG 颜色定量。"
        "不得要求或使用立方体/GeoTIFF。"
    )


def _rich_readout(title: str, definition: str, may: list[str], must_not: list[str], accuracy: list[str]) -> list[str]:
    """无大模型时的领域解读，禁止只回显三个数字。"""
    may0 = may[0] if may else ""
    no0 = must_not[0] if must_not else ""
    acc = accuracy[-1] if accuracy else ""
    return [
        (
            f"{title}：全图均值 {{mean:.2f}}，范围 {{min:.2f}}～{{max:.2f}}。"
            f"{definition}最低值与最高值要分开读，不能把极值当成整景结论。"
        ),
        f"{no0}本次只支持相对格局判断，不是处方，也不能当业务验收。",
        f"{may0}{acc}",
    ]


def _item(
    aid: str,
    title: str,
    group: str,
    definition: str,
    method: str,
    inp: str,
    output: str,
    accuracy: list[str],
    may: list[str],
    must_not: list[str],
    readout: list[str] | None = None,
) -> dict[str, Any]:
    """构造一条可校验的知识记录。"""
    must_not = list(must_not)
    for guard in ("不得推荐其他算法。", "不得输出处方或业务决策。"):
        if guard not in must_not:
            must_not.append(guard)
    return {
        "id": aid,
        "title": title,
        "group": group,
        "definition": definition,
        "method": method,
        "input": inp,
        "output": output,
        "accuracy": accuracy,
        "llmMay": may,
        "llmMustNot": must_not,
        "llmPrompt": _build_prompt(title, definition, method, accuracy, may, must_not),
        "readout": readout or _rich_readout(title, definition, may, must_not, accuracy),
    }


ALGORITHMS: dict[str, dict[str, Any]] = {
    "27_ndvi": _item(
        "27_ndvi",
        "NDVI植被指数",
        "index",
        "归一化差值植被指数 NDVI = (近红外反射率 − 红光反射率) / (近红外反射率 + 红光反射率)，用于表征植被绿度、活力及冠层覆盖状况。",
        "NDVI = (NIR − RED) / (NIR + RED)",
        "地表反射率数据，以及可映射至红光和近红外区域的波段；典型红光约 630–690 nm、近红外约 760–900 nm，具体按传感器光谱响应选择。",
        "单波段 NDVI GeoTIFF，理论值域为 −1～1。",
        [
            "输入应优先使用经过辐射定标及必要预处理的反射率，不建议直接使用原始 DN。",
            "按传感器光谱响应选择红光与近红外；典型范围约 630–690 nm 与 760–900 nm，不能死记演示数据默认 2/3。",
            "云、云影、NoData 应先掩膜，再做全图或地块统计。",
            "高叶面积条件下 NDVI 容易饱和，对生物量增量的敏感性下降，不能直接作为叶绿素含量或生物量定量产品。",
        ],
        [
            "对照 data.red_band、data.nir_band 说明本次索引是否只适用于演示数据，生产须按传感器光谱响应重选红光与近红外。",
            "把 min、max、mean、shape、format 读成统计口径与产物形态：全图算术统计不是地块结论，format 不是定标证明。",
            "说明高叶面积时容易饱和、对增量不敏感，这是方法边界，不是把阈值切碎就能消除。",
            "指出 NDVI 不能直接作为叶绿素含量或生物量定量产品，也不是养分含量。",
        ],
        [
            "不得重算或改写 NDVI 公式。",
            "不得根据预览 PNG 颜色下定量结论或业务决策。",
            "不得把立方体或 GeoTIFF 送进上下文。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是全部像元的算术统计，不是地块结论。低值先排除水体、阴影或未掩膜残差；高值接近 1 时增量会被压缩，这是公式饱和，不是把阈值切碎就能消除。",
            "NDVI 描述绿度与冠层状况的相对格局，不能直接作为叶绿素含量或生物量定量产品，也不是养分含量。",
            "应优先用定标反射率，并按传感器光谱响应选择红光与近红外。这是演示数据 的相对判断，不能当业务验收。",
        ],
    ),
    "28_ndre": _item(
        "28_ndre",
        "NDRE红边植被指数",
        "index",
        "归一化差值红边指数 NDRE = (近红外反射率 − 红边反射率) / (近红外反射率 + 红边反射率)，以红边代替红光。",
        "NDRE = (NIR − RE) / (NIR + RE)",
        "含真实红边波段的反射率立方体及红边、近红外索引。",
        "单波段 NDRE GeoTIFF。",
        [
            "必须使用真实红边通道，不能用红光或近红外冒充。",
            "按波长表选择约 705–740 nm 与稳定近红外平台。",
            "跨传感器比较须固定红边中心波长和预处理。",
            "输入须为反射率并掩膜云影与 NoData。",
        ],
        [
            "对照 data.re_band、data.nir_band 说明本次索引是否落在真实红边和近红外平台。",
            "把 min、max、mean、shape、format 读成统计口径与产物形态：全图算术统计不是地块结论。",
            "指出没有真实红边通道时本公式没有物理意义。",
        ],
        [
            "不得把 NDRE 说成叶绿素或施氮的毫克数。",
            "不得根据 PNG 色带下定量营养结论。",
            "不得把立方体送进上下文。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。红边指数对叶绿素变化更敏感，低值是相对低值，不是含量诊断。",
            "NDRE 不是叶绿素毫克数。没有真实红边通道时这张图没有物理意义。",
            "须按波长选择红边与近红外。这是演示数据，不能当业务验收。",
        ],
    ),
    "29_evi_savi": _item(
        "29_evi_savi",
        "EVI/SAVI/MSAVI",
        "index",
        "相对 NDVI：SAVI 用固定土壤因子 L（分母加 L 并乘 1+L）；MSAVI 由红光与近红外自适应土壤项；EVI 另加蓝光项与增益，密冠层更晚饱和。",
        "EVI=2.5(N−R)/(N+6R−7.5B+1)；SAVI=(1+L)(N−R)/(N+R+L)；MSAVI=0.5(2N+1−√((2N+1)²−8(N−R)))",
        "蓝、红、近红外反射率；SAVI 土壤系数 L。",
        "按 EVI、SAVI、MSAVI 分别写出的三个单波段 GeoTIFF。",
        [
            "三个索引必须是同尺度反射率，并按中心波长核验。",
            "蓝光低信噪或阴影重时重点检查 EVI 分母。",
            "L 应按覆盖度调整，默认 0.5 不是所有地块最优。",
            "三个文件要分别读，不能平均成一个长势分。",
        ],
        [
            "按文件分别解读 evi.tif、savi.tif、msavi.tif，不能把一个均值当成三个指数已经各自校正。",
            "说明 L=0 时 SAVI 退化成 NDVI 形式，这是本公式性质。",
            "提醒本仓库 EVI 系数是固定实现，迁到其他传感器可能失真。",
        ],
        [
            "不得把三个指数直接当成 LAI、氮或产量。",
            "不得改写 EVI/SAVI 公式系数冒充新算法。",
            "不得根据假彩色合成图解读类别。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是 EVI/SAVI/MSAVI 三个文件里被折叠进统计的相对量，必须回到 evi.tif、savi.tif、msavi.tif 分别读，不能把一个均值当成「已经抑制了土壤或大气」。",
            "三个指数都不是 LAI、氮或产量。L=0.5 只是演示数据默认。",
            "必须回到三个单波段文件分别读。这是演示数据，不能当业务验收。",
        ],
    ),
    "30_ndmi_ndwi": _item(
        "30_ndmi_ndwi",
        "NDMI/NDWI/MNDWI",
        "index",
        "NDMI = (近红外 − 短波红外)/(近红外 + 短波红外)，表征冠层水分；NDWI = (绿光 − 近红外)/(绿光 + 近红外)，圈定开阔水体；MNDWI 用绿光与短波红外。",
        "NDMI=(NIR−SWIR)/(NIR+SWIR)；NDWI=(GREEN−NIR)/(GREEN+NIR)；MNDWI=(GREEN−SWIR)/(GREEN+SWIR)",
        "绿光、近红外和真实短波红外反射率。",
        "三个单波段 GeoTIFF：ndmi.tif、ndwi.tif、mndwi.tif。",
        [
            "NDMI/MNDWI 必须有真实 SWIR，不能用末波段冒充。",
            "写清本仓库 NDWI 是 McFeeters，不是 Gao 的 (NIR−SWIR)。",
            "掩膜镜面反射、云影和低信噪 SWIR。",
            "城市阴影、湿土、薄膜可能与水体指数混淆。",
        ],
        [
            "按波段区分 NDMI、NDWI、MNDWI 各自的公式与所需波段。",
            "没有 SWIR 时明确说 NDMI/MNDWI 无物理意义。",
            "提醒同名 NDWI 版本不能混比。",
        ],
        [
            "不得把 McFeeters 与 Gao 的 NDWI 当成同一个数。",
            "不得给出绝对含水量或固定全国水体阈值。",
            "不得把立方体送进上下文。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是 NDMI/NDWI/MNDWI 三个文件里被折叠进统计的相对量，必须回到 ndmi.tif、ndwi.tif、mndwi.tif 分别读，不能把一个均值当成「已经分清水和叶子」。",
            "没有真实 SWIR 时 NDMI/MNDWI 没有物理意义；McFeeters 与 Gao 的 NDWI 不能混比，也不能给出绝对含水量。",
            "湿土、阴影、薄膜会抬高水体指数，先目视抽检再谈阈值。这是演示数据，不能当业务验收。",
        ],
    ),
    "31_red_edge_params": _item(
        "31_red_edge_params",
        "红边位置与光谱特征参数",
        "index",
        "红边位置四点线性内插：REP = 700 + 40×((R670+R780)/2 − R700)/(R740 − R700)。",
        "Guyot：REP = 700 + 40 × ((R670+R780)/2 − R700) / (R740 − R700)",
        "覆盖 670–780 nm、带可靠波长轴的反射率立方体。",
        "Guyot REP、振幅和导数 REP 三波段 GeoTIFF。",
        [
            "优先使用传感器真实波长，禁止用假等间隔轴当纳米真相。",
            "红边区要有足够窄带采样，宽带多光谱插值不可信。",
            "SG 窗口应小于红边主宽度，避免抹平或吃噪声。",
            "坏波段与低信噪会让导数峰乱跳。",
        ],
        [
            "解释叶绿素升高时 REP 常向长波移动，但不是绝对含量。",
            "指出只有稀疏窄带时 Guyot 四点不可靠。",
            "不能把单一位置参数当成含量。",
            "可指出国内文献已用红边位置/参数做氮、水分和叶面积指数研究，但不得把中文论文说成 Guyot 四点公式出处。",
        ],
        [
            "不得把 REP 纳米数说成叶绿素毫克数。",
            "不得在无波长标定时宣称位置精确。",
            "不得把整条连续光谱数组送进上下文。",
        ],
    ),
    "32_regression_inversion": _item(
        "32_regression_inversion",
        "经验回归反演",
        "index",
        "光谱经 SNV 后，用偏最小二乘回归映射到连续生化量。",
        "SNV 后 PLS：潜变量最大化 X 与 Y 的协方差，再预测整图",
        "光谱立方体与同尺寸真值图；成分数等训练参数。",
        "预测的连续量 GeoTIFF，以及训练/测试误差摘要。",
        [
            "真值必须与影像逐像元对齐，并有明确单位。",
            "评估应按地块或空间块留出，禁止只靠像元随机划分。",
            "成分数过多会过拟合，需同时看训练与测试误差。",
            "SNV 与波段集合要在训练和推断保持一致。",
        ],
        [
            "说明本次 R² 只对当前划分有效，不能当跨场景精度。",
            "提醒像元随机切分会造成空间泄漏、指标虚高。",
            "建议补地面样点后再谈定量。",
        ],
        [
            "不得把一次测试 R² 写成业务验收通过。",
            "不得在无真值时编造反演精度。",
            "不得把立方体或真值栅格送进上下文。",
        ],
    ),
    "33_physical_inversion": _item(
        "33_physical_inversion",
        "辐射传输物理反演",
        "index",
        "不用化验图，一次给出叶面积和叶绿素两张图，用来分清是叶子少还是叶子黄。PROSPECT 模拟叶片光学，SAIL 模拟冠层反射，耦合为 PROSAIL，用查找表匹配。",
        "构建 (LAI, Cab) LUT → RMSE（可选 SAM）→ 最优若干条平均",
        "地表反射率立方体（非 DN）、真实中心波长、太阳/观测几何；可调 n_lai、n_cab、best_frac、cost_method。",
        "lai.tif 看密不密，cab.tif 看绿不绿；另有 lut_size、best_n 和边界命中计数。",
        [
            "波长、反射率尺度必须与 LUT 模拟一致。",
            "混合像元和行距土壤会破坏纯冠层假设。",
            "固定其它生理参数时，结果只是表格上的候选解平均。",
            "边界格点要抽检，不能当可靠极值。",
        ],
        [
            "说明输出是 LUT 最优若干条的平均，不是全参数连续优化解。",
            "提醒土壤、叶倾角仍写死，不能当田间实测。",
            "指出缺少连续红边时匹配会偏。",
        ],
        [
            "不得把 LUT 命中值说成实验室化验结果。",
            "不得声称已经实现 Combal 先验。",
            "不得把查找表整表送进上下文。",
        ],
    ),
    "34_svm_rf_classify": _item(
        "34_svm_rf_classify",
        "SVM/随机森林分类",
        "classify",
        "支持向量机在核空间求最大间隔分类；随机森林由多棵决策树投票。",
        "SVM：核空间最大间隔；RF：多棵树投票。gt=0 为背景忽略",
        "反射率立方体与逐像元正整数标签。",
        "分类图及 OA/AA/Kappa 等测试摘要。",
        [
            "标签与影像必须同网格对齐，0 为背景忽略。",
            "正式评估用地块或空间块留出，不要像元随机对半切。",
            "类别不平衡时同时看 OA、AA、Kappa。",
            "SVM 输入需要统一尺度，否则会被高幅度波段主导。",
        ],
        [
            "解释 OA/AA/Kappa 各自回答什么问题。",
            "指出像元随机划分会让指标虚高。",
            "提醒背景像元被强制分类不代表地类存在。",
        ],
        [
            "不得把一次测试 OA 说成业务过关。",
            "不得根据分类预览色块编造未训练的类别。",
            "不得把标签栅格送进上下文。",
        ],
    ),
    "35_spectral_matching": _item(
        "35_spectral_matching",
        "光谱匹配分类(SAM)",
        "classify",
        "SAM 用像元与参考光谱的夹角分类；SID 用光谱作为概率分布的相对熵衡量差异。",
        "θ = arccos( x·e / (‖x‖‖e‖) )；分类 = 最小角端元",
        "反射率立方体与端元光谱表，波段必须对齐。",
        "类别图与最小角/散度图。",
        [
            "端元与影像波段数、顺序、反射率尺度必须一致。",
            "SAM 对整体增益不敏感，但不能消除混合像元。",
            "没有拒绝阈值时每个像元都会被硬分到某类。",
            "端元要覆盖主要材料且彼此可分。",
        ],
        [
            "说明高最小角仍被分类，是本实现限制不是高置信。",
            "提醒本算法输出唯一类别，混合像元仍会被硬分。",
            "指出 SID 与 SAM 分数不能互换。",
        ],
        [
            "不得把最小角说成概率或精度百分比。",
            "不得在端元错位时宣称匹配可靠。",
            "不得把端元 CSV 全文无过滤地送进上下文。",
        ],
    ),
    "36_cnn1d_classify": _item(
        "36_cnn1d_classify",
        "1D-CNN光谱分类",
        "classify",
        "一维卷积神经网络沿光谱维提取局部特征并做像元分类。",
        "Conv1d → ReLU → Pool → FC → Softmax",
        "标注像元光谱；波段顺序固定。",
        "逐像元分类图与测试摘要。",
        [
            "波段数量和顺序必须与训练时一致。",
            "空间上应按地块留出，避免邻域泄漏。",
            "短训轮数只够演示，不能当收敛模型。",
            "当前实现不使用空间邻域，碎斑是预期现象。",
            "当前未实现 RNN 分支。",
        ],
        [
            "说明这是小模型分类，不是通用大模型识图。",
            "提醒随机像元测试指标会虚高。",
            "指出预览碎斑不等于地物破碎。",
        ],
        [
            "不得宣称深度网络已经达到业务精度。",
            "不得把权重或立方体送进上下文重训。",
            "不得用一次 OA 替代独立验证。",
        ],
    ),
    "37_cnn3d_classify": _item(
        "37_cnn3d_classify",
        "2D/3D-CNN空谱分类",
        "classify",
        "HybridSN：先用三维卷积提取空谱局部特征，再用二维卷积压缩空间。",
        "PCA→P×P×C patch → Conv3d 空谱 → Conv2d → 分类",
        "立方体、标签与奇数 patch 边长。",
        "分类图与测试摘要。",
        [
            "相邻 patch 大量重叠，随机按样本切分会泄漏。",
            "patch 过大混入边界，过小退化为单像元。",
            "PCA 维数与训练推断必须一致。",
            "边缘填充会改变边界光谱，需抽检。",
        ],
        [
            "说明空谱 patch 能平滑碎斑，也会通过重叠扩大泄漏。",
            "提醒应按完整对象或地块分组切分。",
            "指出演示短训不能当 HybridSN 论文复现。",
        ],
        [
            "不得把演示 OA 写成论文级精度。",
            "不得要求大模型根据 PNG 重标类别。",
            "不得上传 patch 数组到上下文。",
        ],
    ),
    "38_transformer_classify": _item(
        "38_transformer_classify",
        "SpectralFormer光谱分类",
        "classify",
        "SpectralFormer：将相邻波段编为 token，用 Transformer 捕获光谱序列依赖。",
        "group=3 滑窗 token → 两层 Transformer + 残差",
        "固定波段顺序的标注立方体。",
        "逐像元分类图。",
        [
            "注意力不自动保证更高精度，必须在同一空间划分上读本次指标。",
            "波段预处理改变后权重不能直接复用。",
            "当前没有图结构 GCN，不要按图节点解释。",
            "样本少时过拟合风险高。",
        ],
        [
            "说明缩小网络已缩小，不是完整 SpectralFormer。",
            "提醒输出是已知类硬分类，没有未知类拒绝。",
            "短训指标只在本次划分协议内有效。",
        ],
        [
            "不得把 Transformer 说成通用视觉大模型。",
            "不得编造注意力图业务含义。",
            "不得把 token 序列送进上下文。",
        ],
    ),
    "39_few_shot_classify": _item(
        "39_few_shot_classify",
        "SAM均值原型少样本分类",
        "classify",
        "原型网络：每类支撑集均值作为原型，查询样本按到原型的距离分类。",
        "proto_k = mean(支持集_k)；ŷ = argmin SAM(x, proto)",
        "每类至少一个有效标签像元。",
        "分类图；指标仅在查询像元上计算。",
        [
            "支持点应覆盖类内变异，并与查询区空间分离。",
            "随机抽支持集会造成结果方差，单次种子不代表稳健。",
            "远离全部原型的未知地物仍会被硬分。",
            "类别过少 shots 时原型不稳定。",
            "当前没有可学习嵌入、源域预训练或迁移学习。",
        ],
        [
            "说明这是原型匹配，不是大模型少样本对话。",
            "提醒无 query 时不要解读那组指标。",
            "建议人工检查支持点是否落在纯像元。",
        ],
        [
            "不得把 shots=几 说成已经解决小样本问题。",
            "不得输出未出现在支持集中的新类名。",
            "不得把支持光谱数组送进上下文。",
        ],
    ),
    "40_detect_segment": _item(
        "40_detect_segment",
        "低NDVI种子ACE目标检测",
        "classify",
        "ACE 在白化背景空间中估计像元与目标光谱的自适应余弦，用于目标探测。",
        "ACE 分数 + 百分位阈值 + 连通域",
        "反射率立方体、红/近红外索引、百分位与最小斑块。",
        "得分图、掩膜和斑块矢量。",
        [
            "当前实现是 ACE 检测，不是深度学习语义分割。",
            "目标光谱由低 NDVI 自动构造，场景变了种子就变。",
            "百分位阈值只在本景有意义。",
            "斑块面积是像元数，要换算平方米需 GSD。",
        ],
        [
            "明确这是 ACE 检测实现，不是深度学习分割。",
            "解释高分只表示相对目标方向，不是概率。",
            "提醒目标光谱由低 NDVI 种子构造，分数与种子定义绑定。",
        ],
        [
            "不得把斑块说成已确认病虫害。",
            "不得把实现写成深度学习分割模型。",
            "不得根据预览圈病下处方。",
        ],
    ),
    "41_unmixing": _item(
        "41_unmixing",
        "混合像元分解",
        "mix",
        "FCLS：把像元表示为端元的线性组合，丰度非负且和为 1。",
        "x ≈ E a，a≥0，1ᵀa=1",
        "与影像对齐的端元矩阵，相同波段与尺度。",
        "K 张丰度图。",
        [
            "端元集合应覆盖主要材料且线性可分。",
            "丰度非负且和约为 1，同时检查重构残差。",
            "多光谱通道少时方程欠定，结果不稳。",
            "非线性混合（阴影、多次散射）会破坏模型。",
        ],
        [
            "说明丰度是线性模型下的相对贡献，不一定等于面积比例。",
            "提醒本算法输出连续比例，不是唯一类别标签。",
            "指出端元错了丰度图会看起来很完整但仍错。",
        ],
        [
            "不得把丰度写成质量分数或产量份额。",
            "不得在通道不足时宣称解混可靠。",
            "不得把端元矩阵送进上下文重解。",
        ],
    ),
    "42_anomaly_detect": _item(
        "42_anomaly_detect",
        "异常检测",
        "mix",
        "RX：目标光谱未知时，用背景协方差把像元马氏距离作为异常分数。",
        "D_RX = (x−μ)ᵀ Σ⁻¹ (x−μ)；LRX 用外窗估背景、挖内窗",
        "反射率立方体；局部窗参数。",
        "连续得分图与二值掩膜。",
        [
            "先做有效像元与坏波段掩膜，否则协方差被污染。",
            "高维波段需足够样本，否则 Σ 不稳定。",
            "LRX 窗太大丢局部，太小把目标当背景。",
            "异常不是类别标签，后续仍要人工或端元解释。",
        ],
        [
            "说明高分只是相对背景离群，不是已命名地物。",
            "提醒云影、饱和常被当成异常。",
            "建议结合真图位置抽检，不要全信掩膜。",
        ],
        [
            "不得把 RX 高分说成特定病害或入侵种。",
            "不得用固定全国阈值复用到新场景。",
            "不得把协方差矩阵送进上下文。",
        ],
    ),
    "43_change_detect": _item(
        "43_change_detect",
        "多时相变化检测",
        "mix",
        "IR-MAD：迭代加权典型相关，提取两期影像的统计变化并形成 χ² 强度。",
        "IR-MAD：迭代加权典型相关，χ² 大者为变化",
        "已配准、同波段、可比反射率的两期立方体。",
        "变化强度、χ² 与候选掩膜。",
        [
            "两期必须同网格、同波段顺序、亚像元配准。",
            "云影与 NoData 要做交集掩膜，否则尾部被污染。",
            "物候和几何差异会被当成变化，需归一化观测条件。",
            "输出是统计变化，不是变化类别或原因。",
        ],
        [
            "解释错位半个像元会在边缘制造假变化。",
            "提醒百分位掩膜只是本景相对阈值。",
            "建议先目视道路田埂，再信 χ² 热点。",
        ],
        [
            "不得把变化图说成灾损等级或原因定性。",
            "不得在未配准时宣称检测成立。",
            "不得把两期立方体送进上下文。",
        ],
    ),
    "44_postprocess_smooth": _item(
        "44_postprocess_smooth",
        "分类后处理平滑/小斑剔除",
        "catalog",
        "对类别栅格先做邻域众数滤波，再将小连通斑块替换为边界类别众数。",
        "众数滤波 → 连通域筛斑 → 边界众数填充",
        "单波段类别 ID 栅格，以及 window 与 min_pixels 参数。",
        "平滑后的 labels_tif、预览图、变更像元数和类别列表。",
        [
            "输入必须是离散类别 ID；连续指数或概率不得当作类别做众数。",
            "window 与 min_pixels 会直接改变边界和小目标，必须保留参数记录。",
            "边界众数替换不会提高原分类器精度，也不能恢复被误分的真实类别。",
            "类别 ID 的业务含义必须来自输入图的既有编码，不能从颜色推断。",
        ],
        [
            "对照 min_pixels、window、n_changed 与 classes 说明本次处理强度和涉及类别。",
            "指出 n_changed 只表示标签被改写的像元数，不表示纠错成功数。",
            "检查小目标、细线边界与孤立斑块是否被过度吞并。",
        ],
        [
            "不得把平滑后视觉更整齐写成精度提高。",
            "不得根据预览颜色编造类别、场景或原因。",
            "不得推荐其他算法，不得输出处方或业务决策。",
            "不得把类别栅格或 GeoTIFF 送进上下文。",
        ],
    ),
    "45_parcel_zonal_stats": _item(
        "45_parcel_zonal_stats",
        "地块汇总与专题统计",
        "catalog",
        "将单波段连续值或类别栅格按整景和可选 GeoJSON 地块汇总；统计只使用有限且不等于栅格 NoData 的像元。",
        "有效像元掩膜 → GeoJSON 栅格化 → 连续描述统计或分类计数/占比",
        "单波段 GeoTIFF、continuous/categorical 模式，以及可选地块 GeoJSON。",
        "report_json、可选地块文件、整景 scene 与逐地块 parcels 统计。",
        [
            "模式必须与输入语义一致：连续量不能转整数类别，类别 ID 不能按连续均值解读。",
            "NoData 与 NaN 必须排除；空有效区不会产生虚假 0，而应明确为空或失败。",
            "地块 CRS、栅格 transform 与多边形覆盖范围决定参与统计的有效像元集合。",
            "分类占比的分母、计数和主导类别只能基于同一有效像元集合。",
        ],
        [
            "对照 mode、n_parcels、n_parcels_with_pixels、scene 与 parcels 解释统计口径。",
            "连续模式只解读 mean/std/min/max 与分位数；分类模式只解读类别计数和面积比例。",
            "指出无有效像元地块的 empty 状态，避免把缺测解释为零值。",
        ],
        [
            "不得预设农业、林业或任何业务场景。",
            "不得把统计相关性写成原因、诊断或行动建议。",
            "不得推荐其他算法，不得输出处方或业务决策。",
            "不得把 GeoTIFF、GeoJSON 全文或地块坐标送进上下文。",
        ],
    ),
    "46_reci": _item(
        "46_reci",
        "RECI红边叶绿素指数",
        "index",
        "红边叶绿素指数 RECI = 近红外反射率 / 红边反射率 − 1，属于叶绿素相关相对指数。",
        "RECI = NIR/RE − 1",
        "含真实红边与近红外的反射率立方体。",
        "单波段 reci.tif。",
        [
            "必须使用真实红边通道，不能用红光或近红外冒充。",
            "输入须为反射率，并掩膜云影与 NoData。",
            "值域不是 −1～1，高值只表示比值大。",
            "不能直接作为叶绿素毫克数。",
        ],
        [
            "对照 data.re_band、data.nir_band 说明本次是否落在真实红边。",
            "把 min、max、mean 读成全图算术统计，不是地块结论。",
            "指出没有真红边时本公式没有物理意义。",
        ],
        [
            "不得把 RECI 说成叶绿素毫克数。",
            "不得根据 PNG 色带下定量营养结论。",
            "不得把立方体送进上下文。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是比值减 1，不是叶绿素含量。",
            "没有真实红边通道时这张图没有物理意义。",
            "须按波长选择红边与近红外。这是演示数据，不能当业务验收。",
        ],
    ),
    "47_gndvi": _item(
        "47_gndvi",
        "GNDVI绿色归一化植被指数",
        "index",
        "GNDVI = (近红外反射率 − 绿光反射率) / (近红外反射率 + 绿光反射率)，用绿光代替红光。",
        "GNDVI = (NIR − GREEN) / (NIR + GREEN)",
        "绿光与近红外反射率。",
        "单波段 gndvi.tif。",
        [
            "输入须为反射率，并掩膜云影与 NoData。",
            "绿光窗口按传感器光谱响应选择，不能死记演示数据默认 1。",
            "高覆盖时仍可能饱和，不能直接当叶绿素含量。",
        ],
        [
            "对照 data.green_band、data.nir_band 说明索引是否只适用于演示数据。",
            "把 min、max、mean 读成全图统计，不是地块结论。",
            "指出 GNDVI 不能直接作为叶绿素定量产品。",
        ],
        [
            "不得把 GNDVI 写成叶绿素毫克数。",
            "不得根据 PNG 颜色定量。",
            "不得把立方体送进上下文。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。绿光通道的相对绿度，不是叶绿素含量。",
            "GNDVI 不是叶绿素毫克数。",
            "须按传感器选择绿光与近红外。这是演示数据，不能当业务验收。",
        ],
    ),
    "48_osavi": _item(
        "48_osavi",
        "OSAVI优化土壤调节植被指数",
        "index",
        "OSAVI = (近红外 − 红光) / (近红外 + 红光 + L)，Rondeaux 等取 L=0.16。",
        "OSAVI = (NIR − RED) / (NIR + RED + L)",
        "红光、近红外反射率；土壤项 L。",
        "单波段 osavi.tif。",
        [
            "默认 L=0.16 来自文献，不是现场标定。",
            "L=0 时公式退化成 NDVI 形式。",
            "输入须为反射率。",
            "不能直接当作叶面积或产量。",
        ],
        [
            "对照 data.L、data.red_band、data.nir_band 说明本次土壤项。",
            "把全图统计与 savi.tif 一类土壤调节指数区分开，本页只输出 OSAVI。",
            "提醒改 L 后不能和未改的图横比。",
        ],
        [
            "不得把 OSAVI 写成 LAI 或产量。",
            "不得改写 0.16 冒充新算法而不声明。",
            "不得根据 PNG 定量。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。L 默认 0.16 是文献常用值，不是现场最优。",
            "OSAVI 不是叶面积或产量。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "49_arvi": _item(
        "49_arvi",
        "ARVI耐大气植被指数",
        "index",
        "ARVI = (近红外 − RB) / (近红外 + RB)，RB = 红光 − γ(蓝光 − 红光)，常用 γ=1。",
        "ARVI = (NIR − RB) / (NIR + RB)",
        "蓝、红、近红外反射率；γ。",
        "单波段 arvi.tif。",
        [
            "ARVI 不能替代大气校正产品。",
            "蓝光差或阴影重时不要解释。",
            "γ 默认 1 不是本传感器标定。",
            "输入须为反射率。",
        ],
        [
            "对照 data.gamma 与蓝光索引，说明本次是否只是演示数据默认。",
            "把 min、max、mean 读成全图统计。",
            "指出蓝光噪声会进入 RB。",
        ],
        [
            "不得把 ARVI 写成已经完成大气校正。",
            "不得给出气溶胶光学厚度。",
            "不得根据 PNG 定量。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。γ=1 只是常用默认。",
            "ARVI 不是大气校正产品，也不是叶面积。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "50_vari": _item(
        "50_vari",
        "VARI可见大气阻力指数",
        "index",
        "VARI = (绿光 − 红光) / (绿光 + 红光 − 蓝光)，只用可见光。",
        "VARI = (GREEN − RED) / (GREEN + RED − BLUE)",
        "蓝、绿、红反射率，不需要近红外。",
        "单波段 vari.tif。",
        [
            "没有近红外不等于能替代 NDVI。",
            "分母 GREEN+RED−BLUE 可能接近零。",
            "土壤颜色和阴影会干扰。",
            "输入须为反射率或至少辐射一致的可见光通道。",
        ],
        [
            "对照三个可见光索引，说明本次没有使用近红外。",
            "把极值与分母接近零的像元分开看。",
            "指出 VARI 不是覆盖度百分比。",
        ],
        [
            "不得把 VARI 写成植被覆盖百分比。",
            "不得根据 RGB 照片 JPEG 未经定标就声称物理 VARI。",
            "不得根据 PNG 定量。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是可见光相对覆盖指数，不是覆盖度百分数。",
            "VARI 不使用近红外，不能替代 NDVI。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "51_lai_index": _item(
        "51_lai_index",
        "叶面积经验指数",
        "index",
        "先算 EVI，再做 LAI = max(3.618×EVI − 0.118, 0)。这是经验线性式，不是 #33 PROSAIL。",
        "LAI = max(3.618×EVI − 0.118, 0)",
        "蓝、红、近红外反射率。",
        "单波段 lai_index.tif。",
        [
            "系数 3.618 与 −0.118 是本仓库演示数据默认，不是全球 LAI 产品。",
            "与 #33 辐射传输物理反演不是同一条算法。",
            "负值被裁成 0，不表示真实零叶面积。",
            "不能当作实验室叶面积真值。",
        ],
        [
            "对照文件名 lai_index.tif，不要和 #33 的 lai.tif 混读。",
            "说明线性系数未经本景标定。",
            "把 min、max、mean 读成该经验式的输出，不是化验值。",
        ],
        [
            "不得把经验 LAI 写成实验室叶面积。",
            "不得把本页写成 #33 PROSAIL。",
            "不得根据 PNG 给出亩产。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是 EVI 线性变换，系数是演示数据默认。",
            "不是 #33 PROSAIL，也不是化验叶面积。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "52_nbr": _item(
        "52_nbr",
        "NBR标准化燃烧率",
        "index",
        "NBR = (近红外 − 短波红外) / (近红外 + 短波红外)。形式接近 NDMI，用途是过火相对差异。",
        "NBR = (NIR − SWIR) / (NIR + SWIR)",
        "近红外与真实短波红外反射率。",
        "单波段 nbr.tif。",
        [
            "必须有真实 SWIR，不能用末波段冒充。",
            "演示数据默认 SWIR 约 1600 nm；Landsat NBR 常用 SWIR2 约 2.1 μm，不能混比。",
            "与 NDMI 公式同型时数值接近，用途和波段窗口仍要分开写。",
            "不能直接写成过火面积或损失金额。",
        ],
        [
            "对照 data.swir_band 说明本次 SWIR 窗口。",
            "把全图统计读成相对格局，不是过火等级。",
            "没有 SWIR 时明确说本公式没有物理意义。",
        ],
        [
            "不得把 NBR 写成过火面积或灾损金额。",
            "不得把演示数据 1600 nm 结果写成 Landsat SWIR2 NBR。",
            "不得根据 PNG 定量。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。相对干湿/过火格局，不是灾损等级。",
            "演示数据 SWIR 约 1600 nm，不是 Landsat SWIR2。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "53_sipi": _item(
        "53_sipi",
        "SIPI结构不敏感色素指数",
        "index",
        "SIPI = (近红外 − 蓝光) / (近红外 − 红光)，用于色素比值相关相对差异。",
        "SIPI = (NIR − BLUE) / (NIR − RED)",
        "蓝、红、近红外反射率。",
        "单波段 sipi.tif。",
        [
            "NIR 接近 RED 时分母接近零。",
            "值域不必落在 −1～1。",
            "不能直接当作类胡萝卜素或叶绿素含量。",
            "输入须为反射率。",
        ],
        [
            "对照三个波段索引，并提醒分母接近零。",
            "把极值与植被/土壤分开看。",
            "指出 SIPI 不是含量产品。",
        ],
        [
            "不得把 SIPI 写成色素毫克数。",
            "不得根据 PNG 定量。",
            "不得把立方体送进上下文。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。色素比值相关相对量，不是含量。",
            "NIR 接近 RED 时数值会炸。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "54_gci": _item(
        "54_gci",
        "GCI绿色叶绿素指数",
        "index",
        "绿色叶绿素指数 GCI = 近红外反射率 / 绿光反射率 − 1。",
        "GCI = NIR/GREEN − 1",
        "绿光与近红外反射率。",
        "单波段 gci.tif。",
        [
            "与 RECI 同型，分母是绿光不是红边。",
            "值域不是 −1～1。",
            "不能直接作为叶绿素毫克数。",
            "输入须为反射率。",
        ],
        [
            "对照 data.green_band、data.nir_band。",
            "把全图统计读成比值指数，不是含量。",
            "指出绿光接近零时数值会很大。",
        ],
        [
            "不得把 GCI 写成叶绿素毫克数。",
            "不得把 GCI 与 RECI 混成同一个产品。",
            "不得根据 PNG 定量。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。这是 NIR/GREEN − 1，不是叶绿素含量。",
            "GCI 不是叶绿素毫克数。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
    "55_ndsi": _item(
        "55_ndsi",
        "NDSI归一化差值雪指数",
        "index",
        "NDSI = (绿光 − 短波红外) / (绿光 + 短波红外)。与 MNDWI 同型，用途是雪不是水。",
        "NDSI = (GREEN − SWIR) / (GREEN + SWIR)",
        "绿光与真实短波红外反射率。",
        "单波段 ndsi.tif。",
        [
            "必须有真实 SWIR。",
            "与 MNDWI 公式同型，不要按水体阈值解释。",
            "云、冰、盐壳可能与雪混淆。",
            "本仓库不输出积雪二值图。",
        ],
        [
            "对照 data.green_band、data.swir_band。",
            "写清这是雪指数，不是 #30 的 MNDWI 水体产品。",
            "没有 SWIR 时明确无物理意义。",
        ],
        [
            "不得把 NDSI 写成积雪面积产品。",
            "不得把本页结果当成 MNDWI 水体。",
            "不得根据 PNG 定量。",
        ],
        [
            "全图均值 {mean:.2f}，范围 {min:.2f}～{max:.2f}。相对积雪格局，不是积雪面积。",
            "与 MNDWI 同型，用途是雪不是水。",
            "这是演示数据，不能当业务验收。",
        ],
    ),
}


# 大模型赋能程度：三维各 0–3 分，合计 0–9。只衡量大模型在本算法上能讲多少，不是精度。
# readout 帮你读返回 / bounds 点出方法限制 / guard 拦住说错
_LLM_LEVERAGE: dict[str, dict[str, tuple[int, str]]] = {
    "27_ndvi": {
        "readout": (2, "对照本次波段索引、全图统计、尺寸和格式，讲清每个返回字段是什么。"),
        "bounds": (2, "指出应优先用定标反射率；高叶面积时饱和，增量被压缩。"),
        "guard": (2, "拦住把 NDVI 直接写成叶绿素含量或生物量定量产品。"),
    },
    "28_ndre": {
        "readout": (2, "核对红边/近红外索引，并说明全图统计只是相对格局。"),
        "bounds": (2, "指出没有真实红边通道时本公式没有物理意义。"),
        "guard": (2, "拦住把 NDRE 写成叶绿素毫克数。"),
    },
    "29_evi_savi": {
        "readout": (2, "分别打开 evi.tif、savi.tif、msavi.tif，避免把一个均值当成三个指数都已校正。"),
        "bounds": (2, "说明 L 会改变 SAVI，三公式量纲与饱和行为不同。"),
        "guard": (2, "拦住把三个指数写成 LAI、氮或产量。"),
    },
    "30_ndmi_ndwi": {
        "readout": (2, "分别打开 ndmi.tif、ndwi.tif、mndwi.tif，以及本次有没有真实 SWIR。"),
        "bounds": (2, "指出无 SWIR 时 NDMI/MNDWI 没有物理意义，同名 NDWI 不能混比。"),
        "guard": (2, "拦住给出绝对含水量，或把一层公式套到另一层。"),
    },
    "31_red_edge_params": {
        "readout": (2, "核对 Guyot 四点是否落在真实波长轴上。"),
        "bounds": (2, "指出假等间隔波长或宽带采样会使位置不可信。"),
        "guard": (2, "拦住把 REP 纳米数写成叶绿素毫克数。"),
    },
    "32_regression_inversion": {
        "readout": (2, "说明训练/测试误差只对当前划分有效。"),
        "bounds": (2, "指出像元随机划分会泄漏，成分数过多会过拟合。"),
        "guard": (3, "拦住把一次测试 R² 写成业务验收。"),
    },
    "33_physical_inversion": {
        "readout": (2, "说明输出是 LUT 最优若干条的平均，不是全参数连续优化解。"),
        "bounds": (2, "指出固定其余参数会把误差挤进 LAI/Cab，边界命中不是可靠极值。"),
        "guard": (3, "拦住把 LUT 命中值写成实验室化验。"),
    },
    "34_svm_rf_classify": {
        "readout": (2, "分开解释 OA、AA、Kappa 各自回答什么问题。"),
        "bounds": (2, "指出背景像元会被强制分类，像元随机划分使指标虚高。"),
        "guard": (3, "拦住把一次测试 OA 写成业务过关。"),
    },
    "35_spectral_matching": {
        "readout": (2, "把最小角/散度与类别标签分开读。"),
        "bounds": (2, "指出无拒绝阈值时每个像元都会被硬分类，SID 与 SAM 分数不可互换。"),
        "guard": (2, "拦住把最小角写成概率或精度百分比。"),
    },
    "36_cnn1d_classify": {
        "readout": (2, "说明短训指标只说明本次划分，不是收敛模型。"),
        "bounds": (2, "指出当前无空间邻域，碎斑是实现边界。"),
        "guard": (3, "拦住宣称本网络已达业务精度。"),
    },
    "37_cnn3d_classify": {
        "readout": (2, "对照 patch 尺寸与测试指标，提示泄漏风险。"),
        "bounds": (2, "指出重叠 patch 会泄漏，演示短训不是论文复现。"),
        "guard": (3, "拦住把演示 OA 写成论文级精度。"),
    },
    "38_transformer_classify": {
        "readout": (2, "把短训指标限制在本次划分协议内解读。"),
        "bounds": (2, "指出缩小网络已缩小，GCN 属于未实现能力。"),
        "guard": (3, "拦住把本实现写成通用视觉大模型。"),
    },
    "39_few_shot_classify": {
        "readout": (2, "说明支持数、query 缺失时指标不能读。"),
        "bounds": (2, "指出这是均值原型匹配，未知光谱仍会被硬分。"),
        "guard": (3, "拦住把少量 shots 写成已经解决小样本。"),
    },
    "40_detect_segment": {
        "readout": (2, "把 ACE 分数、百分位与斑块像元数分开读。"),
        "bounds": (2, "指出当前是 ACE 检测而不是深度学习分割，百分位只相对本景。"),
        "guard": (3, "拦住把斑块写成已确认目标类别。"),
    },
    "41_unmixing": {
        "readout": (3, "把丰度、和约束与残差一起读。"),
        "bounds": (2, "指出线性混合、通道少时欠定，丰度不一定等于面积比例。"),
        "guard": (3, "拦住把丰度写成质量分数或产量份额。"),
    },
    "42_anomaly_detect": {
        "readout": (2, "把连续得分与相对阈值掩膜分开读。"),
        "bounds": (2, "指出高分只是相对背景离群，不是已命名类别。"),
        "guard": (3, "拦住把 RX 高分写成特定地物名称。"),
    },
    "43_change_detect": {
        "readout": (2, "把 χ² 强度与相对百分位掩膜分开读。"),
        "bounds": (2, "指出输出是统计变化不是原因，错位会造假变化。"),
        "guard": (3, "拦住把变化图写成灾损等级或因果定性。"),
    },
    "44_postprocess_smooth": {
        "readout": (2, "对照窗口、小斑阈值、变更像元数与类别列表解释处理强度。"),
        "bounds": (2, "指出众数与筛斑会吞并小目标和边界，视觉整齐不等于更准确。"),
        "guard": (3, "拦住根据预览颜色编造类别、场景或业务决策。"),
    },
    "45_parcel_zonal_stats": {
        "readout": (3, "区分连续统计与分类计数占比，并说明整景和逐地块口径。"),
        "bounds": (2, "指出 NoData、NaN、CRS 与空有效区如何改变分母和可解释性。"),
        "guard": (3, "拦住把汇总统计写成原因、处方或业务决策。"),
    },
    "46_reci": {
        "readout": (2, "对照红边与近红外索引，把全图统计读成比值指数。"),
        "bounds": (2, "指出没有真实红边时公式没有物理意义。"),
        "guard": (3, "拦住把 RECI 写成叶绿素毫克数。"),
    },
    "47_gndvi": {
        "readout": (2, "对照绿光与近红外索引，把全图统计读成相对绿度。"),
        "bounds": (2, "指出 GNDVI 不能直接当作叶绿素含量。"),
        "guard": (3, "拦住把 GNDVI 写成叶绿素毫克数。"),
    },
    "48_osavi": {
        "readout": (2, "对照 L 是否为 0.16，以及红光近红外索引。"),
        "bounds": (2, "指出 L 改了就不能和未改的图横比。"),
        "guard": (3, "拦住把 OSAVI 写成叶面积或产量。"),
    },
    "49_arvi": {
        "readout": (2, "对照 γ 与蓝光索引，说明 RB 是怎么来的。"),
        "bounds": (2, "指出 ARVI 不能替代大气校正。"),
        "guard": (3, "拦住把 ARVI 写成已经完成大气校正。"),
    },
    "50_vari": {
        "readout": (2, "说明本次只用可见光，没有近红外。"),
        "bounds": (2, "指出分母可能接近零，VARI 不是覆盖度百分数。"),
        "guard": (3, "拦住把 VARI 写成植被覆盖百分比。"),
    },
    "51_lai_index": {
        "readout": (2, "对照 lai_index.tif 文件名，说明这是 EVI 线性变换。"),
        "bounds": (2, "指出系数是演示数据默认，不是 #33 PROSAIL。"),
        "guard": (3, "拦住把经验 LAI 写成实验室叶面积。"),
    },
    "52_nbr": {
        "readout": (2, "对照 SWIR 索引，说明演示数据窗口约 1600 nm。"),
        "bounds": (2, "指出与 NDMI 同型时仍不能混成过火等级。"),
        "guard": (3, "拦住把 NBR 写成过火面积或灾损金额。"),
    },
    "53_sipi": {
        "readout": (2, "对照蓝、红、近红外，提醒分母接近零。"),
        "bounds": (2, "指出 SIPI 值域不必落在 −1～1。"),
        "guard": (3, "拦住把 SIPI 写成色素毫克数。"),
    },
    "54_gci": {
        "readout": (2, "对照绿光与近红外，说明这是比值减 1。"),
        "bounds": (2, "指出 GCI 与 RECI 同型但分母不同。"),
        "guard": (3, "拦住把 GCI 写成叶绿素毫克数。"),
    },
    "55_ndsi": {
        "readout": (2, "对照绿光与 SWIR，写清这是雪不是水。"),
        "bounds": (2, "指出与 MNDWI 同型，本页不输出积雪二值图。"),
        "guard": (3, "拦住把 NDSI 写成积雪面积或 MNDWI 水体。"),
    },
}

_DIM_LABELS = (
    ("readout", "帮你读返回"),
    ("bounds", "点出方法限制"),
    ("guard", "拦住说错"),
)


def _dim_effect(score: int) -> str:
    """0 几乎帮不上，1 效果有限，2 能看出来，3 作用明显。"""
    if score <= 0:
        return "几乎帮不上"
    if score == 1:
        return "效果有限"
    if score == 2:
        return "能看出来"
    return "作用明显"


def _leverage_band(total: int) -> str:
    """1–4 偏低，5–6 中等，7–9 偏高。"""
    if total <= 4:
        return "偏低"
    if total <= 6:
        return "中等"
    return "偏高"


_DEFAULT_LEVERAGE: dict[str, tuple[int, str]] = {
    "readout": (2, "对照本次接口返回，讲清已登记字段是什么。"),
    "bounds": (2, "指出本算法已写明的方法限制，不外推未登记机理。"),
    "guard": (2, "拦住把返回写成知识库未登记的物理量或处方。"),
}


def llm_leverage_of(algorithm_id: str) -> dict[str, Any]:
    """返回可展示的赋能程度与四段分析；缺分数登记时用默认 2+2+2。"""
    from common.l3_aide.leverage_sections import SECTION_ORDER, SECTIONS

    raw = _LLM_LEVERAGE.get(algorithm_id) or _DEFAULT_LEVERAGE
    dims: list[dict[str, Any]] = []
    total = 0
    for key, label in _DIM_LABELS:
        score, why = raw.get(key, (0, "尚未登记大模型在本算法上能做什么。"))
        score = int(score)
        total += score
        dims.append(
            {
                "id": key,
                "label": label,
                "score": score,
                "max": 3,
                "effect": _dim_effect(score),
                "why": why,
            }
        )
    body = SECTIONS[algorithm_id]
    sections = [
        {"id": key, "label": label, "text": body[key]}
        for key, label in SECTION_ORDER
    ]
    return {
        "score": total,
        "max": 9,
        "percent": round(100 * total / 9),
        "band": _leverage_band(total),
        "note": "综合效果只说明大模型能讲多少，不是精度贡献，也不改推其他算法。",
        "dims": dims,
        "sections": sections,
    }


def list_algorithm_ids() -> list[str]:
    """按编号列出指数、分类与解混知识条目。"""
    return list(_INDEX_IDS + _CLASSIFY_IDS + _MIX_IDS)


def _fallback_algorithm(algorithm_id: str) -> dict[str, Any] | None:
    """用目录标题与输出知识摘要拼解读卡，不编造未登记机理。"""
    from common.catalog import ALGORITHMS as CATALOG
    from common.console_output_knowledge import get_algorithm_output_knowledge

    meta = next((row for row in CATALOG if row["id"] == algorithm_id), None)
    if meta is None:
        return None
    summary = get_algorithm_output_knowledge(algorithm_id).get("summary") or {}
    what = str(summary.get("what") or "").strip()
    value = str(summary.get("value") or "").strip()
    caution = str(summary.get("caution") or "").strip()
    title = str(meta["title"])
    definition = what or f"本仓库实现「{title}」。"
    accuracy = [
        line
        for line in (
            what,
            value,
            caution,
        )
        if line
    ]
    if len(accuracy) < 3:
        accuracy.extend(
            [
                "只依据已登记输出字段解读。",
                "不得外推知识库未写明的物理量。",
                "演示数据 不能当业务验收。",
            ][: 3 - len(accuracy)]
        )
    may = [
        "对照本次接口返回，说明已登记字段分别是什么。",
        "点出本算法摘要里已经写明的方法限制。",
        "拦住把返回写成未登记的含量、剂量或其他算法。",
    ]
    must_not = [
        "不得把立方体或 GeoTIFF 送进上下文。",
        "不得改推其他算法。",
        "不得开处方或给出剂量。",
        "不得编造本知识库未写明的物理量。",
    ]
    return _item(
        algorithm_id,
        title,
        "catalog",
        definition,
        "以本仓库实现与已登记输出字段为准。",
        "见本算法接口输入。",
        "见本算法已登记输出。",
        accuracy[:4],
        may,
        must_not,
        [
            f"{title}：{definition}只依据已登记输出字段解读本次返回，不把无关的 min/max/mean 当成地块结论。",
            "本次只支持对照本算法产物，不是处方，也不能当业务验收。",
            caution or "下一步核对本算法输入、参数与已登记输出是否一致。",
        ],
    )


def get_algorithm(algorithm_id: str) -> dict[str, Any] | None:
    """返回知识副本；目录内算法可回退到输出知识，未知 id 为 None。"""
    row = ALGORITHMS.get(algorithm_id) or _fallback_algorithm(algorithm_id)
    if not row:
        return None
    out = dict(row)
    out["llmLeverage"] = llm_leverage_of(algorithm_id)
    return out


def list_algorithm_groups() -> list[dict[str, Any]]:
    """目录三组。"""
    buckets = {
        "index": _INDEX_IDS,
        "classify": _CLASSIFY_IDS,
        "mix": _MIX_IDS,
    }
    groups: list[dict[str, Any]] = []
    for gid, title in GROUP_ORDER:
        items = []
        for aid in buckets[gid]:
            doc = ALGORITHMS[aid]
            items.append({"id": aid, "title": doc["title"]})
        groups.append({"id": gid, "title": title, "items": items})
    return groups
