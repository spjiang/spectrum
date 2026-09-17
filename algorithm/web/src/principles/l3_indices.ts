import type { PrincipleDoc } from "./types";

const VIS = { b: "#5b8def", g: "#3d5648", r: "#c45c4a", re: "#b0893a", n: "#8c2f2f", s: "#6b4f8c" };

export const L3_INDEX_PRINCIPLES: PrincipleDoc[] = [
  {
    id: "46_reci",
    purpose: "用近红外除以红边再减 1，看叶绿素相关的相对差异。",
    why: "叶绿素把红边往长波推，红边反射相对近红外更低时，这个比值会变大。须有真红边。",
    formula: "RECI = NIR / RE − 1",
    formulaNote: "NIR、RE 须为反射率。本仓库分母加 1e-12 只防除零。值域不是 −1～1。",
    formulaItems: [
      {
        name: "RECI 红边叶绿素指数",
        eq: "RECI = NIR / RE − 1",
        note: "NIR 近红外、RE 红边，须为反射率。和 NDRE 不同：这是比值减 1，不是归一化差。没有真红边不要算。不能读成叶绿素毫克数。",
      },
    ],
    scenarioCases: [
      {
        title: "有真红边，想看叶绿素相关相对差异",
        body: "封垄以后 NDVI 已经不太动，如果相机真有红边通道，打开 reci.tif 看相对差异。这是比值，不是 −1 到 1。",
      },
      {
        title: "必须同一红边中心才能比",
        body: "换相机、换红边中心波长，同名 RECI 不能直接横比。",
      },
      {
        title: "不要读成缺氮毫克数",
        body: "没有真红边就不要算。要解释营养，须本地叶片实测或已知样地。",
      },
    ],
    steps: ["按索引取红边与近红外", "近红外除以红边再减 1", "写出 reci.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "RECI 用红边当除数，近红外当分子。",
      bands: [
        { id: "re", label: "红边 RE", nm: 720, color: VIS.re },
        { id: "nir", label: "近红外 NIR", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体（须有红边）" },
      { name: "re_band / nir_band", meaning: "默认 4 / 3，仅适用于演示数据" },
    ],
    outputs: [{ name: "reci.tif", meaning: "单波段比值指数，不是 −1～1" }],
    industryGap: "没有真红边时不要套默认索引。",
    checks: ["没有红边通道时，用红光冒充会怎样？"],
    summary: {
      definition: "红边叶绿素指数 RECI = 近红外反射率 / 红边反射率 − 1。",
      value: "密冠层叶绿素相关相对分区；不能直接当作叶绿素含量。",
      keyInput: "含真实红边与近红外的反射率立方体。",
      keyOutput: "单波段 reci.tif。",
      keyLimit: "没有真红边则无物理意义；值域不是 −1～1。",
    },
    background: [
      "红边约 700–740 nm，随叶绿素向长波移动。",
      "Gitelson 等把 NIR/RE − 1 称作红边叶绿素指数；叶片尺度相关不等于冠层毫克数。",
    ],
    prerequisites: ["输入须为反射率并掩膜云影与 NoData。", "确认传感器确有红边；默认 4/3 只对应演示数据。"],
    parameterNotes: [
      { name: "re_band", role: "指定红边通道", guidance: "按波长表选约 705–740 nm", effect: "不同中心对应不同叶绿素敏感度", risk: "把红光或近红外误作红边会改变含义" },
      { name: "nir_band", role: "指定近红外", guidance: "选稳定近红外平台", effect: "提供冠层结构参照", risk: "与红边过近会压缩动态范围" },
    ],
    resultInterpretation: [
      "数值较高通常表示红边相对更低、叶绿素相关响应更强；不是毫克数。",
      "跨期比较须固定红边中心和预处理。",
    ],
    applicable: ["具有窄红边波段的高光谱或红边多光谱。", "NDVI 已接近饱和、仍想看相对差异。"],
    notApplicable: ["没有红边却用相邻通道代替。", "要叶绿素化验值。"],
    risks: ["红边中心差异会让同名 RECI 不可横比。", "红边接近零时比值会很大。"],
    upstream: ["反射率校正、波长核验与有效像元掩膜。"],
    downstream: ["叶绿素相关相对分区、地块统计。"],
    demoFocus: ["光谱上定位红边斜坡与近红外平台。", "同一像元红边降低时 RECI 上升。"],
  },
  {
    id: "47_gndvi",
    purpose: "用绿光代替红光做归一化差，看绿度相关相对差异。",
    why: "绿光反射峰对叶绿素也敏感。有绿光和近红外就能算。",
    formula: "GNDVI = (NIR − GREEN) / (NIR + GREEN)",
    formulaNote: "须为反射率。本仓库分母加 1e-12 只防除零。",
    formulaItems: [
      {
        name: "GNDVI 绿色归一化植被指数",
        eq: "GNDVI = (NIR − GREEN) / (NIR + GREEN)",
        note: "NIR 近红外、GREEN 绿光。和 NDVI 同型，只是红光换成绿光。不是叶绿素毫克数。",
      },
    ],
    scenarioCases: [
      {
        title: "想用绿光通道看相对绿度",
        body: "有绿光和近红外反射率时，打开 gndvi.tif，看同一处理链里哪里更绿。",
      },
      {
        title: "不要和 NDVI 混成同一个阈值",
        body: "同名都叫植被指数，绿光窗口和红光窗口不是一回事，不要套 NDVI 的固定切分。",
      },
      {
        title: "不要读成叶绿素含量",
        body: "高覆盖时仍可能饱和。要解释营养，须本地实测。",
      },
    ],
    steps: ["取绿光与近红外", "归一化差", "写出 gndvi.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "GNDVI 用绿光反射峰和近红外高原。",
      bands: [
        { id: "green", label: "绿 GREEN", nm: 560, color: VIS.g },
        { id: "nir", label: "近红外 NIR", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体" },
      { name: "green_band / nir_band", meaning: "默认 1 / 3，仅适用于演示数据" },
    ],
    outputs: [{ name: "gndvi.tif", meaning: "单波段指数图，理论约 −1～1" }],
    industryGap: "绿光中心因传感器而异，不能死记默认 1。",
    checks: ["把红光误当成绿光，GNDVI 还叫这个名字吗？"],
    summary: {
      definition: "GNDVI = (近红外反射率 − 绿光反射率) / (近红外反射率 + 绿光反射率)。",
      value: "绿光通道的相对绿度；不能直接当作叶绿素含量。",
      keyInput: "绿光与近红外反射率。",
      keyOutput: "单波段 gndvi.tif。",
      keyLimit: "绿光窗口、饱和与土壤背景都会改变数值。",
    },
    background: [
      "绿光约 520–600 nm，是叶绿素吸收之间的反射峰。",
      "Gitelson 等 1996 年讨论在全球植被监测中使用绿光通道。",
    ],
    prerequisites: ["输入须为反射率并掩膜云影与 NoData。", "按传感器选绿光，默认 1 只对应演示数据。"],
    parameterNotes: [
      { name: "green_band", role: "指定绿光通道", guidance: "按波长表选绿光反射峰附近", effect: "决定叶绿素相关的可见光端", risk: "误选红光或红边会改变指数含义" },
      { name: "nir_band", role: "指定近红外", guidance: "选稳定近红外平台", effect: "提供冠层结构参照", risk: "选成红边或 SWIR 会失去意义" },
    ],
    resultInterpretation: [
      "较高正值通常更绿；水体近红外低，指数常偏低。",
      "比较须保持传感器、波段和处理链一致。",
    ],
    applicable: ["有绿光与近红外的反射率监测。"],
    notApplicable: ["原始 DN 硬算。", "要叶绿素化验值。"],
    risks: ["绿光窗口不同不能横比。", "分母接近零会产生极值。"],
    upstream: ["反射率定标与掩膜。"],
    downstream: ["相对绿度分区、地块统计。"],
    demoFocus: ["绿光峰与近红外平台。"],
  },
  {
    id: "48_osavi",
    purpose: "在 NDVI 分母上加固定土壤项，压土壤亮度。",
    why: "土很多时 NDVI 会被土壤亮度拽偏。OSAVI 把土壤项固定为文献常用的 0.16。",
    formula: "OSAVI = (NIR − RED) / (NIR + RED + L)",
    formulaNote: "文献 L=0.16。本仓库默认 0.16，允许改写。L=0 时退化成 NDVI 形式。",
    formulaItems: [
      {
        name: "OSAVI 优化土壤调节植被指数",
        eq: "OSAVI = (NIR − RED) / (NIR + RED + L)",
        note: "NIR 近红外、RED 红光。和 SAVI 同类，但文献把 L 固定为 0.16，不再乘 (1+L)。本仓库默认 L=0.16。L=0 就是 NDVI 那条归一化差。",
      },
    ],
    scenarioCases: [
      {
        title: "出苗、稀疏、土很多",
        body: "地还没封垄，亮土暗土会拽偏 NDVI。打开 osavi.tif，看固定土壤项之后相对绿度是否稳一些。",
      },
      {
        title: "L 不要随便改",
        body: "文献常用 0.16。改了 L，就不能和没改的图横比。不要把 0.16 当成现场标定。",
      },
      {
        title: "不要当成叶面积",
        body: "这是土壤调节后的绿度，不是产量，也不是 #29 的 SAVI/MSAVI。",
      },
    ],
    steps: ["取红光与近红外", "分母加 L 后做差比", "写出 osavi.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "OSAVI 仍用红光与近红外，只是分母多一个土壤项。",
      bands: [
        { id: "red", label: "红 RED", nm: 660, color: VIS.r },
        { id: "nir", label: "近红外 NIR", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体" },
      { name: "L", meaning: "默认 0.16，文献常用值" },
    ],
    outputs: [{ name: "osavi.tif", meaning: "单波段 OSAVI" }],
    industryGap: "0.16 来自 Rondeaux 等 1996 年的优化，不是本传感器现场值。",
    checks: ["L=0 时 OSAVI 与 NDVI 是什么关系？"],
    summary: {
      definition: "OSAVI = (近红外 − 红光) / (近红外 + 红光 + L)，文献取 L=0.16。",
      value: "稀疏植被时压土壤亮度的相对绿度；不是叶面积。",
      keyInput: "红光、近红外反射率与土壤项 L。",
      keyOutput: "单波段 osavi.tif。",
      keyLimit: "L 不是现场标定；改 L 后不可与未改图横比。",
    },
    background: [
      "Huete 的 SAVI 用可调 L 并乘 (1+L)。",
      "Rondeaux、Steven、Baret 1996 年给出 OSAVI，把 L 取 0.16。",
    ],
    prerequisites: ["输入须为反射率。", "默认 L=0.16 只是文献常用值。"],
    parameterNotes: [
      { name: "red_band", role: "指定红光", guidance: "约 630–690 nm", effect: "叶绿素吸收端", risk: "误选红边会改变含义" },
      { name: "nir_band", role: "指定近红外", guidance: "约 760–900 nm", effect: "叶片散射端", risk: "选成红边会压缩动态范围" },
      { name: "L", role: "土壤项", guidance: "文献常用 0.16", effect: "L 越大越压土壤，也越改尺度", risk: "跨时相改 L 会破坏可比性" },
    ],
    resultInterpretation: [
      "相对 NDVI，土多时 OSAVI 往往更稳；不是叶面积。",
      "比较须固定 L 和处理链。",
    ],
    applicable: ["土壤背景明显的稀疏植被。"],
    notApplicable: ["要自适应 L 请看 #29 MSAVI。", "要叶面积化验值。"],
    risks: ["L 改了不能横比。", "密冠层过大 L 会压敏感度。"],
    upstream: ["反射率定标与掩膜。"],
    downstream: ["稀疏植被相对绿度、地块统计。"],
    demoFocus: ["L=0 与 L=0.16 的差别方向。"],
  },
  {
    id: "49_arvi",
    purpose: "用蓝光修正红光，再做归一化差，减轻气溶胶一类残差。",
    why: "薄霾会抬高红光。蓝光对气溶胶更敏感，用来改红光后再和近红外比。",
    formula: "ARVI = (NIR − RB) / (NIR + RB)，RB = RED − γ(BLUE − RED)",
    formulaNote: "默认 γ=1。不能替代大气校正。",
    formulaItems: [
      {
        name: "1. 自校正红光 RB",
        eq: "RB = RED − γ × (BLUE − RED)",
        note: "γ 常用 1。蓝光差、阴影重时 RB 会乱。这不是已经做完大气校正。",
      },
      {
        name: "2. ARVI",
        eq: "ARVI = (NIR − RB) / (NIR + RB)",
        note: "用 RB 代替 NDVI 里的红光。须为反射率。本仓库分母加 1e-12。",
      },
    ],
    scenarioCases: [
      {
        title: "担心薄霾残差",
        body: "已经有反射率，仍觉得气溶胶在拽红光时，打开 arvi.tif 作对照。蓝光必须可靠。",
      },
      {
        title: "不要当成大气校正",
        body: "这只是指数里加了一项蓝光修正。要大气校正请走 #13。γ=1 不是本相机标定。",
      },
      {
        title: "蓝光差就不要硬看",
        body: "阴影重、蓝光噪声大时 ARVI 会比 NDVI 更乱。",
      },
    ],
    steps: ["取蓝、红、近红外", "按 γ 算 RB", "写出 arvi.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "ARVI 多用一个蓝光通道来改红光。",
      bands: [
        { id: "blue", label: "蓝", nm: 480, color: VIS.b },
        { id: "red", label: "红", nm: 660, color: VIS.r },
        { id: "nir", label: "近红外", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体" },
      { name: "gamma", meaning: "默认 1" },
    ],
    outputs: [{ name: "arvi.tif", meaning: "单波段 ARVI" }],
    industryGap: "γ=1 来自 Kaufman 与 Tanré 的常用取值，不是本传感器现场值。",
    checks: ["γ=0 时 ARVI 变成什么？"],
    summary: {
      definition: "ARVI = (近红外 − RB)/(近红外 + RB)，RB = 红光 − γ(蓝光 − 红光)，常用 γ=1。",
      value: "减轻气溶胶一类残差后的相对绿度；不能替代大气校正。",
      keyInput: "蓝、红、近红外反射率与 γ。",
      keyOutput: "单波段 arvi.tif。",
      keyLimit: "蓝光差时不稳定；γ 不是现场标定。",
    },
    background: [
      "Kaufman 与 Tanré 1992 年为 EOS-MODIS 提出 ARVI。",
      "它抵抗大气影响，但论文并不把它写成完整大气校正。",
    ],
    prerequisites: ["输入须为反射率。", "蓝光通道信噪须可接受。"],
    parameterNotes: [
      { name: "blue_band", role: "指定蓝光", guidance: "约 450–510 nm，避开噪声", effect: "进入 RB", risk: "蓝光差时 ARVI 比 NDVI 更不稳" },
      { name: "red_band", role: "指定红光", guidance: "约 630–690 nm", effect: "RB 的基准", risk: "误选红边会改变含义" },
      { name: "nir_band", role: "指定近红外", guidance: "约 760–900 nm", effect: "植被散射端", risk: "选错通道失去意义" },
      { name: "gamma", role: "气溶胶权重", guidance: "常用 1", effect: "γ 越大蓝光修正越强", risk: "改 γ 后不能横比" },
    ],
    resultInterpretation: [
      "相对 NDVI，薄霾时 ARVI 往往更稳；不是已经完成大气校正。",
      "比较须固定 γ。",
    ],
    applicable: ["有可靠蓝光的反射率、气溶胶残差可见时的对照。"],
    notApplicable: ["蓝光很差。", "要用大气校正产品请走 #13。"],
    risks: ["阴影和蓝光噪声会放大。", "γ 改了不能横比。"],
    upstream: ["反射率定标；需要时先做大气校正。"],
    downstream: ["相对绿度对照。"],
    demoFocus: ["γ=1 时 RB 与红光的差别方向。"],
  },
  {
    id: "50_vari",
    purpose: "只用可见光估相对覆盖，不需要近红外。",
    why: "有的相机没有近红外。绿减红、再拿蓝光进分母，用来估覆盖相关相对差异。",
    formula: "VARI = (GREEN − RED) / (GREEN + RED − BLUE)",
    formulaNote: "分母可能接近零或变号。不是覆盖度百分数。",
    formulaItems: [
      {
        name: "VARI 可见大气阻力指数",
        eq: "VARI = (GREEN − RED) / (GREEN + RED − BLUE)",
        note: "GREEN 绿、RED 红、BLUE 蓝。没有近红外。分母加 1e-12 只防除零。不是植被覆盖百分比。",
      },
    ],
    scenarioCases: [
      {
        title: "只有可见光三通道",
        body: "RGB 相机、没有近红外时，打开 vari.tif 看相对覆盖格局。不要拿它去替代 NDVI。",
      },
      {
        title: "分母可能接近零",
        body: "绿加红减蓝很小的地方，数值会炸。先看这些像元是不是阴影或异常色。",
      },
      {
        title: "不要读成覆盖度百分数",
        body: "土壤颜色、阴影都会干扰。要覆盖度百分数须本地标定。",
      },
    ],
    steps: ["取蓝、绿、红", "按公式计算", "写出 vari.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "VARI 只用可见光，轴上没有近红外。",
      bands: [
        { id: "blue", label: "蓝", nm: 480, color: VIS.b },
        { id: "green", label: "绿", nm: 560, color: VIS.g },
        { id: "red", label: "红", nm: 660, color: VIS.r },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率或辐射一致的可见光立方体" },
      { name: "blue_band / green_band / red_band", meaning: "默认 0 / 1 / 2" },
    ],
    outputs: [{ name: "vari.tif", meaning: "单波段 VARI，值域不必在 −1～1" }],
    industryGap: "JPEG 未经定标的照片不能声称物理 VARI。",
    checks: ["没有近红外时，VARI 能替代 NDVI 吗？"],
    summary: {
      definition: "VARI = (绿光 − 红光) / (绿光 + 红光 − 蓝光)。",
      value: "可见光相对覆盖示意；不是覆盖度百分数，也不能替代 NDVI。",
      keyInput: "蓝、绿、红反射率。",
      keyOutput: "单波段 vari.tif。",
      keyLimit: "分母可能接近零；土壤颜色和阴影会干扰。",
    },
    background: [
      "Gitelson 等 2002 年在可见光空间提出估植被覆盖分数的算法，其中包括 VARI。",
      "论文讨论的是覆盖分数估计，不是已经标定好的百分数产品。",
    ],
    prerequisites: ["三通道辐射尺度须一致。", "默认 0/1/2 仅适用于演示数据。"],
    parameterNotes: [
      { name: "blue_band", role: "指定蓝光", guidance: "可见光蓝通道", effect: "进入分母", risk: "蓝光偏了分母会偏" },
      { name: "green_band", role: "指定绿光", guidance: "绿反射峰", effect: "分子正端", risk: "误选红光会改变符号" },
      { name: "red_band", role: "指定红光", guidance: "红吸收区", effect: "分子负端", risk: "误选绿光会压对比" },
    ],
    resultInterpretation: [
      "较高值通常更绿、覆盖相对更高；不是百分数。",
      "极值先查分母。",
    ],
    applicable: ["只有可见光三通道、需要相对覆盖示意。"],
    notApplicable: ["有近红外却只用 VARI 替代 NDVI。", "未定标 JPEG 照片。"],
    risks: ["分母接近零。", "土壤颜色干扰。"],
    upstream: ["辐射一致的可见光通道。"],
    downstream: ["相对覆盖示意。"],
    demoFocus: ["同一像元绿升红降时 VARI 上升。"],
  },
  {
    id: "51_lai_index",
    purpose: "由 EVI 做一条经验线性式，得到经验叶面积指数。",
    why: "外部指数菜单常把 LAI 放进来。本页明确：这是经验式，不是 #33 PROSAIL。",
    formula: "LAI = max(3.618 × EVI − 0.118, 0)",
    formulaNote: "EVI 用 MODIS 习惯系数。3.618/−0.118 是本仓库演示数据默认，不是全球 LAI 产品。",
    formulaItems: [
      {
        name: "1. EVI",
        eq: "EVI = 2.5 × (NIR − RED) / (NIR + 6×RED − 7.5×BLUE + 1)",
        note: "与 #29 的 EVI 相同。系数沿用 MODIS 习惯。",
      },
      {
        name: "2. 经验叶面积",
        eq: "LAI = max(3.618 × EVI − 0.118, 0)",
        note: "线性系数是本仓库演示数据默认，未经本景标定。负值裁成 0，不表示真实零叶面积。产物是 lai_index.tif，不要和 #33 的 lai.tif 混。",
      },
    ],
    scenarioCases: [
      {
        title: "指数菜单里的 LAI，不是物理反演",
        body: "打开 lai_index.tif，把它当成 EVI 拉过一条直线后的示意。要机理反演请去 #33。",
      },
      {
        title: "系数不要当成全球真值",
        body: "3.618 和 −0.118 没有在本传感器、本作物上标定。换地方不能照搬。",
      },
      {
        title: "不要读成化验叶面积",
        body: "负值被裁成 0。全图均值不是地块叶面积。",
      },
    ],
    steps: ["取蓝、红、近红外", "算 EVI", "线性变换并裁负值", "写出 lai_index.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "经验 LAI 先走 EVI，所以也用蓝光。",
      bands: [
        { id: "blue", label: "蓝", nm: 480, color: VIS.b },
        { id: "red", label: "红", nm: 660, color: VIS.r },
        { id: "nir", label: "近红外", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体" },
      { name: "blue_band / red_band / nir_band", meaning: "默认 0 / 2 / 3" },
    ],
    outputs: [{ name: "lai_index.tif", meaning: "经验叶面积指数，不是 #33" }],
    industryGap: "线性系数未经本地标定；与 PROSAIL 不是同一条算法。",
    checks: ["lai_index.tif 和 #33 的 lai.tif 能当同一产品吗？"],
    summary: {
      definition: "经验 LAI = max(3.618×EVI − 0.118, 0)，EVI 为 MODIS 习惯式。",
      value: "经验叶面积示意；不是实验室叶面积，也不是 #33。",
      keyInput: "蓝、红、近红外反射率。",
      keyOutput: "单波段 lai_index.tif。",
      keyLimit: "系数是演示数据默认；负值裁零。",
    },
    background: [
      "Huete 等给出 MODIS EVI。植被指数与 LAI 在高叶面积时饱和（Carlson 与 Ripley 1997）。",
      "因此本仓库把线性系数标成演示数据默认，而不是全球产品。",
    ],
    prerequisites: ["输入须为反射率。", "不要把本页与 #33 混用。"],
    parameterNotes: [
      { name: "blue_band", role: "EVI 蓝光项", guidance: "蓝光有效波段", effect: "进入 EVI 分母", risk: "蓝光差时 EVI 不稳，经验 LAI 跟着偏" },
      { name: "red_band", role: "指定红光", guidance: "约 630–690 nm", effect: "EVI 红光项", risk: "误选红边会改变 EVI" },
      { name: "nir_band", role: "指定近红外", guidance: "约 760–900 nm", effect: "EVI 近红外项", risk: "选错通道失去意义" },
    ],
    resultInterpretation: [
      "数值是经验式输出，单位看起来像叶面积，但未经标定。",
      "零可能是裁切，不一定是裸土。",
    ],
    applicable: ["只要指数菜单里的经验 LAI 示意。"],
    notApplicable: ["要实验室叶面积。", "要 PROSAIL 请走 #33。"],
    risks: ["把演示数据系数当成全球真值。", "与 #33 文件名混淆。"],
    upstream: ["反射率定标。"],
    downstream: ["仅作示意，不要当地块叶面积验收。"],
    demoFocus: ["EVI 升高时经验 LAI 上升；负值被裁零。"],
  },
  {
    id: "52_nbr",
    purpose: "用近红外和短波红外的归一化差，看过火相关相对差异。",
    why: "过火后近红外往往下降、短波红外相对升高，NBR 会下降。形式接近 NDMI，用途不同。",
    formula: "NBR = (NIR − SWIR) / (NIR + SWIR)",
    formulaNote: "须有真 SWIR。演示数据默认约 1600 nm；Landsat NBR 常用 SWIR2 约 2.1 μm。",
    formulaItems: [
      {
        name: "NBR 标准化燃烧率",
        eq: "NBR = (NIR − SWIR) / (NIR + SWIR)",
        note: "与 NDMI 同型。演示立方体 SWIR 默认索引 5，约 1600 nm。Landsat 过火产品常用 SWIR2 约 2.08–2.35 μm。同一公式、不同窗口，不能混比。不是过火面积。",
      },
    ],
    scenarioCases: [
      {
        title: "过火前后同一套反射率",
        body: "有真 SWIR 时，打开 nbr.tif 看相对变干、变黑的格局。要过火面积还得再分类、再统计。",
      },
      {
        title: "不要和 NDMI 混成一句话",
        body: "公式可以一样，NDMI 讲冠层相对水分，NBR 讲过火。波段窗口还可能不同。",
      },
      {
        title: "演示数据 1600 nm 不是 Landsat SWIR2",
        body: "默认索引 5 只对应演示立方体。没有真 SWIR 不要用末波段冒充。",
      },
    ],
    steps: ["取近红外与短波红外", "归一化差", "写出 nbr.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "NBR 用近红外和短波红外。演示示意画在 1600 nm。",
      bands: [
        { id: "nir", label: "近红外 NIR", nm: 800, color: VIS.n },
        { id: "swir", label: "短波红外 SWIR", nm: 1600, color: VIS.s },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体（须有 SWIR）" },
      { name: "nir_band / swir_band", meaning: "默认 3 / 5" },
    ],
    outputs: [{ name: "nbr.tif", meaning: "单波段 NBR，不是过火面积" }],
    industryGap: "演示数据 SWIR 约 1600 nm，不是 Landsat SWIR2。",
    checks: ["NBR 和 NDMI 公式一样时，还能当同一个产品吗？"],
    summary: {
      definition: "NBR = (近红外 − 短波红外) / (近红外 + 短波红外)。",
      value: "过火相关相对差异；不是过火面积或损失金额。",
      keyInput: "近红外与真实短波红外。",
      keyOutput: "单波段 nbr.tif。",
      keyLimit: "SWIR 窗口不同不能混比；无 SWIR 无物理意义。",
    },
    background: [
      "Key 与 Benson 的 FIREMON 方法给出 NBR，并在 Landsat 上使用 SWIR2。",
      "差分 NBR 才常被用来谈过火严重度；本页只输出单期 NBR。",
    ],
    prerequisites: ["必须有真实 SWIR。", "默认 5 只对应演示立方体。"],
    parameterNotes: [
      { name: "nir_band", role: "指定近红外", guidance: "约 760–900 nm", effect: "过火后通常下降", risk: "选成红边会改变含义" },
      { name: "swir_band", role: "指定短波红外", guidance: "确认真实 SWIR；过火产品常要 ~2.1 μm", effect: "过火后相对升高使 NBR 下降", risk: "用末波段冒充则无物理意义" },
    ],
    resultInterpretation: [
      "较低值可能更干、更黑或过火更重，须结合前后时相，不能单期定级。",
      "演示数据 1600 nm 不能写成 Landsat SWIR2 产品。",
    ],
    applicable: ["有真 SWIR 的过火相对对照。"],
    notApplicable: ["无 SWIR。", "要过火面积或金额。"],
    risks: ["与 NDMI 混读。", "窗口不同却横比。"],
    upstream: ["反射率与 SWIR 波长核验。"],
    downstream: ["过火相对分区；面积须另做。"],
    demoFocus: ["SWIR 升高、近红外下降时 NBR 下降。"],
  },
  {
    id: "53_sipi",
    purpose: "用近红外减蓝光，除以近红外减红光，看色素比值相关相对差异。",
    why: "蓝光和红光都被色素吸收，近红外几乎不被色素吸收。相除后对冠层结构相对不那么敏感。",
    formula: "SIPI = (NIR − BLUE) / (NIR − RED)",
    formulaNote: "NIR 接近 RED 时分母接近零。值域不必在 −1～1。",
    formulaItems: [
      {
        name: "SIPI 结构不敏感色素指数",
        eq: "SIPI = (NIR − BLUE) / (NIR − RED)",
        note: "NIR、BLUE、RED 须为反射率。不是类胡萝卜素或叶绿素毫克数。分母加 1e-12 只防除零。",
      },
    ],
    scenarioCases: [
      {
        title: "想看色素比值相关相对差异",
        body: "有蓝、红、近红外反射率时，打开 sipi.tif。这是比值，不一定落在 −1 到 1。",
      },
      {
        title: "近红外和红光几乎一样时会炸",
        body: "稀疏、土壤、阴影处 NIR≈RED，分母接近零。先别解释那些格子。",
      },
      {
        title: "不要读成色素毫克数",
        body: "论文是叶片半经验关系。冠层图不能直接当化验值。",
      },
    ],
    steps: ["取蓝、红、近红外", "按公式计算", "写出 sipi.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "SIPI 用蓝光、红光和近红外。",
      bands: [
        { id: "blue", label: "蓝", nm: 480, color: VIS.b },
        { id: "red", label: "红", nm: 660, color: VIS.r },
        { id: "nir", label: "近红外", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体" },
      { name: "blue_band / red_band / nir_band", meaning: "默认 0 / 2 / 3" },
    ],
    outputs: [{ name: "sipi.tif", meaning: "单波段 SIPI，值域不必在 −1～1" }],
    industryGap: "叶片尺度关系不能直接写成冠层含量。",
    checks: ["NIR 等于 RED 时 SIPI 会怎样？"],
    summary: {
      definition: "SIPI = (近红外 − 蓝光) / (近红外 − 红光)。",
      value: "色素比值相关相对差异；不是色素含量。",
      keyInput: "蓝、红、近红外反射率。",
      keyOutput: "单波段 sipi.tif。",
      keyLimit: "分母接近零时数值不稳定。",
    },
    background: [
      "Peñuelas、Baret、Filella 1995 年给出半经验色素指数，其中包括 SIPI 这类 (R800−R445)/(R800−R680)。",
      "结构不敏感是相对说法，不是完全不受结构影响。",
    ],
    prerequisites: ["输入须为反射率。", "注意 NIR−RED 接近零的像元。"],
    parameterNotes: [
      { name: "blue_band", role: "指定蓝光", guidance: "约 445–480 nm", effect: "色素吸收端之一", risk: "蓝光噪声进入分子" },
      { name: "red_band", role: "指定红光", guidance: "约 680 nm 附近", effect: "分母", risk: "与近红外过近则分母接近零" },
      { name: "nir_band", role: "指定近红外", guidance: "约 800 nm", effect: "几乎无色素吸收的参照", risk: "选成红边会改变含义" },
    ],
    resultInterpretation: [
      "数值变化反映色素比值相关相对差异，不是毫克数。",
      "极值先查分母。",
    ],
    applicable: ["有蓝、红、近红外的色素相对对照。"],
    notApplicable: ["要色素化验值。", "NIR 与红光几乎相同的稀疏像元。"],
    risks: ["分母接近零。", "把叶片关系外推到冠层含量。"],
    upstream: ["反射率定标与掩膜。"],
    downstream: ["色素相对分区。"],
    demoFocus: ["红光接近近红外时数值发炸。"],
  },
  {
    id: "54_gci",
    purpose: "用近红外除以绿光再减 1，看叶绿素相关相对差异。",
    why: "和 RECI 同型，只是分母换成绿光。有绿光和近红外就能算，不要求红边。",
    formula: "GCI = NIR / GREEN − 1",
    formulaNote: "须为反射率。值域不是 −1～1。",
    formulaItems: [
      {
        name: "GCI 绿色叶绿素指数",
        eq: "GCI = NIR / GREEN − 1",
        note: "NIR 近红外、GREEN 绿光。与 RECI 同型，分母是绿光不是红边。不能读成叶绿素毫克数。",
      },
    ],
    scenarioCases: [
      {
        title: "有绿光和近红外，想看叶绿素相关相对差异",
        body: "打开 gci.tif。这是比值减 1，不是 −1 到 1。没有红边时不要拿它冒充 RECI。",
      },
      {
        title: "绿光接近零会很大",
        body: "阴影、水体绿光很低时数值会炸。先掩膜再看统计。",
      },
      {
        title: "不要读成叶绿素毫克数",
        body: "Gitelson 等给出的是相关关系，须本地标定才能谈含量。",
      },
    ],
    steps: ["取绿光与近红外", "近红外除以绿光再减 1", "写出 gci.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "GCI 用绿光当除数，近红外当分子。",
      bands: [
        { id: "green", label: "绿 GREEN", nm: 560, color: VIS.g },
        { id: "nir", label: "近红外 NIR", nm: 800, color: VIS.n },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体" },
      { name: "green_band / nir_band", meaning: "默认 1 / 3" },
    ],
    outputs: [{ name: "gci.tif", meaning: "单波段比值指数，不是 −1～1" }],
    industryGap: "绿光窗口因传感器而异。",
    checks: ["GCI 和 RECI 差在哪个波段？"],
    summary: {
      definition: "GCI = 近红外反射率 / 绿光反射率 − 1。",
      value: "叶绿素相关相对分区；不能直接当作叶绿素含量。",
      keyInput: "绿光与近红外反射率。",
      keyOutput: "单波段 gci.tif。",
      keyLimit: "值域不是 −1～1；绿光接近零时不稳定。",
    },
    background: [
      "Gitelson 等把 NIR/GREEN − 1 称作绿色叶绿素指数。",
      "与红边版同型，波段不同就不能混成一个产品。",
    ],
    prerequisites: ["输入须为反射率。", "默认 1/3 仅适用于演示数据。"],
    parameterNotes: [
      { name: "green_band", role: "指定绿光", guidance: "绿反射峰", effect: "除数", risk: "绿光接近零时比值很大" },
      { name: "nir_band", role: "指定近红外", guidance: "近红外平台", effect: "分子", risk: "选成红边会改变含义" },
    ],
    resultInterpretation: [
      "较高值通常叶绿素相关响应更强；不是毫克数。",
      "与 RECI 不要套同一阈值。",
    ],
    applicable: ["有绿光与近红外、没有红边时的叶绿素相关示意。"],
    notApplicable: ["要叶绿素化验值。", "把 GCI 冒充 RECI。"],
    risks: ["绿光接近零。", "与 RECI 混比。"],
    upstream: ["反射率定标与掩膜。"],
    downstream: ["叶绿素相关相对分区。"],
    demoFocus: ["绿光降低时 GCI 上升。"],
  },
  {
    id: "55_ndsi",
    purpose: "用绿光和短波红外的归一化差，看积雪相关相对差异。",
    why: "雪在绿光亮、在短波红外暗。水和雪都能让短波红外变暗，所以和 MNDWI 同型，用途必须写清。",
    formula: "NDSI = (GREEN − SWIR) / (GREEN + SWIR)",
    formulaNote: "须有真 SWIR。与 MNDWI 同型，本页用途是雪不是水。不输出二值雪图。",
    formulaItems: [
      {
        name: "NDSI 归一化差值雪指数",
        eq: "NDSI = (GREEN − SWIR) / (GREEN + SWIR)",
        note: "与 #30 的 MNDWI 公式同型。本页用途是雪。不要拿水体阈值来切。没有真 SWIR 不要算。不是积雪面积。",
      },
    ],
    scenarioCases: [
      {
        title: "有真 SWIR，想看哪里更像雪",
        body: "打开 ndsi.tif 看相对积雪格局。云、冰、盐壳可能也亮，不要一刀切成积雪面积。",
      },
      {
        title: "不要和 MNDWI 混成一句话",
        body: "公式可以一样。MNDWI 圈水，NDSI 看雪。阈值和后续规则都不同。",
      },
      {
        title: "本页不输出雪/非雪二值图",
        body: "MODIS 积雪产品还有额外规则。这里只给指数本身。",
      },
    ],
    steps: ["取绿光与短波红外", "归一化差", "写出 ndsi.tif"],
    viz: {
      kind: "index_spectrum",
      caption: "NDSI 用绿光和短波红外，和 MNDWI 画在同一对波段上。",
      bands: [
        { id: "green", label: "绿 GREEN", nm: 560, color: VIS.g },
        { id: "swir", label: "短波红外 SWIR", nm: 1600, color: VIS.s },
      ],
    },
    inputs: [
      { name: "file", meaning: "反射率立方体（须有 SWIR）" },
      { name: "green_band / swir_band", meaning: "默认 1 / 5" },
    ],
    outputs: [{ name: "ndsi.tif", meaning: "单波段 NDSI，不是积雪面积" }],
    industryGap: "无二值化与云检测规则，不能当 MODIS 积雪产品。",
    checks: ["NDSI 和 MNDWI 公式一样，为什么不能当水图？"],
    summary: {
      definition: "NDSI = (绿光 − 短波红外) / (绿光 + 短波红外)。",
      value: "积雪相对格局；不是积雪面积，也不是 MNDWI 水体图。",
      keyInput: "绿光与真实短波红外。",
      keyOutput: "单波段 ndsi.tif。",
      keyLimit: "与 MNDWI 同型；云冰盐壳会混淆；无 SWIR 无物理意义。",
    },
    background: [
      "Hall、Riggs、Salomonson 1995 年用 NDSI 辅助 MODIS 全球积雪制图。",
      "业务积雪产品还有阈值和云检测，本仓库只实现指数本身。",
    ],
    prerequisites: ["必须有真实 SWIR。", "默认 1/5 仅适用于演示数据。"],
    parameterNotes: [
      { name: "green_band", role: "指定绿光", guidance: "绿光反射峰", effect: "雪在绿光通常较亮", risk: "误选红光会改变含义" },
      { name: "swir_band", role: "指定短波红外", guidance: "真实 SWIR", effect: "雪在 SWIR 通常很暗", risk: "用近红外冒充则无物理意义" },
    ],
    resultInterpretation: [
      "较高值更像雪或冰，须目视排除云和盐壳。",
      "不要用 MNDWI 的水体阈值。",
    ],
    applicable: ["有真 SWIR 的积雪相对对照。"],
    notApplicable: ["无 SWIR。", "要水体请走 #30 MNDWI。", "要积雪面积产品。"],
    risks: ["与 MNDWI 混读。", "把指数图当成面积。"],
    upstream: ["反射率与 SWIR 波长核验。"],
    downstream: ["积雪相对分区；面积须另做。"],
    demoFocus: ["绿光高、SWIR 低时 NDSI 升高。"],
  },
];
