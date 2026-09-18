"""参数字典种子：与设计规格 §5.2 对齐。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ParamDefinition

# (key, stage, type, default, description, advanced, sort)
PARAM_SEED: list[tuple] = [
    ("input_dir", "S0_io", "path", None, "输入 MAX_* 目录（宿主机绝对路径）。只读扫描，禁止把输出写进此树。", False, 10),
    ("output_dir", "S0_io", "path", None, "本次运行输出根目录。其下生成 拼图结果/、附件/、cache/、log/ 等。", False, 20),
    ("cache_dir", "S0_io", "path", None, "特征/空三缓存目录。续跑可复用，避免重复提特征。默认 {output_dir}/cache/features。", False, 30),
    ("log_dir", "S0_io", "path", None, "明码文本日志目录；执行记录保存此路径便于溯源。默认 {output_dir}/log。", False, 40),
    ("process_dir", "S0_io", "path", None, "中间过程图/调试产物根（与拼图结果分离）。默认 {output_dir}/附件。", True, 50),
    ("products_dir_name", "S0_io", "string", "拼图结果", "商业对齐的成果子目录名。", True, 60),
    ("run_mode", "S0_io", "enum", "full", "运行模式：full 全流程；until_stage 跑到 stop_after_stage 后等待继续；step 每阶段确认。", False, 70),
    ("start_stage", "S0_io", "enum", "S0_io", "从哪一阶段开始（须有检查点或从 S0）。", False, 80),
    ("stop_after_stage", "S0_io", "enum", None, "until_stage 时必填：跑完该阶段后进入 awaiting_continue。", False, 90),
    ("preset", "S0_io", "enum", None, "快捷预设：rgb_preview=仅 Color 正射，便于快速看几何结果。", False, 100),
    ("max_index", "S1_catalog", "int", None, "只扫描文件名编号 ≤ 该值的曝光，便于小范围调试。", False, 10),
    ("max_frames", "S1_catalog", "int", None, "过滤后最多使用前 N 个可用曝光。", False, 20),
    ("min_agl_m", "S1_catalog", "float", 5.0, "相对航高低于此值视为地面/无效帧丢弃。", False, 30),
    ("max_tilt_deg", "S1_catalog", "float", 60.0, "光轴偏离天底超过此角度丢弃（REQ-03-03）。", False, 40),
    ("drop_white_panel", "S1_catalog", "bool", True, "丢弃文件名角色 _W 白板帧（不参与重建）。", False, 50),
    ("require_pos", "S1_catalog", "bool", True, "无 XMP/EXIF POS 的帧丢弃。", True, 60),
    ("primary_band", "S2_at", "enum", "Color", "主波段：仅此波段做特征匹配与空三；其余波段迁移外方位。", False, 10),
    ("workers_at", "S2_at", "int", 10, "空三/特征提取并行度。", False, 20),
    ("sigma_xy_m", "S2_at", "float", 3.0, "GNSS 平面先验标准差（米）。", True, 30),
    ("sigma_z_m", "S2_at", "float", 5.0, "GNSS 高程先验标准差（米）。", True, 40),
    ("sigma_attitude_deg", "S2_at", "float", 3.0, "IMU 姿态先验标准差（度）。", True, 50),
    ("outlier_threshold_px", "S2_at", "float", 6.0, "重投影外点阈值（像素）。", True, 60),
    ("calibrate_intrinsics", "S2_at", "bool", True, "是否分阶段释放内参自标定。", True, 70),
    ("dsm_gsd", "S3_dense", "float", 0.107747293, "DSM 地面分辨率（米）；默认对齐商业成品。", False, 10),
    ("reuse_dsm", "S3_dense", "path", None, "若指定，跳过密集匹配，复用已有 DSM.tif。", False, 20),
    ("n_layers", "S3_dense", "int", 48, "沿高程扫描层数；越大越慢越细。", True, 30),
    ("z_margin_m", "S3_dense", "float", 12.0, "在稀疏先验面上下搜索半宽（米）。", True, 40),
    ("workers_dense", "S3_dense", "int", None, "密集匹配进程数，默认 CPU-1。", False, 50),
    ("spike_tolerance_m", "S4_dsm", "float", 2.5, "相对中值超过此高差视为尖刺剔除。", True, 10),
    ("max_fill_gap_m", "S4_dsm", "float", 40.0, "空洞填充最大跨度（米）。", True, 20),
    ("bands", "S5_ortho", "string[]", ["Color", "450nm", "550nm", "650nm", "720nm", "750nm", "800nm", "850nm"], "参与正射的波段。仅 RGB 快速预览时设为 [\"Color\"]。", False, 10),
    ("color_correction", "S5_ortho", "enum", "off_for_ms", "RGB 可开增益均衡；多光谱强制禁用保辐射。", True, 20),
    ("seamline_enabled", "S5_ortho", "bool", True, "是否计算拼接线。", False, 30),
    ("workers_ortho", "S5_ortho", "int", None, "正射并行度。", False, 40),
    ("write_pdf_report", "S6_report", "bool", True, "生成质量报告.pdf。", False, 10),
    ("write_json_report", "S6_report", "bool", True, "生成机器可读质量 JSON。", False, 20),
]

RGB_PREVIEW_VALUES = {
    "preset": "rgb_preview",
    "bands": ["Color"],
    "run_mode": "full",
}


def seed_param_definitions(db: Session) -> int:
    n = 0
    for key, stage, vtype, default, desc, advanced, sort in PARAM_SEED:
        existing = db.get(ParamDefinition, key)
        if existing is None:
            db.add(
                ParamDefinition(
                    key=key,
                    stage_id=stage,
                    value_type=vtype,
                    default_value=default,
                    description=desc,
                    advanced=advanced,
                    sort_order=sort,
                )
            )
            n += 1
        else:
            existing.description = desc
            existing.default_value = default
            existing.stage_id = stage
            existing.value_type = vtype
            existing.advanced = advanced
            existing.sort_order = sort
    db.commit()
    return n


def default_snapshot() -> dict:
    return {k: d for k, _, _, d, *_ in ((t[0], t[1], t[2], t[3]) for t in PARAM_SEED)}
