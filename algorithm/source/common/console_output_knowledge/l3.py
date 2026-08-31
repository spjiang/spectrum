"""算法 27–45 的专属输出知识。"""
from __future__ import annotations

from typing import Any

from .common import make_output


def _summary(what: str, value: str, caution: str) -> dict[str, str]:
    """构造算法级摘要。"""
    return {"what": what, "value": value, "caution": caution}


def _row(
    path: str,
    label: str,
    *,
    description: str,
    effect: str,
    business: str,
    interpretation: str,
    check: str,
    warning: str,
    downstream: str,
    abnormal: list[str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """构造包含完整解释边界的输出记录。"""
    return make_output(
        path,
        label,
        description=description,
        effect=effect,
        business_meaning=business,
        interpretation=interpretation,
        quality_check=check,
        abnormal_signs=abnormal or [warning],
        downstream_use=downstream,
        misuse_warning=warning,
        **kwargs,
    )


def _metric(
    path: str,
    label: str,
    description: str,
    interpretation: str,
    *,
    check: str,
    warning: str,
    downstream: str,
    unit: str = "—",
    range_text: str = "由本次输入与算法参数决定",
    optional: bool = False,
    conditional: str = "",
    quality_rule: dict[str, Any] | None = None,
    format_name: str = "",
    vis: str = "json_table",
) -> dict[str, Any]:
    """构造有明确口径的指标或元数据记录。"""
    return _row(
        path,
        label,
        description=description,
        effect=f"记录本次运行的{label}，用于解释、复算和结果追溯。",
        business=f"帮助判断{label}对应的模型表现、数据规模或处理配置。",
        interpretation=interpretation,
        check=check,
        warning=warning,
        downstream=downstream,
        unit=unit,
        range_text=range_text,
        optional=optional,
        conditional=conditional,
        quality_rule=quality_rule,
        format_name=format_name,
        vis=vis,
    )


def _preview(path: str, title: str, related: str, *, categorical: bool = False) -> dict[str, Any]:
    """构造仅供目视快检的 PNG 记录。"""
    color_text = "颜色仅映射类别 ID，不表示类别大小、置信度或业务等级。" if categorical else "颜色由本次渲染拉伸决定，不是原始数值。"
    return _row(
        path,
        f"{title}预览图",
        description=f"{title}的 PNG 快速预览；{color_text}",
        effect="把空间分布渲染为便于浏览的静态图片。",
        business="用于快速发现空间错位、条带、空洞和异常斑块。",
        interpretation=f"只做目视快检；定量分析应读取 {related}。{color_text}",
        check=f"与 {related} 的空间格局对照，核查方向、范围和显著斑块是否一致。",
        warning="不得从 PNG 颜色反推原始数值、类别置信度或面积统计。",
        downstream="用于报告插图和人工质量复核，不进入定量计算。",
        format_name="PNG",
        vis="image",
        related_outputs=[related],
    )


def _index_knowledge(
    *,
    algorithm_id: str,
    name: str,
    formula: str,
    first_band: str,
    second_band: str,
    file_key: str,
    meaning: str,
) -> dict[str, Any]:
    """构造归一化差值指数的完整知识。"""
    domain_rule = {
        "kind": "between",
        "min": -1.0,
        "max": 1.0,
        "passWhenInside": True,
        "basis": f"{name} 理论定义域",
    }
    outputs: dict[str, Any] = {
        f"files.{file_key}": _row(
            f"files.{file_key}",
            f"{name}专题图",
            description=f"逐像元按 {formula} 计算的单波段 GeoTIFF，{first_band} 与 {second_band} 使用 0-based 参数索引。",
            effect=f"把 {first_band} 与 {second_band} 的归一化差异映射为空间指数。",
            business=meaning,
            interpretation=f"在非负且可比的反射率输入下理论范围为 [-1, 1]；需结合地物、物候和采集条件比较。",
            check="核对波段索引、空间参考、NoData 和有限值，并确认有效像元处于 [-1, 1] 理论定义域。",
            warning="不得在波段含义错误、辐射尺度不可比或跨期未归一化时直接解释指数差异。",
            downstream="用于地块统计、时序比较、阈值候选区和 GIS 专题制图。",
            unit="无量纲指数",
            range_text=f"{formula} 的理论范围 [-1, 1]（非负可比输入）",
            format_name="GeoTIFF",
            vis="raster_index",
            related_outputs=["data.min", "data.max", "data.mean"],
        ),
        "files.preview_png": _preview("files.preview_png", name, f"files.{file_key}"),
    }
    for key, label, role in (
        ("min", "最小值", "场景低值端"),
        ("max", "最大值", "场景高值端"),
        ("mean", "均值", "全景平均水平"),
    ):
        outputs[f"data.{key}"] = _metric(
            f"data.{key}",
            f"{name}{label}",
            f"{name}栅格全部像元的{label}，表示{role}。",
            f"应位于 [-1, 1]；极端值需结合水体、阴影、裸土和分母接近零区域检查。",
            check="与 GeoTIFF 复算统计一致，并处于理论定义域 [-1, 1]。",
            warning="全景统计会掩盖空间异质性，不能替代分区统计或分布检查。",
            downstream="用于运行快检、批次对比和统计摘要。",
            unit="无量纲指数",
            range_text="理论范围 [-1, 1]",
            quality_rule=domain_rule,
        )
    return {
        "summary": _summary(
            f"按 {formula} 逐像元计算{name}。",
            f"形成{meaning}的空间栅格和全景统计。",
            "结果依赖正确波段索引和可比辐射尺度；PNG 仅供目视，统计量不代表局部地块。",
        ),
        "outputs": outputs,
    }


def _classification_metric(path: str, label: str, description: str, *, optional: bool = False) -> dict[str, Any]:
    """构造没有预设业务阈值的分类评估指标。"""
    key = path.rsplit(".", 1)[-1]
    range_text = "通常 [-1, 1]" if key == "kappa" else "[0, 1]"
    direction = "越高通常表示一致性越好" if key == "kappa" else "越高通常表示测试集分类表现越好"
    condition = "仅存在未作为支持集的查询样本时返回" if optional else ""
    return _metric(
        path,
        label,
        description,
        f"{direction}；只能在相同标签口径、划分策略和测试样本上比较。",
        check="核对独立测试/查询样本数、类别覆盖和划分方式；没有业务验收阈值，当前结果质量状态不可判定。",
        warning="不得把单次随机划分指标当作跨场景泛化能力或业务通过结论。",
        downstream="用于同数据划分下的模型对比、误差分析和实验记录。",
        unit="比例",
        range_text=range_text,
        optional=optional,
        conditional=condition,
    )


def _classification_file(title: str) -> dict[str, Any]:
    """构造类别 ID 栅格说明。"""
    return _row(
        "files.pred_map_tif",
        f"{title}分类图",
        description="逐像元类别 ID 的单波段 GeoTIFF，ID 来自有效训练标签，不表示大小顺序。",
        effect=f"将整景光谱映射为{title}预测类别。",
        business="提供地物类别空间分布，支持面积汇总、样本复核和后处理。",
        interpretation="像元值是离散类别 ID；必须与 data.classes 及外部类别字典联合解释。",
        check="核对标签尺寸、类别集合、空间参考，并用独立测试样本检查混淆情况。",
        warning="类别 ID 不是概率、置信度或业务等级；未输出逐像元置信度。",
        downstream="用于分类平滑、地块类别统计、GIS 叠加和样本迭代。",
        format_name="GeoTIFF",
        vis="raster_class",
        related_outputs=["data.classes", "files.preview_png"],
    )


def _classification_outputs(
    title: str,
    *,
    extras: dict[str, tuple[str, str, str]],
    optional_metrics: bool = False,
) -> dict[str, Any]:
    """构造监督分类算法的公共输出，并保留模型专属元数据。"""
    outputs: dict[str, Any] = {
        "files.pred_map_tif": _classification_file(title),
        "files.preview_png": _preview(
            "files.preview_png", f"{title}分类", "files.pred_map_tif", categorical=True
        ),
        "data.oa": _classification_metric(
            "data.oa", "总体精度 OA", "测试/查询样本中预测正确数占总样本数的比例。", optional=optional_metrics
        ),
        "data.aa": _classification_metric(
            "data.aa", "平均精度 AA", "按混淆矩阵逐类召回率取有效类别平均。", optional=optional_metrics
        ),
        "data.kappa": _classification_metric(
            "data.kappa", "Kappa 系数", "测试/查询预测与真值扣除随机一致后的 Cohen Kappa。", optional=optional_metrics
        ),
    }
    for key, (label, description, interpretation) in extras.items():
        is_query = optional_metrics and key == "n_query"
        outputs[f"data.{key}"] = _metric(
            f"data.{key}",
            label,
            description,
            interpretation,
            check="与本次参数、标签筛选和模型返回值核对。",
            warning="该字段只描述本次运行配置或样本，不代表模型跨场景能力。",
            downstream="用于实验复现、结果筛选和批次对比。",
            optional=is_query,
            conditional="仅存在未作为支持集的查询样本时返回" if is_query else "",
            vis="array" if key == "classes" else "json_table",
        )
    return outputs


def _simple_data(
    path: str,
    label: str,
    description: str,
    interpretation: str,
    *,
    warning: str,
    downstream: str = "用于运行追溯、结果筛选和关联产物复算。",
    **kwargs: Any,
) -> dict[str, Any]:
    """构造算法专属的参数、计数或结构字段。"""
    return _metric(
        path,
        label,
        description,
        interpretation,
        check="与输入、参数和关联文件复核，确认口径与数量一致。",
        warning=warning,
        downstream=downstream,
        **kwargs,
    )


L3_OUTPUT_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "27_ndvi": _index_knowledge(
        algorithm_id="27_ndvi",
        name="NDVI",
        formula="(NIR-RED)/(NIR+RED)",
        first_band="NIR",
        second_band="RED",
        file_key="ndvi_tif",
        meaning="植被绿度与覆盖状况",
    ),
    "28_ndre": _index_knowledge(
        algorithm_id="28_ndre",
        name="NDRE",
        formula="(NIR-RE)/(NIR+RE)",
        first_band="NIR",
        second_band="红边 RE",
        file_key="ndre_tif",
        meaning="冠层红边响应与中高覆盖植被差异",
    ),
    "29_evi_savi": {
        "summary": _summary(
            "从蓝、红、近红外波段同时计算 EVI、SAVI 和 MSAVI。",
            "用三种不同背景校正机制描述植被状态，便于比较大气和土壤背景影响。",
            "当前公式不裁剪结果；EVI/SAVI/MSAVI 不能统一套用 NDVI 的 [-1,1] 质量门限。",
        ),
        "outputs": {
            "files.indices_tif": _row(
                "files.indices_tif", "EVI/SAVI/MSAVI 三波段栅格",
                description="固定按 EVI、SAVI、MSAVI 顺序写出的三波段 GeoTIFF。",
                effect="同步生成增强植被指数、土壤调节植被指数和改进土壤调节植被指数。",
                business="用于比较高覆盖冠层、裸土背景和不同土壤校正假设下的植被响应。",
                interpretation="波段 1=EVI，2=SAVI，3=MSAVI；数值受反射率尺度、蓝光质量及 L 参数影响。",
                check="按服务公式抽样复算，检查 MSAVI 根号项、有限值及三个波段顺序。",
                warning="不得把三个指数视为同一量纲下可直接互换的业务评分，也不得统一强制到 [-1,1]。",
                downstream="用于指数对比、地块统计、特征工程和时序分析。",
                format_name="GeoTIFF", vis="raster_cube",
                bands=[
                    {"name": "EVI", "description": "2.5×(NIR-RED)/(NIR+6RED-7.5BLUE+1)"},
                    {"name": "SAVI", "description": "(1+L)×(NIR-RED)/(NIR+RED+L)"},
                    {"name": "MSAVI", "description": "0.5×(2NIR+1-sqrt((2NIR+1)^2-8(NIR-RED)))"},
                ],
                related_outputs=["data.L", "data.evi_mean", "data.savi_mean", "data.msavi_mean"],
            ),
            "files.preview_png": _preview("files.preview_png", "EVI", "files.indices_tif"),
            "data.L": _simple_data(
                "data.L", "SAVI 土壤调节因子 L", "SAVI 公式使用的土壤背景调节参数。",
                "L 越大，SAVI 对土壤背景的修正越强；当前默认 0.5。",
                warning="L 是模型参数，不是观测结果；不同 L 的 SAVI 均值不可直接混合比较。",
            ),
            "data.evi_mean": _simple_data(
                "data.evi_mean", "EVI 均值", "全景 EVI 的 NaN 忽略均值。",
                "用于概括增强植被指数整体水平，需结合空间分布。",
                warning="均值可能掩盖分母接近零、异常蓝光和局部极值。",
            ),
            "data.savi_mean": _simple_data(
                "data.savi_mean", "SAVI 均值", "全景 SAVI 的 NaN 忽略均值。",
                "用于概括给定 L 下的土壤调节指数水平。",
                warning="不同 L 或不同土壤背景下的均值不可脱离参数直接比较。",
            ),
            "data.msavi_mean": _simple_data(
                "data.msavi_mean", "MSAVI 均值", "全景 MSAVI 的 NaN 忽略均值。",
                "用于概括自动土壤背景修正后的植被指数水平。",
                warning="根号项无效会产生 NaN；均值不能替代无效像元检查。",
            ),
        },
    },
    "30_ndmi_ndwi": {
        "summary": _summary(
            "从绿、近红外和短波红外计算 NDMI、NDWI、MNDWI。",
            "同时表达植被水分响应与水体增强信息。",
            "三波段含义和方向不同；阈值受传感器、地物和场景影响，不设业务通过阈值。",
        ),
        "outputs": {
            "files.indices_tif": _row(
                "files.indices_tif", "NDMI/NDWI/MNDWI 三波段栅格",
                description="固定按 NDMI、NDWI、MNDWI 顺序写出的三波段归一化差值 GeoTIFF。",
                effect="分别计算 (NIR-SWIR)/(NIR+SWIR)、(GREEN-NIR)/(GREEN+NIR)、(GREEN-SWIR)/(GREEN+SWIR)。",
                business="用于植被含水变化、水体候选提取和建成区背景抑制分析。",
                interpretation="波段 1=NDMI，2=NDWI，3=MNDWI；非负可比输入下各指数理论范围 [-1,1]。",
                check="核对绿/NIR/SWIR 索引，抽样复算并检查三波段顺序和 [-1,1] 理论定义域。",
                warning="不得用单一固定阈值跨传感器、季节和区域直接判水或判旱。",
                downstream="用于水分监测、水体候选区、地块统计和多指数特征。",
                format_name="GeoTIFF", vis="raster_cube",
                bands=[
                    {"name": "NDMI", "description": "(NIR-SWIR)/(NIR+SWIR)"},
                    {"name": "NDWI", "description": "(GREEN-NIR)/(GREEN+NIR)"},
                    {"name": "MNDWI", "description": "(GREEN-SWIR)/(GREEN+SWIR)"},
                ],
                related_outputs=["data.ndmi_mean", "data.ndwi_mean", "data.mndwi_mean"],
            ),
            "files.preview_png": _preview("files.preview_png", "NDWI", "files.indices_tif"),
            **{
                f"data.{key}_mean": _simple_data(
                    f"data.{key}_mean", f"{key.upper()} 均值", f"全景 {key.upper()} 像元算术均值。",
                    "在非负可比输入下应位于 [-1,1]；只能与相同波段定义和处理口径结果比较。",
                    warning="全景均值不能直接作为水体、含水量或干旱业务阈值。",
                    unit="无量纲指数", range_text="理论范围 [-1, 1]",
                )
                for key in ("ndmi", "ndwi", "mndwi")
            },
        },
    },
    "31_red_edge_params": {
        "summary": _summary(
            "用 Guyot 四锚点线性内插和 Savitzky–Golay 一阶导数峰值提取红边参数。",
            "输出红边位置、红边振幅和导数峰值位置，支撑冠层胁迫与叶绿素变化分析。",
            "波长由起止值线性生成；非真实中心波长、覆盖不足或光谱噪声会直接影响结果。",
        ),
        "outputs": {
            "files.params_tif": _row(
                "files.params_tif", "红边参数三波段栅格",
                description="固定按 Guyot REP、红边振幅、SG 导数 REP 顺序写出的 GeoTIFF。",
                effect="将每个像元的红边位置和振幅压缩为三个可解释参数。",
                business="用于比较冠层红边位移、红边强度和胁迫响应。",
                interpretation="波段 1/3 单位 nm；波段 2 为 R780-R670，单位随输入光谱。",
                check="确认波长范围覆盖 670/700/740/780 nm 和 680–750 nm，抽样复算锚点内插与导数峰值。",
                warning="起止波长仅线性生成波长轴，不代表已读取传感器真实波长定标。",
                downstream="用于红边专题制图、地块统计和回归特征。",
                format_name="GeoTIFF", vis="raster_cube",
                bands=[
                    {"name": "guyot_rep_nm", "description": "Guyot 四锚点线性内插红边位置，nm"},
                    {"name": "red_edge_amplitude", "description": "R780-R670 红边振幅"},
                    {"name": "sg_derivative_rep_nm", "description": "SG 一阶导数在红边窗口的峰值波长，nm"},
                ],
                related_outputs=["data.anchors_nm", "data.rep_mean", "data.amp_mean", "data.deriv_rep_mean"],
            ),
            "files.preview_png": _preview("files.preview_png", "Guyot 红边位置", "files.params_tif"),
            "data.anchors_nm": _simple_data(
                "data.anchors_nm", "Guyot 锚点波长", "固定四锚点 [670,700,740,780] nm。",
                "这些波长用于插值 R670/R700/R740/R780，不是输入的实际波段索引。",
                warning="波长轴未覆盖锚点时 np.interp 会使用边界值，结果不应按正常 REP 解释。",
                unit="nm", range_text="[670, 700, 740, 780]", vis="array",
            ),
            "data.rep_mean": _simple_data(
                "data.rep_mean", "Guyot REP 均值", "Guyot REP 栅格的全景均值。",
                "单位 nm；应结合锚点覆盖和空间分布判断。",
                warning="分母 R740-R700 很小时 REP 可出现极端外推值。", unit="nm",
            ),
            "data.amp_mean": _simple_data(
                "data.amp_mean", "红边振幅均值", "R780-R670 振幅栅格的全景均值。",
                "正值通常表示 670–780 nm 反射率上升，大小随输入尺度。",
                warning="不是无量纲归一化指标，跨辐射尺度不可直接比较。",
            ),
            "data.deriv_rep_mean": _simple_data(
                "data.deriv_rep_mean", "导数 REP 均值", "SG 一阶导数峰值波长栅格的全景均值。",
                "表示所用离散波长轴上导数峰值的平均位置。",
                warning="受波段间隔、SG 窗口和噪声影响，不等同 Guyot REP。", unit="nm",
            ),
            "data.wl_start_nm": _simple_data(
                "data.wl_start_nm", "波长起点", "线性生成输入波长轴的起始值。",
                "与 wl_end_nm 和波段数共同决定每个输入波段的假定波长。",
                warning="不是从影像元数据读取的实测中心波长。", unit="nm",
            ),
            "data.wl_end_nm": _simple_data(
                "data.wl_end_nm", "波长终点", "线性生成输入波长轴的结束值。",
                "与 wl_start_nm 和波段数共同决定假定波长间隔。",
                warning="错误终点会系统性偏移两个 REP 结果。", unit="nm",
            ),
        },
    },
    "32_regression_inversion": {
        "summary": _summary(
            "用真值图监督训练 PLS 回归，并对整景反演连续变量。",
            "输出连续反演图及留出测试集 R²/RMSE。",
            "当前响应固定报告 preprocess=snv；指标无业务验收阈值，且同一场景像元随机拆分可能高估空间泛化。",
        ),
        "outputs": {
            "files.inversion_tif": _row(
                "files.inversion_tif", "PLS 连续反演图",
                description="以 file2 真值图训练 PLS 后，对输入立方体全部像元预测的单波段 GeoTIFF。",
                effect="把多波段光谱映射为与真值同口径的连续变量。",
                business="用于生化参数、含量或其他连续目标的空间估算。",
                interpretation="数值单位和含义完全继承真值图；当前实现不裁剪到训练目标范围。",
                check="核对 file2 尺寸、目标单位、训练/测试数和预测极值，并检查外推区域。",
                warning="没有独立场景验证时不得把留出像元指标宣称为跨区域反演精度。",
                downstream="用于地块统计、连续变量制图和独立样点验证。",
                format_name="GeoTIFF", vis="raster_continuous",
                related_outputs=["data.r2", "data.rmse", "data.n_components", "data.preprocess"],
            ),
            "files.preview_png": _preview("files.preview_png", "PLS 反演", "files.inversion_tif"),
            "data.r2": _simple_data(
                "data.r2", "测试集 R²", "留出测试像元上的决定系数。",
                "越高通常拟合越好，但可为负；只能在相同目标、划分和预处理下比较。",
                warning="没有业务验收阈值，质量状态不可判定；空间自相关可能抬高结果。",
            ),
            "data.rmse": _simple_data(
                "data.rmse", "测试集 RMSE", "留出测试像元预测误差平方均值的平方根。",
                "越低通常越好，单位与真值图相同，必须结合目标量程解释。",
                warning="没有业务验收阈值，质量状态不可判定；不同单位 RMSE 不可直接比较。",
            ),
            **{
                f"data.{key}": _simple_data(
                    f"data.{key}", label, description, interpretation, warning=warning
                )
                for key, label, description, interpretation, warning in (
                    ("n_components", "PLS 成分数", "约束到波段数与样本数后的实际 PLS 潜变量数量。", "至少为 1，可能小于请求值。", "不是自动选出的最优复杂度。"),
                    ("n_train", "训练样本数", "随机拆分后用于拟合 PLS 的像元数。", "与 n_test 合计为真值图像元数。", "当前实现未屏蔽 NoData 或无效真值。"),
                    ("n_test", "测试样本数", "随机拆分后用于计算 R²/RMSE 的像元数。", "测试集来自同一影像的随机像元。", "不能视为独立区域或独立时相验证。"),
                    (
                        "preprocess",
                        "预处理回显",
                        "响应固定回显 snv；仅当请求参数 preprocess 忽略大小写后等于 snv 时，服务才实际执行标准正态变量变换。",
                        "该固定回显可能与实际执行不一致，不能据此确认使用了 SNV；实际执行以请求参数和处理记录为准。",
                        "不得把 data.preprocess 的固定回显当作预处理执行证据。",
                    ),
                )
            },
        },
    },
    "33_physical_inversion": {
        "summary": _summary(
            "用 PROSPECT-5+4SAIL 固定网格 LUT，以最小光谱角匹配反演 LAI 与 Cab。",
            "输出叶面积指数和叶绿素含量的空间估计。",
            "LUT 仅变化 LAI/Cab，其余参数固定；结果取离散网格值，不代表经过地面验证。",
        ),
        "outputs": {
            "files.lai_tif": _row(
                "files.lai_tif", "LAI 反演图", description="最相似 PROSAIL LUT 光谱对应的 LAI 单波段 GeoTIFF。",
                effect="把每像元光谱匹配到 0.2–6.0 的离散 LAI 网格。",
                business="用于冠层结构、覆盖和生物量相关分析。",
                interpretation="输出为 LUT 最近邻参数，不是连续优化结果；网格边界堆积提示超出 LUT。",
                check="检查 0.2–6.0 网格范围、边界值比例、波长数组长度及地面样点一致性。",
                warning="不得把固定参数 LUT 的最近邻结果当作唯一物理解或绝对真值。",
                downstream="用于地块 LAI 汇总、时序比较和独立样点校准。",
                unit="m²/m²", range_text="LUT 网格 0.2–6.0", format_name="GeoTIFF", vis="raster_continuous",
                related_outputs=["data.lai_mean", "data.lai_max", "data.lut_size"],
            ),
            "files.cab_tif": _row(
                "files.cab_tif", "Cab 反演图", description="最相似 PROSAIL LUT 光谱对应的叶绿素 Cab 单波段 GeoTIFF。",
                effect="把每像元光谱匹配到 10–70 的离散 Cab 网格。",
                business="用于叶绿素状态和冠层生化差异分析。",
                interpretation="输出为 LUT 最近邻 Cab；与 LAI 联合匹配，存在参数等效性。",
                check="检查 10–70 网格范围、边界堆积、波长覆盖和地面叶绿素样点。",
                warning="不得忽略 LAI/Cab 耦合、土壤和观测几何固定造成的不确定性。",
                downstream="用于地块叶绿素汇总、胁迫分析和地面校准。",
                unit="µg/cm²", range_text="LUT 网格 10–70", format_name="GeoTIFF", vis="raster_continuous",
                related_outputs=["data.cab_mean", "data.model", "data.wavelengths_nm"],
            ),
            "files.preview_png": _preview("files.preview_png", "PROSAIL LAI", "files.lai_tif"),
            **{
                f"data.{key}": _simple_data(
                    f"data.{key}", label, description, interpretation, warning=warning,
                    vis="array" if key == "wavelengths_nm" else "json_table",
                )
                for key, label, description, interpretation, warning in (
                    ("model", "物理模型", "实际 LUT 模型标识 PROSAIL-5 + 4SAIL。", "说明光谱由叶片与冠层辐射传输模型组合生成。", "模型名不代表所有输入参数均已针对场景校准。"),
                    ("lut_size", "LUT 光谱数", "LAI 12 点与 Cab 8 点笛卡尔积的光谱数量。", "当前默认应为 96 条；描述搜索规模而非有效样本量。", "LUT 大小不等同反演精度或不确定度。"),
                    ("lai_mean", "LAI 均值", "LAI 栅格全景均值。", "应落在 LUT 网格范围内，需检查边界堆积。", "全景均值不能替代地块分布和地面验证。"),
                    ("lai_max", "LAI 最大值", "LAI 栅格最大网格值。", "接近 6.0 可能是 LUT 上边界饱和。", "最大值等于边界不证明真实 LAI 就是该值。"),
                    ("cab_mean", "Cab 均值", "Cab 栅格全景均值。", "应落在 10–70 网格范围内，需结合 LAI 解释。", "不得脱离单位、LUT 固定参数和地面样点解释。"),
                    ("wavelengths_nm", "匹配波长数组", "用于插值 PROSAIL 光谱和匹配输入各波段的动态波长数组。", "第 i 项对应输入第 i 波段；缺省时按默认起止值线性生成。", "长度或顺序不匹配会使光谱角比较失去物理意义。"),
                )
            },
        },
    },
}


L3_OUTPUT_KNOWLEDGE.update(
    {
        "34_svm_rf_classify": {
            "summary": _summary(
                "用正标签像元训练 SVM 或随机森林，并对整景逐像元分类。",
                "输出类别图和同场景随机留出测试集 OA/AA/Kappa。",
                "0 类仅在训练样本筛选时忽略；整景仍会全部预测，指标没有业务验收阈值。",
            ),
            "outputs": _classification_outputs(
                "SVM/随机森林",
                extras={
                    "n_train": ("训练样本数", "随机拆分后用于训练的正标签像元数。", "受 test_size 和有效标注量决定。"),
                    "n_test": ("测试样本数", "随机拆分后用于评估的正标签像元数。", "来自同一场景，不是独立外部验证。"),
                    "classes": ("类别 ID 集合", "有效正标签中出现的动态类别 ID。", "需与外部类别字典映射，不存在大小顺序。"),
                    "model": ("模型类型", "实际使用的 svm 或 rf 标识。", "svm 还使用 kernel；rf 使用固定随机种子。"),
                },
            ),
        },
        "35_spectral_matching": {
            "summary": _summary(
                "以端元 CSV 各列为类别，计算 SAM 光谱角或 SID 散度并取最小距离分类。",
                "无需训练标签即可生成端元匹配类别图和最小距离图。",
                "score_mean 是距离均值，越小匹配越接近；SAM 与 SID 数值不可直接横向比较。",
            ),
            "outputs": {
                "files.pred_map_tif": _row(
                    "files.pred_map_tif",
                    "SAM/SID 端元匹配分类图",
                    description="逐像元最小端元距离对应的单波段类别 ID GeoTIFF；端元 CSV 第 k 列对应类别 ID=k+1。",
                    effect="对每个像元计算其到全部端元的 SAM 光谱角或 SID 散度，并写出最小距离端元的列序类别。",
                    business="提供各端元最佳匹配区域，支持端元覆盖制图和候选区域筛选。",
                    interpretation="类别 ID 只由端元 CSV 列顺序决定；必须保留端元 CSV 才能恢复类别语义。",
                    check="核对端元 CSV 波段数与影像一致、列顺序、分类 ID 与最小距离 argmin 的对应关系。",
                    warning="类别 ID 不是置信度、业务等级或监督分类结果；更换端元列顺序会改变 ID 语义。",
                    downstream="用于端元匹配制图、面积汇总、低匹配区检查和端元迭代。",
                    format_name="GeoTIFF",
                    vis="raster_class",
                    related_outputs=["files.angle_tif", "data.method", "data.classes"],
                ),
                "files.angle_tif": _row(
                    "files.angle_tif", "最小匹配距离图",
                    description="每像元对所有端元距离的最小值；SAM 为弧度光谱角，SID 为光谱信息散度。",
                    effect="保留获胜端元对应的匹配距离，越小表示与该端元越匹配。",
                    business="用于定位低可信匹配区、端元代表性不足区和类别边界。",
                    interpretation="越小匹配越近；SAM 与 SID 的定义和尺度不同，不能共用阈值。",
                    check="抽样核对归一化、端元列顺序、最小距离与分类 ID 的 argmin 关系。",
                    warning="文件名 angle_tif 在 SID 模式下仍保存 SID 散度，不是角度。",
                    downstream="用于匹配质量分层、端元迭代和候选像元筛选。",
                    format_name="GeoTIFF", vis="raster_score",
                    related_outputs=["files.pred_map_tif", "data.method", "data.score_mean"],
                ),
                "files.preview_png": _preview(
                    "files.preview_png", "SAM/SID 分类", "files.pred_map_tif", categorical=True
                ),
                "data.method": _simple_data(
                    "data.method", "匹配方法", "实际采用 sam 或 sid。",
                    "sam 输出最小光谱角；sid 输出最小对称信息散度。",
                    warning="不同方法的分数尺度和阈值不可直接比较。",
                ),
                "data.n_endmembers": _simple_data(
                    "data.n_endmembers", "端元数", "端元 CSV 的动态列数。",
                    "每列形成一个类别，分类 ID 从 1 开始并按 CSV 列顺序对应。",
                    warning="端元数量不是分类质量指标，且不得脱离 CSV 列顺序解释类别。",
                ),
                "data.score_mean": _simple_data(
                    "data.score_mean", "最小距离均值", "最小匹配距离图的全景均值。",
                    "越小通常表示场景整体更接近所给端元；仅同方法、同预处理可比。",
                    warning="不是置信概率；SAM 和 SID 均值不能直接横向比较。",
                ),
                "data.classes": _simple_data(
                    "data.classes", "实际类别 ID", "分类图中出现的动态类别 ID 集合。",
                    "ID 对应端元 CSV 列序号加 1，不代表类别等级。",
                    warning="必须保留端元 CSV 才能恢复类别语义。", vis="array",
                ),
            },
        },
        "36_cnn1d_classify": {
            "summary": _summary(
                "训练 Hu2015 结构的一维卷积网络进行逐像元光谱分类。",
                "输出整景类别图、测试集指标、设备和网络结构元数据。",
                "训练/测试来自同一场景正标签像元；未输出概率图，指标无业务验收阈值。",
            ),
            "outputs": _classification_outputs(
                "Hu2015 1D-CNN",
                extras={
                    "n_train": ("训练样本数", "用于神经网络训练的正标签像元数。", "受随机拆分和有效标签数量决定。"),
                    "n_test": ("测试样本数", "用于 OA/AA/Kappa 的留出像元数。", "来自同一场景随机拆分。"),
                    "classes": ("类别 ID 集合", "训练标签中的动态正类别 ID。", "预测内部索引会映射回原类别 ID。"),
                    "device": ("计算设备", "本次 PyTorch 使用的 mps、cuda 或 cpu。", "影响性能和数值可复现细节，不代表精度。"),
                    "architecture": ("网络结构", "实际模型标识 Hu2015_1DCNN。", "光谱卷积核长度会随输入波段数自适应。"),
                    "epochs": ("训练轮数", "服务采用的训练 epoch 参数。", "至少执行 1 轮；轮数不是收敛证明。"),
                },
            ),
        },
        "37_cnn3d_classify": {
            "summary": _summary(
                "先对整景 PCA，再以中心像元 patch 训练 HybridSN 3D+2D CNN。",
                "同时利用光谱与邻域空间结构生成整景类别图。",
                "PCA 在整景上拟合且随机拆分 patch，测试指标不等同独立场景泛化；无业务验收阈值。",
            ),
            "outputs": _classification_outputs(
                "HybridSN",
                extras={
                    "n_train": ("训练 patch 数", "随机拆分后用于训练的有标签中心 patch 数。", "每个 patch 以标签像元为中心。"),
                    "n_test": ("测试 patch 数", "用于评估的留出中心 patch 数。", "相邻 patch 可重叠并共享邻域。"),
                    "classes": ("类别 ID 集合", "有效训练标签中的动态类别 ID。", "内部连续索引最终映射回原 ID。"),
                    "device": ("计算设备", "本次 PyTorch 使用设备。", "影响运行性能，不是质量指标。"),
                    "bands_after_pca": ("PCA 后波段数", "实际 PCA 主成分数量，受请求值、原波段和像元数约束。", "是 HybridSN 输入光谱深度，不对应原始单个波长。"),
                    "architecture": ("网络结构", "实际结构标识 HybridSN。", "包含三层 3D 卷积和一层 2D 卷积。"),
                    "patch_size": ("空间 patch 尺寸", "中心像元邻域的方形边长。", "必须为不小于 3 的奇数，边界采用 edge padding。"),
                    "epochs": ("训练轮数", "实际训练 epoch 参数。", "至少执行 1 轮，不代表模型已收敛。"),
                },
            ),
        },
        "38_transformer_classify": {
            "summary": _summary(
                "用相邻波段滑窗 token 和两层编码器的 SpectralFormer 分类。",
                "输出整景类别图、测试指标及网络和设备元数据。",
                "模型只利用单像元光谱序列，不是 GCN；同景随机留出指标无业务验收阈值。",
            ),
            "outputs": _classification_outputs(
                "SpectralFormer",
                extras={
                    "n_train": ("训练样本数", "用于训练的正标签像元数。", "来自同场景随机拆分。"),
                    "n_test": ("测试样本数", "用于评估的留出正标签像元数。", "不是独立场景样本。"),
                    "classes": ("类别 ID 集合", "有效训练标签中的动态类别 ID。", "预测会映射回这些原始 ID。"),
                    "device": ("计算设备", "本次 PyTorch 运行设备。", "不代表模型质量。"),
                    "architecture": ("网络结构", "实际返回 SpectralFormer。", "相邻波段 token 经两层 TransformerEncoder 和跨层残差。"),
                    "epochs": ("训练轮数", "服务采用的 epoch 参数。", "至少执行 1 轮，不是收敛或泛化保证。"),
                },
            ),
        },
        "39_few_shot_classify": {
            "summary": _summary(
                "每类随机选至多 shots 个支持像元求均值原型，再以 SAM 最近原型分类。",
                "在极少标注下生成整景分类，并在剩余标注查询样本存在时报告指标。",
                "这不是经过梯度训练的迁移学习模型；若每类样本都被支持集占用，OA/AA/Kappa/n_query 不返回。",
            ),
            "outputs": _classification_outputs(
                "少样本 SAM 原型",
                optional_metrics=True,
                extras={
                    "shots": ("每类请求 shots", "每类最多抽取的支持样本数。", "实际每类取 min(shots, 该类样本数)。"),
                    "n_support": ("支持样本总数", "所有类别实际用于构建原型的像元总数。", "各类贡献可能因样本不足而少于 shots。"),
                    "classes": ("原型类别 ID", "成功构建原型的动态正类别 ID。", "整景预测只会落入这些类别。"),
                    "n_query": ("查询样本数", "未进入支持集且标签大于 0 的评估样本数。", "仅查询样本存在时与指标一起返回。"),
                },
            ),
        },
    }
)


L3_OUTPUT_KNOWLEDGE.update(
    {
        "40_detect_segment": {
            "summary": _summary(
                "由低 NDVI 像元估计目标光谱，计算 ACE 分数并在高分侧分位阈值后去除小斑。",
                "输出目标相似度、二值掩膜、连通斑块矢量及可选输入标注副本。",
                "低 NDVI 仅用于生成目标端元，不是业务胁迫真值；ACE 高分表示更像该目标。",
            ),
            "outputs": {
                "files.score_tif": _row(
                    "files.score_tif", "ACE 目标分数图",
                    description="每像元相对低 NDVI 目标光谱的 ACE 自适应余弦分数 GeoTIFF。",
                    effect="在背景协方差白化后衡量像元与目标方向的一致性。",
                    business="用于排序潜在胁迫候选并识别高相似区域。",
                    interpretation="分数越高越接近目标方向；最终掩膜取 ace_percentile 对应的高分侧。",
                    check="核对目标种子数量、协方差稳定性、分位阈值和高分区空间合理性。",
                    warning="ACE 分数不是胁迫概率；目标由本景低 NDVI 像元均值启发式生成。",
                    downstream="用于阈值调整、候选斑块排序和现场核查。",
                    format_name="GeoTIFF", vis="raster_score",
                    related_outputs=["files.mask_tif", "data.ace_percentile", "data.threshold_ndvi"],
                ),
                "files.mask_tif": _row(
                    "files.mask_tif", "ACE 检测二值掩膜",
                    description="ACE 高分侧分位阈值、可选形态学开运算和 min_pixels 过滤后的 0/1 栅格。",
                    effect="把连续相似度转为候选目标区域。",
                    business="用于候选面积统计、连通斑块矢量化和现场任务规划。",
                    interpretation="1=保留的目标候选，0=其他；不是人工确认的真实类别。",
                    check="复核 score>=分位阈值、形态学和连通域过滤后的像元数。",
                    warning="不得把 1 直接解释为已确认胁迫或病害。",
                    downstream="用于对象矢量化、面积统计和人工审核。",
                    format_name="GeoTIFF", vis="raster_mask",
                    bands=[{"name": "mask", "description": "0=非候选，1=ACE 高分候选"}],
                    related_outputs=["files.score_tif", "files.polygons_geojson", "data.n_positive_pixels"],
                ),
                "files.polygons_geojson": _row(
                    "files.polygons_geojson", "检测斑块 GeoJSON",
                    description="二值掩膜连通域矢量化的 FeatureCollection；properties 精确包含 object_id、class='stress_candidate'、area_pixels。",
                    effect="把候选像元聚合为空间对象。",
                    business="便于 GIS 审核、巡检任务和对象级统计。",
                    interpretation="每个 Feature 对应一个连通域；area_pixels 是像元数，不是地图面积。",
                    check="核对 Feature 数与 n_objects、几何位置、CRS 和 area_pixels。",
                    warning="未换算物理面积，且 stress_candidate 只是候选标签。",
                    downstream="用于 GIS 叠加、现场导航和人工标注。",
                    format_name="GeoJSON", vis="vector",
                    related_outputs=["files.mask_tif", "data.n_objects"],
                ),
                "files.annotation_geojson": _row(
                    "files.annotation_geojson", "输入标注/AOI 副本",
                    description="当 file2 为 .json/.geojson 时保存的原始上传文件路径。",
                    effect="将用户提供的标注或 AOI 与本次检测作业关联。",
                    business="支持结果追溯和后续人工对照。",
                    interpretation="当前服务只统计 features 数，不用该几何约束 ACE 计算或评价。",
                    check="核对文件类型、FeatureCollection 结构和 annotation_features。",
                    warning="不得误认为该标注已参与训练、阈值选择或精度评估。",
                    downstream="用于人工叠加、审阅和外部评价。",
                    format_name="GeoJSON", vis="vector", optional=True,
                    conditional="仅提供 GeoJSON 标注/AOI 作为 file2 时输出",
                    related_outputs=["data.has_annotation_geojson", "data.annotation_features"],
                ),
                "files.preview_png": _preview("files.preview_png", "ACE 分数", "files.score_tif"),
                **{
                    f"data.{key}": _simple_data(
                        f"data.{key}", label, description, interpretation, warning=warning
                    )
                    for key, label, description, interpretation, warning in (
                        (
                            "threshold_ndvi",
                            "原始 NDVI 种子阈值回显",
                            "原始 percentile 对应的 NDVI 阈值；响应始终仍返回该值。",
                            "初始种子少于 3 个像元时，服务会按 min(percentile+20, 50) 的更高分位回退并重选种子，因此此回显不一定是实际种子阈值。",
                            "不是最终 ACE 掩膜阈值；发生回退时也不得用该值复算实际目标种子。",
                        ),
                        ("ace_percentile", "ACE 分位参数", "用于 ACE 高分侧检测的百分位参数。", "分位越高通常保留像元越少，但形态学会进一步改变数量。", "不是跨场景固定分数阈值。"),
                        ("n_objects", "候选对象数", "最终掩膜连通域数量。", "应与 polygons_geojson Feature 数一致。", "对象数受分辨率、阈值和连通性影响，不能直接代表事件数。"),
                        ("n_positive_pixels", "候选像元数", "最终 0/1 掩膜中值为 1 的像元数。", "是形态学和小斑过滤后的数量。", "未乘像元面积，不能直接当物理面积。"),
                        ("has_annotation_geojson", "是否接收标注 GeoJSON", "file2 是否为被识别的 JSON/GeoJSON。", "仅表示文件被记录，不表示参与计算。", "不得当作有监督评价已完成的标志。"),
                        ("annotation_features", "标注要素数", "输入标注字典 features 数组长度。", "只做结构计数，不验证几何有效性。", "要素数不是标注像元数或准确率。"),
                    )
                },
            },
        },
        "41_unmixing": {
            "summary": _summary(
                "用端元 CSV 和增广 NNLS 实现 FCLS 非负、和为一丰度估计。",
                "输出每个端元的像元丰度和全景丰度统计。",
                "丰度波段数动态等于端元 CSV 列数，顺序严格对应 CSV 列顺序；并非固定类别数。",
            ),
            "outputs": {
                "files.abundance_tif": _row(
                    "files.abundance_tif", "FCLS 丰度立方体",
                    description="动态 K 波段 GeoTIFF，输出波段 k 对应端元 CSV 第 k 列的丰度。",
                    effect="把混合光谱分解为非负端元贡献，并归一化使每像元丰度和接近 1。",
                    business="用于亚像元组分比例、混合地物分析和端元覆盖制图。",
                    interpretation="波段与端元 CSV 列顺序一一对应，动态长度 K=n_endmembers；丰度通常在 [0,1]。",
                    check="逐波段核对端元 CSV 列顺序、非负性和像元丰度和，并检查零和异常。",
                    warning="不得固化端元数量或脱离原 CSV 列名解释波段；丰度是线性混合模型估计。",
                    downstream="用于组分地块统计、纯像元筛选和混合模型诊断。",
                    format_name="GeoTIFF（动态波段）", vis="raster_cube",
                    related_outputs=["data.n_endmembers", "data.abundance_mean", "data.sum_to_one_mean"],
                ),
                "files.preview_png": _preview("files.preview_png", "第 1 端元丰度", "files.abundance_tif"),
                "data.n_endmembers": _simple_data(
                    "data.n_endmembers", "端元数", "端元 CSV 的动态列数，也是丰度 GeoTIFF 波段数。",
                    "决定丰度向量长度；必须保留 CSV 列顺序映射。",
                    warning="端元数不是固定值，也不表示解混质量。",
                ),
                "data.abundance_mean": _simple_data(
                    "data.abundance_mean", "逐端元平均丰度", "按丰度波段顺序计算的动态均值数组。",
                    "第 k 项对应端元 CSV 第 k 列，可用于全景组分概览。",
                    warning="全景均值受场景组成影响，不是端元纯度或模型拟合误差。",
                    vis="array",
                ),
                "data.sum_to_one_mean": _simple_data(
                    "data.sum_to_one_mean", "丰度和均值", "各像元全部端元丰度和的全景平均。",
                    "FCLS 归一化后通常接近 1；零解像元可能拉低该值。",
                    warning="接近 1 只验证约束，不证明端元完整或重构误差小。",
                ),
            },
        },
        "42_anomaly_detect": {
            "summary": _summary(
                "计算全局 RX 或双窗局部 RX 马氏距离，并在高分侧分位阈值后去小斑。",
                "输出异常分数、二值候选掩膜和分数统计。",
                "分数越高表示相对所估背景越异常，不等于特定目标概率；阈值是场景内分位数。",
            ),
            "outputs": {
                "files.score_tif": _row(
                    "files.score_tif", "RX 异常分数图", description="全局或局部背景下的平方马氏距离 GeoTIFF。",
                    effect="衡量像元光谱相对背景均值和协方差的偏离程度。",
                    business="用于无监督发现稀有光谱、异常设备响应或潜在目标。",
                    interpretation="分数越高越异常；local_rx 使用排除中心内窗的局部背景，小图可能回退全局 RX。",
                    check="核对方法、协方差稳定性、分数有限性和高分空间分布。",
                    warning="高分可能来自噪声、阴影、边缘或坏波段，不是目标类别概率。",
                    downstream="用于异常候选排序、现场核查和坏数据筛查。",
                    format_name="GeoTIFF", vis="raster_score",
                    related_outputs=["files.mask_tif", "data.threshold", "data.method"],
                ),
                "files.mask_tif": _row(
                    "files.mask_tif", "RX 异常掩膜", description="score>=场景分位阈值并过滤小连通域后的 0/1 GeoTIFF。",
                    effect="把连续异常分数转换为高分候选区。",
                    business="支持候选像元计数、对象提取和人工审核。",
                    interpretation="1=保留异常候选，0=其他；分位阈值前固定选择高分侧。",
                    check="复核 percentile、threshold、min_pixels 和 n_anomaly_pixels。",
                    warning="候选掩膜不是已确认异常类型或业务告警。",
                    downstream="用于对象分析、样本标注和复核任务。",
                    format_name="GeoTIFF", vis="raster_mask",
                    bands=[{"name": "mask", "description": "0=背景，1=高 RX 分数候选"}],
                ),
                "files.preview_png": _preview("files.preview_png", "RX 异常分数", "files.score_tif"),
                **{
                    f"data.{key}": _simple_data(
                        f"data.{key}", label, description, interpretation, warning=warning
                    )
                    for key, label, description, interpretation, warning in (
                        ("method", "RX 方法", "实际使用 reed_xiaoli 或 local_rx。", "local_rx 估局部背景；小图或窗口不足时内部可回退全局计算。", "方法名不能替代窗口和输入波段记录。"),
                        ("percentile", "异常分位参数", "在分数分布上取阈值的百分位。", "越高通常保留更少的原始高分像元。", "不是跨场景固定分数阈值。"),
                        ("threshold", "异常分数阈值", "本景 score 指定分位数的实际值。", "score>=threshold 才进入小斑过滤。", "只适用于本次分数分布和方法。"),
                        ("n_anomaly_pixels", "异常候选像元数", "小斑过滤后掩膜为 1 的像元数。", "可能少于分位阈值直接选中的数量。", "不是物理面积或真实异常数量。"),
                        ("score_min", "分数最小值", "RX 分数图最小值。", "用于检查数值范围和异常计算。", "不能单独评价检测质量。"),
                        ("score_max", "分数最大值", "RX 分数图最大值。", "反映本景最强偏离，但易受孤立噪声影响。", "不能当跨场景统一严重度。"),
                        ("score_mean", "分数均值", "RX 分数图全景均值。", "描述本景分数尺度，受波段数和背景协方差影响。", "不同方法、窗口或波段数下不可直接比较。"),
                    )
                },
            },
        },
        "43_change_detect": {
            "summary": _summary(
                "对两时相共同左上尺寸和最小共同波段执行 IR-MAD，并以 chi² 高分侧分位数检测变化。",
                "输出 MAD 幅度、chi² 分数、二值变化候选和典型相关元数据。",
                "当前实现不检查配准、CRS 或完整尺寸一致性；高分表示变化更强，也可能来自错位和辐射差异。",
            ),
            "outputs": {
                "files.magnitude_tif": _row(
                    "files.magnitude_tif", "IR-MAD 变化幅度图", description="标准化 MAD 变量平方和开方得到的连续幅度 GeoTIFF。",
                    effect="汇总多个 MAD 分量的标准化差异强度。",
                    business="用于变化强度排序、分区汇总和热点分析。",
                    interpretation="值越高通常表示两时相差异越强；与 chi2_tif 单调相关但一个开方。",
                    check="核对输出尺寸为两景共同最小范围、有限值和配准边缘。",
                    warning="高幅度不区分真实地物变化、错位、云影或辐射尺度差异。",
                    downstream="用于变化强度制图和对象级汇总。",
                    format_name="GeoTIFF", vis="raster_score",
                    related_outputs=["files.chi2_tif", "files.mask_tif"],
                ),
                "files.chi2_tif": _row(
                    "files.chi2_tif", "IR-MAD chi² 分数图", description="各标准化 MAD 分量平方和的连续 GeoTIFF。",
                    effect="形成用于迭代权重和最终高分侧阈值的变化统计量。",
                    business="用于变化候选筛选和相对显著性排序。",
                    interpretation="分数越高表示变化越强；服务按场景 percentile 取高分候选。",
                    check="核对 chi2_df、分位阈值、典型相关和配准质量。",
                    warning="实现以经验分位数切分，不是按理论 chi² 显著性水平直接判定。",
                    downstream="用于阈值调整、变化排序和掩膜复算。",
                    format_name="GeoTIFF", vis="raster_score",
                    related_outputs=["data.threshold", "data.percentile", "files.mask_tif"],
                ),
                "files.mask_tif": _row(
                    "files.mask_tif", "变化候选掩膜", description="chi² 分数大于等于本景分位阈值的 0/1 GeoTIFF。",
                    effect="把连续变化统计量转为高分候选区域。",
                    business="用于变化面积、地块和对象汇总。",
                    interpretation="1=相对高变化分数，0=其他；没有形态学去噪。",
                    check="复算 score>=threshold 并核对 n_change。",
                    warning="不得把 1 直接解释为已确认业务变化类别。",
                    downstream="用于地块变化统计、对象提取和人工核查。",
                    format_name="GeoTIFF", vis="raster_mask",
                    bands=[{"name": "mask", "description": "0=未选中，1=高 chi² 变化候选"}],
                ),
                "files.preview_png": _preview("files.preview_png", "IR-MAD chi²", "files.chi2_tif"),
                **{
                    f"data.{key}": _simple_data(
                        f"data.{key}", label, description, interpretation, warning=warning,
                        vis="array" if key == "canonical_correlations" else "json_table",
                    )
                    for key, label, description, interpretation, warning in (
                        ("canonical_correlations", "典型相关系数", "各共同波段维度 IR-MAD 典型变量的动态相关系数数组。", "越接近 1 表示对应典型变量跨时相越稳定；长度为共同最小波段数。", "不能脱离迭代收敛、配准和波段对应关系解释。"),
                        ("chi2_mean", "chi² 均值", "chi² 分数图全景均值。", "描述本景变化分数整体尺度。", "不同波段数和场景分布下不可直接比较。"),
                        ("chi2_df", "chi² 自由度", "当前参与 IR-MAD 的共同最小波段数。", "决定 chi² 统计量维度，但当前阈值仍使用经验分位数。", "不得据此宣称已执行理论显著性检验。"),
                        ("percentile", "变化分位参数", "用于 chi² 高分侧阈值的百分位。", "越高通常选中更少像元。", "不是跨场景固定变化标准。"),
                        ("threshold", "变化分数阈值", "本景 chi² 指定分位数实际值。", "chi²>=该值被标为候选变化。", "只适用于本次输入和波段维度。"),
                        ("n_change", "变化候选像元数", "最终二值掩膜中值为 1 的像元数。", "未做物理面积换算。", "不能直接代表变化事件数或变化面积。"),
                    )
                },
            },
        },
        "44_postprocess_smooth": {
            "summary": _summary(
                "先做邻域众数滤波，再把小于 min_pixels 的同类连通斑块填为边界众数。",
                "减少分类椒盐噪声和孤立小斑，输出平滑类别图。",
                "处理会修改类别边界且包含背景类；window 偶数不会自动改为奇数，只保证至少 3。",
            ),
            "outputs": {
                "files.labels_tif": _row(
                    "files.labels_tif", "平滑分类标签图", description="众数滤波与小斑替换后的单波段类别 ID GeoTIFF。",
                    effect="改变局部标签以增强空间连续性并去除小连通斑。",
                    business="用于改善分类图可读性和后续对象/地块统计稳定性。",
                    interpretation="像元值仍是离散类别 ID；与输入差异由 n_changed 统计。",
                    check="对照输入检查边界、稀有类别保留、窗口尺寸和小斑替换结果。",
                    warning="可能抹去真实小目标或窄线状地物，不会提高光谱分类证据。",
                    downstream="用于 GIS 制图、地块分类统计和人工复核。",
                    format_name="GeoTIFF", vis="raster_class",
                    related_outputs=["data.n_changed", "data.classes", "files.preview_png"],
                ),
                "files.preview_png": _preview(
                    "files.preview_png", "平滑分类", "files.labels_tif", categorical=True
                ),
                **{
                    f"data.{key}": _simple_data(
                        f"data.{key}", label, description, interpretation, warning=warning,
                        vis="array" if key == "classes" else "json_table",
                    )
                    for key, label, description, interpretation, warning in (
                        ("min_pixels", "最小斑块像元数", "小于该像元数的同类连通域会尝试替换为边界众数。", "值越大通常消除更多小斑。", "不是物理面积阈值，且可能删除真实小目标。"),
                        ("window", "众数窗口尺寸", "实际传给 generic_filter 的窗口 size=max(3, 请求值)。", "控制初始众数平滑邻域；当前服务不强制奇数。", "偶数窗口的中心语义与常见奇数邻域不同。"),
                        ("n_changed", "改变像元数", "最终标签与原始输入不同的像元数量。", "综合反映众数滤波和小斑替换影响。", "改变少不代表质量提升，改变多也不自动表示错误。"),
                        ("classes", "输出类别 ID", "平滑后实际存在的动态类别 ID 集合。", "类别可能因平滑完全消失；ID 无大小顺序。", "必须与输入类别字典联合解释。"),
                    )
                },
            },
        },
        "45_parcel_zonal_stats": {
            "summary": _summary(
                "对单波段栅格计算整景统计，并在提供 GeoJSON 时逐 Feature 栅格化做地块统计。",
                "连续模式输出描述统计，分类模式输出类别像元数和面积比例。",
                "无 file2 时 parcels 为空且只做整景统计；GeoJSON 缺省 CRS 按 EPSG:4326，all_touched=True。",
            ),
            "outputs": {
                "files.report_json": _row(
                    "files.report_json", "分区统计报告", description="包含 mode、地块计数、scene 短结构和动态 parcels 数组的 JSON。",
                    effect="把整景及可选地块统计汇总为可交换报告。",
                    business="用于地块看板、批量导出、区域排名和专题分析。",
                    interpretation="continuous 与 categorical 的 scene/parcels 字段结构不同，应按 mode 解析。",
                    check="核对模式、像元数、GeoJSON 覆盖、空地块和分类比例和。",
                    warning="不得假设 parcels 固定长度或两种 mode 使用同一字段结构。",
                    downstream="用于数据库入库、报表生成和地块级业务分析。",
                    format_name="JSON", vis="json",
                    related_outputs=["data.mode", "data.scene", "data.parcels"],
                ),
                "files.parcel_geojson": _row(
                    "files.parcel_geojson", "输入地块 GeoJSON 副本", description="当 file2 为 JSON/GeoJSON 时保存的上传地块文件路径。",
                    effect="把地块几何与统计报告关联。",
                    business="用于追溯统计边界和 GIS 叠加。",
                    interpretation="服务按 Feature 逐个栅格化；该文件本身不会写回统计属性。",
                    check="核对 CRS、Feature 数、几何有效性和与栅格覆盖关系。",
                    warning="不得把输入副本误认为已经附加统计结果的输出矢量。",
                    downstream="用于复算、地图叠加和边界审计。",
                    format_name="GeoJSON", vis="vector", optional=True,
                    conditional="仅提供 JSON/GeoJSON 地块作为 file2 时输出",
                    related_outputs=["files.report_json", "data.n_parcels"],
                ),
                "data.mode": _simple_data(
                    "data.mode", "统计模式", "请求的 continuous 或 categorical 模式字符串。",
                    "决定 scene 和 parcels 中使用连续统计还是类别计数结构。",
                    warning="服务未将其他字符串规范化为合法枚举；非 categorical 会走连续分支。",
                ),
                "data.n_parcels": _simple_data(
                    "data.n_parcels", "地块记录数", "zonal_by_geojson 实际返回的动态地块记录数量。",
                    "无 GeoJSON 时为 0；无 geometry 的 Feature 不进入结果。",
                    warning="不一定等于输入 Feature 数，且不代表所有地块都有像元。",
                ),
                "data.n_parcels_with_pixels": _simple_data(
                    "data.n_parcels_with_pixels", "有像元地块数", "pixel_count>0 的地块记录数量。",
                    "用于区分有效覆盖与空地块。",
                    warning="all_touched=True 会影响边界像元计入，不能当精确矢量面积覆盖数。",
                ),
                "data.scene": _metric(
                    "data.scene", "整景统计短结构",
                    "按 mode 返回短结构：continuous 为 mean/std/min/max；categorical 为 class_area_ratio/class_pixel_count。",
                    "用于概括整幅单波段栅格，不展开任何动态地块列表。",
                    check="连续模式复算四项统计；分类模式核对计数总和与比例和约为 1。",
                    warning="整景统计包含数组全部像元，当前实现未显式屏蔽 NoData。",
                    downstream="用于场景级摘要、批次比较和报告表头。",
                    format_name="JSON 短结构", vis="json",
                ),
                "data.parcels": _metric(
                    "data.parcels", "地块统计动态短结构数组",
                    "动态数组；每项为 id/name/pixel_count/properties 加连续分位统计或分类计数短结构。",
                    "逐地块表达栅格覆盖和统计，不预设地块数量或属性集合。",
                    check="逐项核对 pixel_count、空地块标志、连续统计或分类比例。",
                    warning="不得固化数组长度、地块属性或把像元比例直接当矢量面积比例。",
                    downstream="用于地块看板、筛选、排名和外部数据库入库。",
                    format_name="JSON 动态短结构数组", vis="json",
                ),
            },
        },
    }
)
