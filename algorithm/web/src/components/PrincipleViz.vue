<template>
  <!-- 按算法类型切换示意：能交互的优先做成可拖滑块 -->
  <div class="pv">
    <p class="pv-cap">{{ viz.caption }}</p>

    <!-- 指数：可调长势的光谱 + 实时公式 -->
    <div v-if="viz.kind === 'index_spectrum'" class="pv-body">
      <svg viewBox="0 0 520 220" class="pv-svg" aria-label="植被光谱示意">
        <line x1="40" y1="190" x2="500" y2="190" stroke="var(--line-strong)" />
        <line x1="40" y1="20" x2="40" y2="190" stroke="var(--line-strong)" />
        <text x="8" y="24" class="ax">ρ</text>
        <text x="470" y="208" class="ax">波长</text>
        <polyline :points="specPoints" fill="none" stroke="var(--forest)" stroke-width="2.4" />
        <g v-for="b in viz.bands || []" :key="b.id">
          <line :x1="nmX(b.nm)" y1="24" :x2="nmX(b.nm)" y2="190" :stroke="b.color" stroke-dasharray="3 3" />
          <circle :cx="nmX(b.nm)" :cy="nmY(sampleAt(b.nm))" r="5" :fill="b.color" />
          <text :x="nmX(b.nm)" y="18" text-anchor="middle" class="blab" :fill="b.color">{{ b.label }}</text>
        </g>
      </svg>
      <label class="pv-slider">
        长势 / 覆盖
        <input type="range" min="0" max="100" v-model.number="vigor" />
        <strong>{{ indexLive.label }} = {{ indexLive.value }}</strong>
      </label>
    </div>

    <!-- 红边四点 -->
    <div v-else-if="viz.kind === 'red_edge'" class="pv-body">
      <svg viewBox="0 0 520 220" class="pv-svg" aria-label="Guyot 红边位置">
        <line x1="40" y1="190" x2="500" y2="190" stroke="var(--line-strong)" />
        <polyline :points="redEdgePoly" fill="none" stroke="var(--forest)" stroke-width="2.4" />
        <g v-for="p in redEdgePts" :key="p.nm">
          <circle :cx="p.x" :cy="p.y" r="5" fill="var(--viz-warm)" />
          <text :x="p.x" :y="p.y - 10" text-anchor="middle" class="blab">{{ p.nm }}</text>
        </g>
        <line :x1="repX" y1="30" :x2="repX" y2="190" stroke="var(--warn)" stroke-dasharray="4 3" />
        <text :x="repX" y="24" text-anchor="middle" class="blab" fill="var(--warn)">REP ≈ {{ repNm.toFixed(0) }} nm</text>
      </svg>
      <label class="pv-slider">
        叶绿素（红边右移）
        <input type="range" min="0" max="100" v-model.number="chlorophyll" />
      </label>
    </div>

    <!-- SAM 夹角 -->
    <div v-else-if="viz.kind === 'sam'" class="pv-body">
      <svg viewBox="0 0 420 240" class="pv-svg" aria-label="光谱角">
        <line x1="40" y1="210" x2="390" y2="210" stroke="var(--line-strong)" />
        <line x1="40" y1="20" x2="40" y2="210" stroke="var(--line-strong)" />
        <line x1="40" y1="210" :x2="endX" :y2="endY" stroke="var(--forest-2)" stroke-width="3" />
        <line x1="40" y1="210" :x2="pixX" :y2="pixY" stroke="var(--viz-warm)" stroke-width="3" />
        <text :x="endX + 6" :y="endY" class="blab">端元 e</text>
        <text :x="pixX + 6" :y="pixY" class="blab">像元 x</text>
        <path :d="arcD" fill="none" stroke="var(--warn)" stroke-width="2" />
        <text x="150" y="150" class="blab">θ = {{ samDeg.toFixed(1) }}°</text>
      </svg>
      <label class="pv-slider">
        光谱夹角
        <input type="range" min="2" max="80" v-model.number="samDeg" />
        <span>{{ samDeg < 12 ? "很像该端元" : samDeg < 25 ? "比较像" : "不太像" }}</span>
      </label>
    </div>

    <!-- 解混 -->
    <div v-else-if="viz.kind === 'unmix'" class="pv-body">
      <svg viewBox="0 0 520 200" class="pv-svg" aria-label="线性混合">
        <polyline :points="mixCrop" fill="none" stroke="var(--forest-2)" stroke-width="2" />
        <polyline :points="mixSoil" fill="none" stroke="var(--viz-warm)" stroke-width="2" />
        <polyline :points="mixPix" fill="none" stroke="var(--warn)" stroke-width="3" />
        <text x="400" y="40" class="blab" fill="var(--forest-2)">作物端元</text>
        <text x="400" y="58" class="blab" fill="var(--viz-warm)">土壤端元</text>
        <text x="400" y="76" class="blab" fill="var(--warn)">混合像元</text>
      </svg>
      <label class="pv-slider">
        作物丰度 a₁
        <input type="range" min="0" max="100" v-model.number="abundance" />
        <strong>作物 {{ (abundance / 100).toFixed(2) }} · 土壤 {{ (1 - abundance / 100).toFixed(2) }}</strong>
      </label>
    </div>

    <!-- RX -->
    <div v-else-if="viz.kind === 'rx'" class="pv-body">
      <svg viewBox="0 0 420 240" class="pv-svg" aria-label="马氏距离椭圆">
        <ellipse cx="200" cy="120" rx="110" ry="55" fill="rgba(26, 124, 117, 0.12)" stroke="var(--forest-2)" />
        <circle v-for="(p, i) in rxBg" :key="i" :cx="p.x" :cy="p.y" r="3.2" fill="var(--forest-2)" opacity="0.55" />
        <circle :cx="rxOut.x" :cy="rxOut.y" r="7" fill="var(--warn)" />
        <text :x="rxOut.x + 10" :y="rxOut.y" class="blab">异常点</text>
        <text x="24" y="28" class="ax">波段 2</text>
        <text x="330" y="228" class="ax">波段 1</text>
      </svg>
      <label class="pv-slider">
        异常偏离
        <input type="range" min="0" max="100" v-model.number="rxShift" />
        <span>{{ rxShift > 55 ? "落在椭圆外 → 判为异常" : "仍在背景云内" }}</span>
      </label>
    </div>

    <!-- ACE -->
    <div v-else-if="viz.kind === 'ace'" class="pv-body">
      <svg viewBox="0 0 420 230" class="pv-svg">
        <ellipse cx="190" cy="130" rx="95" ry="48" fill="rgba(26, 124, 117, 0.12)" stroke="var(--forest-2)" />
        <line x1="190" y1="130" x2="340" y2="48" stroke="var(--warn)" stroke-width="2" marker-end="url(#arr)" />
        <circle cx="190" cy="130" r="5" fill="var(--forest-2)" />
        <circle cx="340" cy="48" r="6" fill="var(--warn)" />
        <text x="24" y="40" class="blab">背景 μ, Σ</text>
        <text x="300" y="38" class="blab">目标方向 d</text>
        <defs>
          <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8" fill="var(--warn)" />
          </marker>
        </defs>
      </svg>
      <p class="pv-note">ACE 看的是：去掉背景相关之后，像元在目标方向上还剩多少能量。</p>
    </div>

    <!-- 少样本 -->
    <div v-else-if="viz.kind === 'fewshot'" class="pv-body">
      <svg viewBox="0 0 480 220" class="pv-svg">
        <circle cx="120" cy="80" r="8" fill="var(--forest-2)" />
        <circle cx="95" cy="120" r="8" fill="var(--forest-2)" />
        <circle cx="145" cy="125" r="8" fill="var(--forest-2)" />
        <circle cx="120" cy="108" r="11" fill="none" stroke="var(--forest-2)" stroke-width="2" />
        <text x="70" y="50" class="blab">类 A 原型</text>
        <circle cx="320" cy="70" r="8" fill="var(--viz-warm)" />
        <circle cx="350" cy="110" r="8" fill="var(--viz-warm)" />
        <circle cx="300" cy="115" r="8" fill="var(--viz-warm)" />
        <circle cx="324" cy="98" r="11" fill="none" stroke="var(--viz-warm)" stroke-width="2" />
        <text x="280" y="48" class="blab">类 B 原型</text>
        <circle :cx="queryX" cy="170" r="7" fill="var(--warn)" />
        <text :x="queryX + 10" y="174" class="blab">查询像元</text>
        <line :x1="queryX" y1="170" x2="120" y2="108" stroke="var(--forest-2)" stroke-dasharray="4 3" />
        <line :x1="queryX" y1="170" x2="324" y2="98" stroke="var(--viz-warm)" stroke-dasharray="4 3" />
      </svg>
      <label class="pv-slider">
        查询像元位置
        <input type="range" min="80" max="360" v-model.number="queryX" />
        <span>归为 {{ queryX < 220 ? "A" : "B" }}（距离更近的原型）</span>
      </label>
    </div>

    <!-- 网络结构 -->
    <div v-else-if="viz.kind === 'cnn_arch'" class="pv-flow">
      <div v-for="(ly, i) in viz.layers || []" :key="ly.name" class="pv-chip">
        <em>{{ i + 1 }}</em>
        <strong>{{ ly.name }}</strong>
        <span>{{ ly.note }}</span>
      </div>
    </div>

    <!-- 流水线 -->
    <div v-else-if="viz.kind === 'pipeline'" class="pv-flow">
      <div v-for="(s, i) in viz.steps || []" :key="s" class="pv-chip">
        <em>{{ i + 1 }}</em>
        <strong>{{ s }}</strong>
      </div>
    </div>

    <!-- 往返航线 -->
    <div v-else-if="viz.kind === 'lawnmower'" class="pv-body">
      <svg viewBox="0 0 460 200" class="pv-svg">
        <rect x="40" y="30" width="380" height="140" fill="none" stroke="var(--line-strong)" />
        <polyline points="50,50 400,50 400,90 50,90 50,130 400,130 400,160 50,160" fill="none" stroke="var(--forest-2)" stroke-width="2.5" />
        <circle v-for="(p, i) in lawnPts" :key="i" :cx="p.x" :cy="p.y" r="4" fill="var(--viz-warm)" />
        <text x="48" y="24" class="ax">测区</text>
      </svg>
    </div>

    <!-- SG 平滑 -->
    <div v-else-if="viz.kind === 'spectrum_smooth'" class="pv-body">
      <svg viewBox="0 0 520 200" class="pv-svg">
        <polyline :points="noisySpec" fill="none" stroke="var(--line-strong)" stroke-width="1.5" />
        <polyline :points="smoothSpec" fill="none" stroke="var(--forest)" stroke-width="2.4" />
        <text x="360" y="36" class="blab" fill="var(--line-strong)">含噪</text>
        <text x="360" y="54" class="blab" fill="var(--forest)">SG 平滑</text>
      </svg>
    </div>

    <!-- 回归 -->
    <div v-else-if="viz.kind === 'regression'" class="pv-body">
      <svg viewBox="0 0 420 220" class="pv-svg">
        <line x1="40" y1="190" x2="390" y2="190" stroke="var(--line-strong)" />
        <line x1="40" y1="20" x2="40" y2="190" stroke="var(--line-strong)" />
        <circle v-for="(p, i) in regPts" :key="i" :cx="p.x" :cy="p.y" r="4" fill="var(--forest-2)" opacity="0.7" />
        <line x1="50" y1="175" x2="370" y2="40" stroke="var(--viz-warm)" stroke-width="2" />
        <text x="300" y="36" class="ax">生化量 Y</text>
        <text x="300" y="210" class="ax">光谱特征 X</text>
      </svg>
      <p class="pv-note">PLS 在「近直线」时稳；关系弯了就要更多成分或非线性模型。</p>
    </div>

    <!-- LUT -->
    <div v-else-if="viz.kind === 'lut'" class="pv-body">
      <svg viewBox="0 0 520 200" class="pv-svg">
        <polyline v-for="(p, i) in lutLines" :key="i" :points="p" fill="none" :stroke="i === lutHit ? 'var(--warn)' : 'var(--line-strong)'" :stroke-width="i === lutHit ? 2.6 : 1.2" />
        <polyline :points="lutQuery" fill="none" stroke="var(--forest)" stroke-width="2.4" stroke-dasharray="5 3" />
        <text x="360" y="30" class="blab">虚线 = 像元 · 红 = 最近 LUT</text>
      </svg>
    </div>

    <!-- 特征空间 -->
    <div v-else-if="viz.kind === 'feature_space'" class="pv-body">
      <svg viewBox="0 0 420 220" class="pv-svg">
        <line x1="40" y1="190" x2="390" y2="40" stroke="var(--viz-warm)" stroke-width="2" />
        <circle v-for="(p, i) in fsA" :key="'a' + i" :cx="p.x" :cy="p.y" r="5" fill="var(--forest-2)" />
        <circle v-for="(p, i) in fsB" :key="'b' + i" :cx="p.x" :cy="p.y" r="5" fill="var(--warn)" />
        <text x="50" y="36" class="blab" fill="var(--forest-2)">类 A</text>
        <text x="320" y="36" class="blab" fill="var(--warn)">类 B</text>
        <text x="250" y="210" class="ax">SVM 最大间隔示意</text>
      </svg>
    </div>

    <!-- 变化 -->
    <div v-else-if="viz.kind === 'change'" class="pv-body">
      <svg viewBox="0 0 420 220" class="pv-svg">
        <line x1="50" y1="180" x2="360" y2="40" stroke="var(--line-strong)" stroke-dasharray="4 3" />
        <circle v-for="(p, i) in chStable" :key="'s' + i" :cx="p.x" :cy="p.y" r="4" fill="var(--forest-2)" opacity="0.7" />
        <circle v-for="(p, i) in chChange" :key="'c' + i" :cx="p.x" :cy="p.y" r="6" fill="var(--warn)" />
        <text x="40" y="24" class="ax">T2</text>
        <text x="340" y="210" class="ax">T1</text>
        <text x="250" y="70" class="blab" fill="var(--warn)">变化点偏离 1:1</text>
      </svg>
    </div>

    <!-- 众数/超像素 -->
    <div v-else-if="viz.kind === 'majority'" class="pv-body">
      <svg viewBox="0 0 440 180" class="pv-svg">
        <g v-for="c in 8" :key="'r' + c">
          <rect v-for="r in 4" :key="c + '-' + r" :x="24 + (c - 1) * 28" :y="28 + (r - 1) * 28" width="24" height="24" :fill="majFill(c, r, false)" stroke="var(--paper)" />
        </g>
        <g v-for="c in 8" :key="'r2' + c">
          <rect v-for="r in 4" :key="'b' + c + r" :x="248 + (c - 1) * 28" :y="28 + (r - 1) * 28" width="24" height="24" :fill="majFill(c, r, true)" stroke="var(--paper)" />
        </g>
        <text x="24" y="20" class="ax">处理前</text>
        <text x="248" y="20" class="ax">处理后</text>
      </svg>
    </div>

    <!-- 地块 -->
    <div v-else-if="viz.kind === 'zonal'" class="pv-body">
      <svg viewBox="0 0 460 200" class="pv-svg">
        <rect x="30" y="20" width="240" height="160" fill="#d4ece8" />
        <polygon points="50,40 150,36 168,120 70,150" fill="rgba(224, 138, 44, 0.35)" stroke="var(--viz-warm)" />
        <polygon points="170,50 250,44 248,160 160,140" fill="rgba(26, 124, 117, 0.28)" stroke="var(--forest-2)" />
        <text x="80" y="90" class="blab">田块 A 均值</text>
        <text x="185" y="100" class="blab">田块 B 均值</text>
        <rect x="300" y="40" width="140" height="50" fill="var(--paper-3)" stroke="var(--line)" />
        <text x="312" y="62" class="blab">A · NDVI 0.72</text>
        <text x="312" y="80" class="blab">B · NDVI 0.41</text>
      </svg>
    </div>

    <!-- PCA -->
    <div v-else-if="viz.kind === 'pca'" class="pv-body">
      <svg viewBox="0 0 420 210" class="pv-svg">
        <ellipse cx="200" cy="110" rx="130" ry="36" transform="rotate(-28 200 110)" fill="rgba(26, 124, 117, 0.12)" stroke="var(--forest-2)" />
        <line x1="80" y1="165" x2="320" y2="55" stroke="var(--viz-warm)" stroke-width="2" />
        <text x="300" y="48" class="blab">PC1</text>
      </svg>
    </div>

    <!-- 大气 -->
    <div v-else-if="viz.kind === 'atmosphere'" class="pv-body">
      <svg viewBox="0 0 460 190" class="pv-svg">
        <path d="M20,80 Q120,40 220,80 T420,80" fill="none" stroke="#8fb4d9" stroke-width="18" opacity="0.45" />
        <line x1="80" y1="20" x2="200" y2="150" stroke="var(--viz-warm)" stroke-width="2" />
        <line x1="140" y1="70" x2="200" y2="150" stroke="#5b8def" stroke-width="2" />
        <rect x="160" y="150" width="80" height="18" fill="var(--forest-2)" />
        <text x="30" y="36" class="blab">太阳</text>
        <text x="230" y="70" class="blab">路径辐射（要减）</text>
        <text x="250" y="164" class="blab">地表</text>
      </svg>
    </div>

    <!-- BRDF -->
    <div v-else-if="viz.kind === 'brdf'" class="pv-body">
      <svg viewBox="0 0 420 180" class="pv-svg">
        <ellipse cx="210" cy="140" rx="140" ry="18" fill="#d4ece8" />
        <line x1="210" y1="40" x2="210" y2="140" stroke="var(--forest-2)" stroke-width="2" />
        <line x1="210" y1="140" x2="330" y2="60" stroke="var(--viz-warm)" stroke-width="2" />
        <text x="180" y="32" class="blab">天底</text>
        <text x="300" y="52" class="blab">大观测角</text>
      </svg>
    </div>

    <!-- 正射 -->
    <div v-else-if="viz.kind === 'ortho'" class="pv-body">
      <svg viewBox="0 0 440 180" class="pv-svg">
        <path d="M30,140 L140,80 L260,130 L420,70 L420,170 L30,170 Z" fill="#d4ece8" stroke="var(--forest-2)" />
        <line x1="220" y1="20" x2="160" y2="100" stroke="var(--warn)" stroke-dasharray="4 3" />
        <line x1="220" y1="20" x2="220" y2="120" stroke="var(--forest-2)" />
        <circle cx="220" cy="20" r="6" fill="var(--viz-warm)" />
        <text x="230" y="24" class="blab">相机</text>
        <text x="30" y="40" class="blab">虚线 = 斜视 · 实线 = 正射</text>
      </svg>
    </div>

    <!-- 镶嵌 -->
    <div v-else-if="viz.kind === 'mosaic'" class="pv-body">
      <svg viewBox="0 0 440 160" class="pv-svg">
        <rect x="40" y="30" width="180" height="100" fill="rgba(26, 124, 117, 0.25)" />
        <rect x="160" y="30" width="180" height="100" fill="rgba(224, 138, 44, 0.28)" />
        <rect x="160" y="30" width="60" height="100" fill="url(#feather)" />
        <defs>
          <linearGradient id="feather" x1="0" x2="1">
            <stop offset="0" stop-color="var(--forest-2)" stop-opacity="0.35" />
            <stop offset="1" stop-color="var(--viz-warm)" stop-opacity="0.35" />
          </linearGradient>
        </defs>
        <text x="60" y="24" class="ax">航带 1</text>
        <text x="280" y="24" class="ax">航带 2</text>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { PrincipleViz } from "../principles/types";

