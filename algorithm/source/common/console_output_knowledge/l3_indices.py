"""算法 46–55 单波段植被指数的输出知识。"""
from __future__ import annotations

from typing import Any

from .l3 import _index_knowledge, _index_runtime_fields, _metric, _preview, _row, _simple_data, _summary


def _band_field(path: str, label: str, param: str, default_note: str) -> dict[str, Any]:
    """波段索引回显。"""
    return {
        path: _simple_data(
            path,
            label,
            f"本次计算使用的{label.replace('索引', '')} 0-based 索引，回显请求参数 {param}。",
            f"这是运行配置，不是观测结果。{default_note}",
            warning="不得把该索引当成波长（nm），也不能套用到其他传感器。",
        )
    }


def _unbounded_index(
    *,
    name: str,
    formula: str,
    file_key: str,
    meaning: str,
    range_text: str,
    check: str,
    warning: str,
) -> dict[str, Any]:
    """值域不必落在 [-1, 1] 的指数。"""
    outputs: dict[str, Any] = {
        f"files.{file_key}": _row(
            f"files.{file_key}",
            f"{name}专题图",
            description=f"逐像元按 {formula} 计算的单波段 GeoTIFF。",
            effect=f"把指定反射率通道映射为 {name}。",
            business=meaning,
            interpretation=f"当前实现不裁剪。{range_text}",
            check=check,
            warning=warning,
            downstream="用于相对分区、GIS 专题制图和地块统计，不能直接当含量。",
            unit="无量纲指数",
            range_text=range_text,
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
            f"{name}栅格全部有效像元的{label}，表示{role}。",
            f"{range_text}全景统计会掩盖空间异质性。",
            check="与 GeoTIFF 复算统计一致，并排除 NoData。",
            warning="全景统计不能替代分区统计或分布检查。",
            downstream="用于运行快检、批次对比和统计摘要。",
            unit="无量纲指数",
            range_text=range_text,
        )
    return {
        "summary": _summary(
            f"按 {formula} 逐像元计算{name}。",
            f"形成{meaning}的空间栅格和全景统计。",
            "结果依赖正确波段索引和可比反射率；PNG 仅供目视。",
        ),
        "outputs": outputs,
    }


def _attach_runtime(item: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    item["outputs"].update(fields)
    return item


def _two_band_nd(
    *,
    algorithm_id: str,
    name: str,
    formula: str,
    first_band: str,
    second_band: str,
    file_key: str,
    meaning: str,
    first_path: str,
    first_label: str,
    first_param: str,
    first_note: str,
    second_path: str,
    second_label: str,
    second_param: str,
    second_note: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item = _index_knowledge(
        algorithm_id=algorithm_id,
        name=name,
        formula=formula,
        first_band=first_band,
        second_band=second_band,
        file_key=file_key,
        meaning=meaning,
    )
    item["outputs"].update(
        _index_runtime_fields(
            name,
            first_path=first_path,
            first_label=first_label,
            first_param=first_param,
            first_default_note=first_note,
            second_path=second_path,
            second_label=second_label,
            second_param=second_param,
            second_default_note=second_note,
        )
    )
    if extra:
        item["outputs"].update(extra)
    return item


L3_INDEX_OUTPUT_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "46_reci": _attach_runtime(
        _unbounded_index(
            name="RECI",
            formula="NIR/RE − 1",
            file_key="reci_tif",
            meaning="红边叶绿素相关相对指数，不是叶绿素毫克数",
            range_text="比值减 1，通常非负，上限随反射率比变化，不是 [-1, 1]。",
            check="核对真实红边与近红外索引、有限值和分母接近零的像元。",
            warning="没有真实红边时不要算；不能把 RECI 写成叶绿素含量。",
        ),
        {
            **_band_field("data.re_band", "红边波段索引", "re_band", "默认 4 只对应演示数据，必须按真实红边波长核验。"),
            **_band_field("data.nir_band", "近红外波段索引", "nir_band", "默认 3 只对应演示数据。"),
            "data.shape": _simple_data(
                "data.shape", "输出栅格尺寸", "写出的 RECI GeoTIFF 行列尺寸，格式为 [行, 列]。",
                "应与输入空间尺寸一致；演示数据 为 16×16。",
                warning="shape 不是地块面积，也不能从预览 PNG 像素数反推。",
            ),
            "data.format": _simple_data(
                "data.format", "主产物格式", "主产物文件格式。当前实现写出 GeoTIFF。",
                "定量读数应打开 GeoTIFF，不要从 PNG 颜色反推。",
                warning="format 只说明容器，不保证已经过反射率定标或掩膜。",
            ),
        },
    ),
    "47_gndvi": _two_band_nd(
        algorithm_id="47_gndvi",
        name="GNDVI",
        formula="(NIR-GREEN)/(NIR+GREEN)",
        first_band="NIR",
        second_band="GREEN",
        file_key="gndvi_tif",
        meaning="用绿光代替红光的绿度相对指数",
        first_path="data.green_band",
        first_label="绿光波段索引",
        first_param="green_band",
        first_note="默认 1 只对应演示数据。",
        second_path="data.nir_band",
        second_label="近红外波段索引",
        second_param="nir_band",
        second_note="默认 3 只对应演示数据。",
    ),
    "48_osavi": _two_band_nd(
        algorithm_id="48_osavi",
        name="OSAVI",
        formula="(NIR-RED)/(NIR+RED+L)",
        first_band="NIR",
        second_band="RED",
        file_key="osavi_tif",
        meaning="固定土壤项的土壤调节植被指数",
        first_path="data.red_band",
        first_label="红光波段索引",
        first_param="red_band",
        first_note="默认 2 只对应演示数据。",
        second_path="data.nir_band",
        second_label="近红外波段索引",
        second_param="nir_band",
        second_note="默认 3 只对应演示数据。",
        extra={
            "data.L": _simple_data(
                "data.L",
                "土壤调节系数 L",
                "OSAVI 分母中的土壤项。Rondeaux 等 1996 年取 0.16；本仓库默认 0.16，允许改写。",
                "L=0 时公式退化成 NDVI 形式。文献推荐值不是现场标定。",
                warning="跨传感器、跨季节改 L 会破坏可比性；不要把 0.16 写成全球最优。",
            )
        },
    ),
    "49_arvi": _attach_runtime(
        _two_band_nd(
            algorithm_id="49_arvi",
            name="ARVI",
            formula="(NIR-RB)/(NIR+RB)",
            first_band="NIR",
            second_band="大气校正红光 RB",
            file_key="arvi_tif",
            meaning="用蓝光修正红光后的耐大气植被指数，不能替代大气校正",
            first_path="data.red_band",
            first_label="红光波段索引",
            first_param="red_band",
            first_note="默认 2 只对应演示数据。",
            second_path="data.nir_band",
            second_label="近红外波段索引",
            second_param="nir_band",
            second_note="默认 3 只对应演示数据。",
        ),
        {
            **_band_field("data.blue_band", "蓝光波段索引", "blue_band", "默认 0 只对应演示数据。"),
            "data.gamma": _simple_data(
                "data.gamma",
                "大气气溶胶权重 γ",
                "RB = RED − γ(BLUE − RED) 中的 γ。Kaufman 与 Tanré 常用 1。",
                "γ 不是本传感器现场标定；蓝光差时指数会乱。",
                warning="ARVI 不能代替大气校正产品；γ 改了就不能和未改的图横比。",
            ),
        },
    ),
    "50_vari": _attach_runtime(
        _unbounded_index(
            name="VARI",
            formula="(GREEN−RED)/(GREEN+RED−BLUE)",
            file_key="vari_tif",
            meaning="只用可见光估相对覆盖，不需要近红外",
            range_text="分母 GREEN+RED−BLUE 可能接近零或变号，值域不必落在 [-1, 1]。",
            check="核对蓝、绿、红索引，并检查分母接近零的像元。",
            warning="没有近红外不等于能替代 NDVI；阴影和土壤颜色会干扰。",
        ),
        {
            **_band_field("data.blue_band", "蓝光波段索引", "blue_band", "默认 0 只对应演示数据。"),
            **_band_field("data.green_band", "绿光波段索引", "green_band", "默认 1 只对应演示数据。"),
            **_band_field("data.red_band", "红光波段索引", "red_band", "默认 2 只对应演示数据。"),
            "data.shape": _simple_data(
                "data.shape", "输出栅格尺寸", "写出的 VARI GeoTIFF 行列尺寸，格式为 [行, 列]。",
                "应与输入空间尺寸一致。",
                warning="shape 不是地块面积。",
            ),
            "data.format": _simple_data(
                "data.format", "主产物格式", "主产物文件格式。当前实现写出 GeoTIFF。",
                "定量读数应打开 GeoTIFF。",
                warning="format 只说明容器。",
            ),
        },
    ),
    "51_lai_index": _attach_runtime(
        _unbounded_index(
            name="经验LAI",
            formula="max(3.618×EVI − 0.118, 0)",
            file_key="lai_index_tif",
            meaning="由 EVI 线性变换得到的经验叶面积指数，不是 #33 PROSAIL",
            range_text="实现把负值裁成 0；系数 3.618/−0.118 是本仓库演示数据默认，不是全球 LAI 产品。",
            check="核对蓝、红、近红外是否为反射率，并与 #33 产物区分文件名。",
            warning="不得把 lai_index.tif 写成实验室叶面积或 #33 物理反演。",
        ),
        {
            **_band_field("data.blue_band", "蓝光波段索引", "blue_band", "默认 0 只对应演示数据。"),
            **_band_field("data.red_band", "红光波段索引", "red_band", "默认 2 只对应演示数据。"),
            **_band_field("data.nir_band", "近红外波段索引", "nir_band", "默认 3 只对应演示数据。"),
            "data.shape": _simple_data(
                "data.shape", "输出栅格尺寸", "写出的 lai_index.tif 行列尺寸，格式为 [行, 列]。",
                "应与输入空间尺寸一致。",
                warning="shape 不是地块叶面积。",
            ),
            "data.format": _simple_data(
                "data.format", "主产物格式", "主产物文件格式。当前实现写出 GeoTIFF。",
                "定量读数应打开 GeoTIFF。",
                warning="format 只说明容器。",
            ),
        },
    ),
    "52_nbr": _two_band_nd(
        algorithm_id="52_nbr",
        name="NBR",
        formula="(NIR-SWIR)/(NIR+SWIR)",
        first_band="NIR",
        second_band="SWIR",
        file_key="nbr_tif",
        meaning="过火与过火严重度相对指数；形式接近 NDMI，波段窗口不同",
        first_path="data.nir_band",
        first_label="近红外波段索引",
        first_param="nir_band",
        first_note="默认 3 只对应演示数据。",
        second_path="data.swir_band",
        second_label="短波红外波段索引",
        second_param="swir_band",
        second_note="默认 5 只对应演示立方体约 1600 nm；Landsat NBR 常用 SWIR2 约 2.1 μm。",
    ),
    "53_sipi": _attach_runtime(
        _unbounded_index(
            name="SIPI",
            formula="(NIR−BLUE)/(NIR−RED)",
            file_key="sipi_tif",
            meaning="色素比值相关指数，对冠层结构相对不敏感，不是叶绿素毫克数",
            range_text="NIR≈RED 时分母接近零；值域不必落在 [-1, 1]。",
            check="核对蓝、红、近红外，并检查红光与近红外几乎相等的像元。",
            warning="不能把 SIPI 写成类胡萝卜素或叶绿素含量。",
        ),
        {
            **_band_field("data.blue_band", "蓝光波段索引", "blue_band", "默认 0 只对应演示数据。"),
            **_band_field("data.red_band", "红光波段索引", "red_band", "默认 2 只对应演示数据。"),
            **_band_field("data.nir_band", "近红外波段索引", "nir_band", "默认 3 只对应演示数据。"),
            "data.shape": _simple_data(
                "data.shape", "输出栅格尺寸", "写出的 SIPI GeoTIFF 行列尺寸，格式为 [行, 列]。",
                "应与输入空间尺寸一致。",
                warning="shape 不是地块面积。",
            ),
            "data.format": _simple_data(
                "data.format", "主产物格式", "主产物文件格式。当前实现写出 GeoTIFF。",
                "定量读数应打开 GeoTIFF。",
                warning="format 只说明容器。",
            ),
        },
    ),
    "54_gci": _attach_runtime(
        _unbounded_index(
            name="GCI",
            formula="NIR/GREEN − 1",
            file_key="gci_tif",
            meaning="绿色叶绿素相关相对指数，不是叶绿素毫克数",
            range_text="比值减 1，通常非负，上限随反射率比变化，不是 [-1, 1]。",
            check="核对绿光与近红外索引、有限值和绿光接近零的像元。",
            warning="不能把 GCI 写成叶绿素含量；与 RECI 同型但分母是绿光。",
        ),
        {
            **_band_field("data.green_band", "绿光波段索引", "green_band", "默认 1 只对应演示数据。"),
            **_band_field("data.nir_band", "近红外波段索引", "nir_band", "默认 3 只对应演示数据。"),
            "data.shape": _simple_data(
                "data.shape", "输出栅格尺寸", "写出的 GCI GeoTIFF 行列尺寸，格式为 [行, 列]。",
                "应与输入空间尺寸一致。",
                warning="shape 不是地块面积。",
            ),
            "data.format": _simple_data(
                "data.format", "主产物格式", "主产物文件格式。当前实现写出 GeoTIFF。",
                "定量读数应打开 GeoTIFF。",
                warning="format 只说明容器。",
            ),
        },
    ),
    "55_ndsi": _two_band_nd(
        algorithm_id="55_ndsi",
        name="NDSI",
        formula="(GREEN-SWIR)/(GREEN+SWIR)",
        first_band="GREEN",
        second_band="SWIR",
        file_key="ndsi_tif",
        meaning="积雪相对指数；与 MNDWI 同型，用途是雪不是水",
        first_path="data.green_band",
        first_label="绿光波段索引",
        first_param="green_band",
        first_note="默认 1 只对应演示数据。",
        second_path="data.swir_band",
        second_label="短波红外波段索引",
        second_param="swir_band",
        second_note="默认 5 只对应演示数据；必须是真实 SWIR。",
    ),
}
