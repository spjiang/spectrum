<template>
  <div class="story">
    <p class="story-one">一句话：同一块地，数据先是「相机数的数」，再变成「光有多强」，再变成「地有多绿」，最后变成「3 号田的一个数字」。</p>

    <div class="morph">
      <button type="button" class="morph-card" @click="go('04_flight_qc')">
        <svg viewBox="0 0 200 140" aria-hidden="true">
          <polygon points="70,18 150,40 150,108 70,86" fill="#7a8590" stroke="var(--ink-soft)" />
          <polygon points="70,18 70,86 28,104 28,36" fill="#5b6878" stroke="var(--ink-soft)" />
          <polygon points="28,104 70,86 150,108 108,126" fill="var(--ink-soft)" />
          <text x="78" y="70" fill="var(--paper)" font-size="22" font-family="Georgia, serif">247</text>
        </svg>
        <em>L0 采集质检</em>
        <strong>相机里的计数</strong>
        <span>像「亮度旋钮的刻度」，还没有物理单位。</span>
      </button>
      <span class="morph-arr">变成</span>
      <button type="button" class="morph-card" @click="go('10_radiance_calibration')">
        <svg viewBox="0 0 200 140" aria-hidden="true">
          <polygon points="70,18 150,40 150,108 70,86" fill="#e8b15a" stroke="var(--viz-warm)" />
          <polygon points="70,18 70,86 28,104 28,36" fill="#d4a24a" stroke="var(--viz-warm)" />
          <polygon points="28,104 70,86 150,108 108,126" fill="#b45309" />
          <circle cx="108" cy="64" r="16" fill="var(--gold-soft)" />
          <circle cx="108" cy="64" r="7" fill="var(--viz-warm)" />
        </svg>
        <em>L1 辐射校正</em>
        <strong>光有多强</strong>
        <span>定标之后，不同相机、不同天可以比。</span>
      </button>
      <span class="morph-arr">变成</span>
      <button type="button" class="morph-card" @click="go('16_orthorectify')">
        <svg viewBox="0 0 200 140" aria-hidden="true">
          <rect x="18" y="18" width="164" height="104" fill="#d4ece8" stroke="var(--forest-2)" />
          <polygon points="40,96 88,48 128,70 168,40 168,112 40,112" fill="#7eb89a" />
          <polygon points="70,22 150,36 150,92 70,78" fill="rgba(17, 78, 75, 0.35)" />
        </svg>
        <em>L2 反射率与正射</em>
        <strong>能贴到地图上的立方体</strong>
        <span>正射 + 反射率。指数、分类都吃这个。</span>
      </button>
      <span class="morph-arr">抽出</span>
      <button type="button" class="morph-card" @click="go('27_ndvi')">
        <svg viewBox="0 0 200 140" aria-hidden="true">
          <rect x="22" y="18" width="156" height="104" fill="var(--forest)" />
          <rect x="22" y="18" width="70" height="104" fill="var(--ok)" />
          <rect x="92" y="18" width="50" height="104" fill="#7a9a4a" />
          <rect x="142" y="18" width="36" height="104" fill="#d4a24a" />
        </svg>
        <em>L3 指数与识别</em>
        <strong>绿旺黄弱，或类别色块</strong>
        <span>立方体被压成一张「人能看懂」的图。</span>
      </button>
      <span class="morph-arr">汇总</span>
      <button type="button" class="morph-card" @click="go('45_parcel_zonal_stats')">
        <svg viewBox="0 0 200 140" aria-hidden="true">
          <rect x="36" y="16" width="128" height="108" fill="#fff" stroke="var(--line-strong)" />
          <text x="48" y="44" font-size="12" fill="var(--ink)">3号田</text>
          <text x="48" y="72" font-size="22" fill="var(--forest)" font-family="Georgia, serif">0.72</text>
          <text x="48" y="96" font-size="11" fill="var(--ink-soft)">平均 NDVI</text>
        </svg>
        <em>L4 地块汇总</em>
        <strong>一块地一个数</strong>
        <span>给领导看的是这张纸，不是立方体。</span>
      </button>
    </div>

    <div class="forbid">
      <svg viewBox="0 0 640 88" aria-hidden="true">
        <rect width="640" height="88" fill="var(--paper-3)" />
        <polygon points="40,20 90,32 90,68 40,56" fill="#7a8590" />
        <text x="100" y="50" font-size="13" fill="var(--ink-soft)">原始计数</text>
        <path d="M180 44 L430 44" stroke="var(--warn)" stroke-width="3" stroke-dasharray="8 6" />
        <circle cx="308" cy="44" r="16" fill="#fff" stroke="var(--warn)" stroke-width="3" />
        <path d="M300 36 L316 52 M316 36 L300 52" stroke="var(--warn)" stroke-width="3" />
        <rect x="450" y="18" width="70" height="52" fill="var(--ok)" />
        <text x="530" y="50" font-size="13" fill="var(--ink-soft)">NDVI</text>
      </svg>
      <p>最容易错的一步：不要从原始计数直接跳到植被指数。中间必须经过「光有多强 → 能上地图的反射率」。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
function go(id: string) {
  void router.push(`/algo/${id}`);
}
</script>