const props = defineProps<{ viz: PrincipleViz }>();

const vigor = ref(70);
const chlorophyll = ref(45);
const samDeg = ref(18);
const abundance = ref(65);
const rxShift = ref(70);
const queryX = ref(200);

function vegRho(nm: number, v: number): number {
  const t = v / 100;
  if (nm < 500) return 0.04 + 0.02 * t;
  if (nm < 600) return 0.06 + 0.08 * t;
  if (nm < 690) return 0.08 - 0.05 * t;
  if (nm < 760) return 0.08 + (0.45 * t * (nm - 690)) / 70;
  return 0.18 + 0.37 * t;
}

function nmX(nm: number): number {
  const lo = 400;
  const hi = 1700;
  return 40 + ((Math.min(hi, Math.max(lo, nm)) - lo) / (hi - lo)) * 460;
}
function nmY(rho: number): number {
  return 190 - rho * 280;
}

const specPoints = computed(() => {
  const pts: string[] = [];
  for (let nm = 430; nm <= 1650; nm += 8) {
    pts.push(`${nmX(nm)},${nmY(vegRho(nm, vigor.value))}`);
  }
  return pts.join(" ");
});

function sampleAt(nm: number): number {
  return vegRho(nm, vigor.value);
}

const indexLive = computed(() => {
  const bands = props.viz.bands || [];
  const get = (id: string, fallback: number) => {
    const hit = bands.find((b) => b.id === id);
    return vegRho(hit?.nm ?? fallback, vigor.value);
  };
  const ids = new Set(bands.map((b) => b.id));
  if (ids.has("re") && ids.has("nir")) {
    const re = get("re", 720);
    const n = get("nir", 800);
    return { label: "NDRE", value: ((n - re) / (n + re + 1e-6)).toFixed(3) };
  }
  if (ids.has("blue") && ids.has("red") && ids.has("nir") && !ids.has("swir")) {
    const b = get("blue", 480);
    const r = get("red", 660);
    const n = get("nir", 800);
    return { label: "EVI", value: (2.5 * (n - r) / (n + 6 * r - 7.5 * b + 1)).toFixed(3) };
  }
  if (ids.has("swir") && ids.has("green")) {
    const g = get("green", 560);
    const n = get("nir", 800);
    const s = get("swir", 1600);
    const ndwi = (g - n) / (g + n + 1e-6);
    return { label: "NDWI", value: ndwi.toFixed(3) };
  }
  if (ids.has("red") && ids.has("nir")) {
    const r = get("red", 660);
    const n = get("nir", 800);
    return { label: "NDVI", value: ((n - r) / (n + r + 1e-6)).toFixed(3) };
  }
  return { label: "示意", value: (vigor.value / 100).toFixed(2) };
});

