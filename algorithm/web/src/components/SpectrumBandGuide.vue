<template>
  <div class="spec-guide">
    <svg
      viewBox="0 0 748 96"
      class="spec-guide-svg"
      role="img"
      :aria-label="ariaLabel"
    >
      <defs>
        <linearGradient :id="ids.vis" x1="0" y1="0" x2="1" y2="0">
          <stop v-for="stop in visStops" :key="stop.nm" :offset="stop.offset" :stop-color="stop.color" />
        </linearGradient>
        <linearGradient :id="ids.swir" x1="0" y1="0" x2="1" y2="0">
          <stop v-for="stop in swirStops" :key="stop.nm" :offset="stop.offset" :stop-color="stop.color" />
        </linearGradient>
        <linearGradient :id="ids.gloss" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18" />
          <stop offset="70%" stop-color="#ffffff" stop-opacity="0" />
        </linearGradient>
        <pattern :id="ids.hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)">
          <line x1="0" y1="0" x2="0" y2="5" stroke="rgba(232,238,241,0.14)" stroke-width="1" />
        </pattern>
      </defs>

      <text x="36" y="11" class="spec-title">光谱波段</text>
      <text x="712" y="11" text-anchor="end" class="spec-unit">λ / nm</text>

      <path
        v-for="region in regions"
        :key="region.id"
        :d="bracketPath(region.fromNm, region.toNm, 26)"
        class="spec-bracket"
      />
      <text
        v-for="region in regions"
        :key="`${region.id}-label`"
        :x="(nmToX(region.fromNm) + nmToX(region.toNm)) / 2"
        y="20"
        text-anchor="middle"
        class="spec-region"
      >
        {{ region.label }}
      </text>

      <rect
        :x="vis.x"
        :y="BAR_Y"
        :width="vis.width"
        :height="BAR_H"
        :fill="`url(#${ids.vis})`"
        class="spec-film"
      />
      <rect :x="vis.x" :y="BAR_Y" :width="vis.width" :height="BAR_H / 2" :fill="`url(#${ids.gloss})`" />
      <rect
        :x="swir.x"
        :y="BAR_Y"
        :width="swir.width"
        :height="BAR_H"
        :fill="`url(#${ids.swir})`"
        class="spec-film"
      />
      <rect :x="swir.x" :y="BAR_Y" :width="swir.width" :height="BAR_H" :fill="`url(#${ids.hatch})`" />

      <g class="spec-break" :transform="`translate(${nmToX(1000)}, ${BAR_Y + BAR_H / 2})`">
        <line x1="-5" y1="-9" x2="1" y2="9" />
        <line x1="-1" y1="-9" x2="5" y2="9" />
      </g>

      <g v-for="tick in ticks" :key="tick">
        <line
          :x1="nmToX(tick)"
          :y1="BAR_Y + BAR_H"
          :x2="nmToX(tick)"
          :y2="BAR_Y + BAR_H + 5"
          class="spec-tick"
        />
        <text :x="nmToX(tick)" :y="BAR_Y + BAR_H + 16" text-anchor="middle" class="spec-tick-lab">
          {{ tick }}
        </text>
      </g>

      <g
        v-for="band in bands"
        :key="band.id"
        class="spec-mark"
        :class="{ on: active.has(band.id), hover: hoverId === band.id }"
        @mouseenter="hoverId = band.id"
        @mouseleave="hoverId = null"
      >
        <rect
          :x="nmToX(band.nm) - 20"
          :y="BAR_Y - 4"
          width="40"
          height="62"
          fill="transparent"
        />
        <line
          :x1="nmToX(band.nm)"
          :y1="BAR_Y"
          :x2="nmToX(band.nm)"
          :y2="BAR_Y + BAR_H"
          class="spec-hair"
        />
        <circle
          v-if="active.has(band.id)"
          :cx="nmToX(band.nm)"
          :cy="BAR_Y + BAR_H / 2"
          r="6.2"
          :fill="band.color"
          class="spec-glow"
        />
        <polygon :points="diamond(band.nm)" :fill="band.color" />
        <text :x="nmToX(band.nm)" y="84" text-anchor="middle" class="spec-name">
          {{ band.name }}
        </text>
      </g>
    </svg>
    <p class="spec-guide-use">
      <template v-if="hovered">
        <span class="spec-guide-k">{{ hovered.region }}</span>
        <span class="spec-guide-v">{{ hovered.name }} · {{ hovered.abbr }} · {{ hovered.nmLabel }}</span>
        <span class="spec-guide-n">典型中心，不是固定窗口</span>
      </template>
      <template v-else>
        {{ caption }}
      </template>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, useId } from "vue";
import {
  AXIS_TICKS_NM,
  BAR_H,
  BAR_Y,
  SPECTRUM_BANDS,
  SPECTRUM_REGIONS,
  bandsForAlgorithm,
  bracketPath,
  nmToX,
  swirBar,
  swirOffset,
  visBar,
  visOffset,
} from "../spectrumBands";

const props = defineProps<{ algorithmId?: string }>();

const uid = useId().replace(/[^a-zA-Z0-9_-]/g, "");
const ids = {
  vis: `spec-vis-${uid}`,
  swir: `spec-swir-${uid}`,
  gloss: `spec-gloss-${uid}`,
  hatch: `spec-hatch-${uid}`,
};

const bands = SPECTRUM_BANDS;
const regions = SPECTRUM_REGIONS;
const ticks = AXIS_TICKS_NM;
const vis = visBar();
const swir = swirBar();
const hoverId = ref<string | null>(null);

const visStops = [
  { nm: 400, color: "#2a0078" },
  { nm: 425, color: "#3a00d4" },
  { nm: 450, color: "#0048ff" },
  { nm: 480, color: "#0098ff" },
  { nm: 500, color: "#00c8c0" },
  { nm: 520, color: "#1ad040" },
  { nm: 555, color: "#b8e000" },
  { nm: 575, color: "#f0d400" },
  { nm: 590, color: "#ff9800" },
  { nm: 620, color: "#f02800" },
  { nm: 650, color: "#c80000" },
  { nm: 700, color: "#5a080c" },
  { nm: 740, color: "#301014" },
  { nm: 800, color: "#1c1014" },
  { nm: 1000, color: "#120e12" },
].map((stop) => ({ ...stop, offset: visOffset(stop.nm) }));

const swirStops = [
  { nm: 1000, color: "#1a1428" },
  { nm: 1400, color: "#2c2450" },
  { nm: 1600, color: "#3c2e62" },
  { nm: 2200, color: "#16121f" },
].map((stop) => ({ ...stop, offset: swirOffset(stop.nm) }));

const active = computed(() => bandsForAlgorithm(props.algorithmId));
const hovered = computed(() => bands.find((b) => b.id === hoverId.value) ?? null);

const caption = computed(() => {
  const names = bands.filter((b) => active.value.has(b.id)).map((b) => b.name);
  if (names.length) return `本页用 ${names.join("、")}。热红外未画出。`;
  return "从左到右波长变长。红外分近红外与短波红外，不是同一种。热红外未画出。";
});

const ariaLabel = computed(() => {
  if (hovered.value) {
    return `${hovered.value.region} ${hovered.value.name} ${hovered.value.nmLabel}`;
  }
  return caption.value;
});

function diamond(nm: number): string {
  const cx = nmToX(nm);
  const cy = BAR_Y + BAR_H / 2;
  const r = 3.4;
  return `${cx},${cy - r} ${cx + r},${cy} ${cx},${cy + r} ${cx - r},${cy}`;
}
</script>
