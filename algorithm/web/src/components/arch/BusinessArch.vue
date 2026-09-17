<template>
  <div class="story">
    <p class="story-one">业务链路：航线采集 → 辐射与几何校正 → 指数/分类制图 → 地块分区统计。</p>

    <div class="story-strip">
      <button type="button" class="scene" @click="go('01_flight_planning')">
        <svg viewBox="0 0 280 168" aria-hidden="true">
          <rect width="280" height="168" fill="#e7efe6" />
          <rect x="0" y="108" width="280" height="60" fill="#c5d4b8" />
          <path d="M0 118 L40 112 L80 122 L120 110 L160 124 L200 112 L240 120 L280 114 V168 H0 Z" fill="#7eb89a" />
          <g stroke="var(--forest-2)" stroke-width="1.6" fill="none" opacity="0.7">
            <path d="M20 128 L260 128" />
            <path d="M260 140 L20 140" />
            <path d="M20 152 L260 152" />
          </g>
          <path d="M118 38 L162 50 L150 58 L132 54 Z" fill="var(--forest)" />
          <circle cx="128" cy="48" r="3" fill="var(--viz-warm)" />
          <line x1="140" y1="52" x2="148" y2="78" stroke="var(--ink-soft)" stroke-width="1" />
        </svg>
        <em>1. 采集</em>
        <strong>按航线完成测区覆盖</strong>
        <span>检查航带覆盖、重叠度与姿态是否满足后续几何定位。</span>
      </button>

      <button type="button" class="scene" @click="go('10_radiance_calibration')">
        <svg viewBox="0 0 280 168" aria-hidden="true">
          <rect width="280" height="168" fill="var(--paper-3)" />
          <g transform="translate(28,36)">
            <rect width="88" height="72" fill="#8a96a3" stroke="var(--ink-soft)" />
            <rect x="8" y="10" width="18" height="52" fill="#6b6356" />
            <rect x="32" y="10" width="18" height="52" fill="#b8a990" />
            <rect x="56" y="10" width="18" height="52" fill="#6b6356" />
            <text x="8" y="92" fill="var(--ink-soft)" font-size="11">原始计数</text>
          </g>
          <path d="M132 72 L168 72" stroke="var(--viz-warm)" stroke-width="3" marker-end="url(#bizArr)" />
          <g transform="translate(176,36)">
            <rect width="76" height="72" fill="#d4ece8" stroke="var(--forest-2)" />
            <rect x="10" y="14" width="56" height="44" fill="#7fa37a" />
            <text x="6" y="92" fill="var(--forest-2)" font-size="11">辐亮度</text>
          </g>
          <defs>
            <marker id="bizArr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 Z" fill="var(--viz-warm)" />
            </marker>
          </defs>
        </svg>
        <em>2. 校正</em>
        <strong>将仪器计数转换为物理量</strong>
        <span>暗电流、辐射定标与正射未完成时，指数不可定量使用。</span>
      </button>

      <button type="button" class="scene" @click="go('27_ndvi')">
        <svg viewBox="0 0 280 168" aria-hidden="true">
          <rect width="280" height="168" fill="var(--paper-3)" />
          <rect x="36" y="28" width="120" height="92" fill="#2b3d32" />
          <rect x="48" y="40" width="44" height="68" fill="var(--ok)" />
          <rect x="96" y="40" width="48" height="68" fill="#d4a24a" />
          <circle cx="210" cy="78" r="28" fill="var(--forest)" />
          <circle cx="202" cy="74" r="6" fill="var(--paper)" />
          <circle cx="218" cy="74" r="6" fill="var(--paper)" />
          <path d="M200 92 Q210 100 220 92" stroke="var(--gold-soft)" fill="none" />
        </svg>
        <em>3. 制图</em>
        <strong>由反射率立方体生成指数或分类图</strong>
        <span>L3 输出植被指数、分类或其他专题图。</span>
      </button>

      <button type="button" class="scene" @click="go('45_parcel_zonal_stats')">
        <svg viewBox="0 0 280 168" aria-hidden="true">
          <rect width="280" height="168" fill="var(--paper)" />
          <rect x="44" y="30" width="86" height="100" fill="#fff" stroke="var(--line-strong)" />
          <line x1="56" y1="48" x2="116" y2="48" stroke="var(--line)" />
          <line x1="56" y1="64" x2="116" y2="64" stroke="var(--line)" />
          <line x1="56" y1="80" x2="100" y2="80" stroke="var(--viz-warm)" stroke-width="3" />
          <text x="56" y="112" font-size="10" fill="var(--forest)">3号田 0.72</text>
          <rect x="154" y="48" width="80" height="64" fill="#d4ece8" stroke="var(--forest-2)" />
          <path d="M162 88 L186 56 L206 96 L226 70" fill="none" stroke="var(--forest-2)" />
        </svg>
        <em>4. 统计</em>
        <strong>按地块输出分区统计</strong>
        <span>将栅格结果汇总为地块均值等统计量，供业务系统引用。</span>
      </button>
    </div>

    <p class="story-foot">
      点击任一环节进入代表算法。L3 指数与识别位于制图环节；上游辐射与几何处理未完成时，指数与分类结果不可定量使用。
    </p>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
function go(id: string) {
  void router.push(`/algo/${id}`);
}
</script>