function reX(nm: number) {
  return 40 + ((nm - 650) / 160) * 460;
}
function reY(rho: number) {
  return 190 - rho * 260;
}

const redEdgePts = computed(() => {
  const shift = chlorophyll.value / 400;
  const r670 = 0.08 - shift;
  const r700 = 0.12 + shift * 0.4;
  const r740 = 0.35 + shift;
  const r780 = 0.48 + shift * 0.6;
  return [
    { nm: 670, x: reX(670), y: reY(r670), rho: r670 },
    { nm: 700, x: reX(700), y: reY(r700), rho: r700 },
    { nm: 740, x: reX(740), y: reY(r740), rho: r740 },
    { nm: 780, x: reX(780), y: reY(r780), rho: r780 },
  ];
});

const redEdgePoly = computed(() => {
  const pts: string[] = [];
  for (let nm = 650; nm <= 810; nm += 4) {
    const t = chlorophyll.value / 100;
    const rho = 0.07 + 0.42 / (1 + Math.exp(-(nm - (710 + t * 18)) / 8));
    pts.push(`${reX(nm)},${reY(rho)}`);
  }
  return pts.join(" ");
});

const repNm = computed(() => 710 + (chlorophyll.value / 100) * 18);
const repX = computed(() => reX(repNm.value));

const samRad = computed(() => (samDeg.value * Math.PI) / 180);
const endX = 40 + 260;
const endY = 210 - 150;
const pixX = computed(() => 40 + 260 * Math.cos(samRad.value));
const pixY = computed(() => 210 - 260 * Math.sin(Math.PI / 2 - samRad.value) * 0.55 - 40);
const arcD = computed(() => `M 120,180 A 40,40 0 0 0 90,155`);

function wavePts(amp: number, phase: number, offset: number): string {
  const pts: string[] = [];
  for (let i = 0; i <= 40; i++) {
    const x = 40 + i * 8;
    const y = 120 - (offset + amp * Math.sin(i / 4 + phase)) * 40;
    pts.push(`${x},${y}`);
  }
  return pts.join(" ");
}
const mixCrop = computed(() => wavePts(0.9, 0, 0.9));
const mixSoil = computed(() => wavePts(0.25, 1.2, 0.35));
const mixPix = computed(() => {
  const a = abundance.value / 100;
  const pts: string[] = [];
  for (let i = 0; i <= 40; i++) {
    const x = 40 + i * 8;
    const c = 120 - (0.9 + 0.9 * Math.sin(i / 4)) * 40;
    const s = 120 - (0.35 + 0.25 * Math.sin(i / 4 + 1.2)) * 40;
    pts.push(`${x},${a * c + (1 - a) * s}`);
  }
  return pts.join(" ");
});

const rxBg = [
  { x: 160, y: 110 },
  { x: 210, y: 125 },
  { x: 190, y: 100 },
  { x: 230, y: 118 },
  { x: 175, y: 135 },
  { x: 205, y: 108 },
  { x: 150, y: 122 },
  { x: 240, y: 132 },
];
const rxOut = computed(() => ({ x: 200 + rxShift.value * 1.4, y: 120 - rxShift.value * 0.55 }));

const lawnPts = [
  { x: 50, y: 50 },
  { x: 160, y: 50 },
  { x: 280, y: 50 },
  { x: 400, y: 50 },
  { x: 400, y: 90 },
  { x: 280, y: 90 },
  { x: 160, y: 90 },
  { x: 50, y: 90 },
];

function sgY(i: number, smooth: boolean): number {
  const base = 90 + 40 * Math.sin(i / 5) + 25 / (1 + Math.exp(-(i - 22) / 2));
  const noise = smooth ? 0 : 10 * Math.sin(i * 2.7) + 6 * Math.cos(i * 1.9);
  return base + noise;
}
const noisySpec = computed(() =>
  Array.from({ length: 48 }, (_, i) => `${40 + i * 9},${sgY(i, false)}`).join(" "),
);
const smoothSpec = computed(() =>
  Array.from({ length: 48 }, (_, i) => `${40 + i * 9},${sgY(i, true)}`).join(" "),
);

const regPts = [
  { x: 80, y: 160 },
  { x: 120, y: 145 },
  { x: 160, y: 120 },
  { x: 200, y: 110 },
  { x: 240, y: 88 },
  { x: 280, y: 70 },
  { x: 320, y: 58 },
];

const lutLines = [
  wavePts(0.5, 0, 0.4),
  wavePts(0.7, 0.4, 0.7),
  wavePts(1.0, 0.1, 1.0),
];
const lutHit = 2;
const lutQuery = wavePts(0.95, 0.12, 0.96);

const fsA = [
  { x: 90, y: 150 },
  { x: 120, y: 130 },
  { x: 100, y: 110 },
  { x: 140, y: 145 },
];
const fsB = [
  { x: 260, y: 70 },
  { x: 300, y: 90 },
  { x: 280, y: 50 },
  { x: 320, y: 75 },
];

const chStable = [
  { x: 90, y: 160 },
  { x: 140, y: 140 },
  { x: 190, y: 118 },
  { x: 240, y: 95 },
];
const chChange = [
  { x: 160, y: 70 },
  { x: 220, y: 150 },
];

function majFill(c: number, r: number, after: boolean): string {
  const pepper = c === 4 && r === 2;
  if (!after) {
    if (pepper) return "var(--warn)";
    return r <= 2 ? "var(--forest-2)" : "var(--viz-warm)";
  }
  return r <= 2 ? "var(--forest-2)" : "var(--viz-warm)";
}
</script>
