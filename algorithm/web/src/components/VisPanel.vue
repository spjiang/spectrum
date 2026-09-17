<template>
  <div class="vis-box">
    <h5>{{ title }} · {{ asset?.name || "无文件" }}</h5>
    <div v-if="!asset?.url" class="empty">暂无可视化文件。</div>
    <template v-else>
      <img
        v-if="isImage"
        ref="imgEl"
        :src="asset.url"
        :alt="asset.name"
        @click="onClickRaster"
      />
      <div v-if="colorScale" class="vis-legend">
        <div class="vis-legend-bar" aria-hidden="true" />
        <div class="vis-legend-ticks">
          <span>红 {{ formatIndex(colorScale.low) }} 偏低</span>
          <span>黄 {{ formatIndex(colorScale.mid) }}</span>
          <span>绿 {{ formatIndex(colorScale.high) }} 偏高</span>
        </div>
      </div>
      <p
        v-if="colorNote"
        class="vis-color-note"
        :class="{ 'vis-color-note-takeaway': isRedEdgeParamsStack }"
      >{{ colorNote }}</p>
      <div v-if="isMap || vis === 'csv_track'" ref="mapEl" class="map" />
      <div v-if="needChart" ref="chartEl" class="chart" />
      <pre v-if="textBlock" class="data">{{ textBlock }}</pre>
      <div v-if="vis === 'none'" class="empty">该文件类型请下载查看：{{ asset.name }}</div>
      <div v-if="spectrumHint" class="hint">{{ spectrumHint }}</div>
      <div v-if="spectrumReady" ref="specEl" class="chart" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import * as echarts from "echarts";
import L from "leaflet";
import { fetchJson, fetchRasterMeta, fetchSpectrum, fetchText } from "../api";
import { rasterClickToCell } from "../rasterClick";
import type { TestdataHttp } from "../types";

const props = defineProps<{
  title: string;
  asset: TestdataHttp | null | undefined;
  algorithmId?: string;
}>();

const imgEl = ref<HTMLImageElement | null>(null);
const mapEl = ref<HTMLDivElement | null>(null);
const chartEl = ref<HTMLDivElement | null>(null);
const specEl = ref<HTMLDivElement | null>(null);
const textBlock = ref("");
const spectrumHint = ref("");
const spectrumReady = ref(false);
const rasterBands = ref(0);

let map: L.Map | null = null;
let chart: echarts.ECharts | null = null;
let specChart: echarts.ECharts | null = null;

const colorScale = ref<{ low: number; mid: number; high: number } | null>(null);
const vis = computed(() => props.asset?.vis || "none");
const isRedEdgeParamsStack = computed(() => {
  if (props.algorithmId !== "31_red_edge_params") return false;
  return (props.asset?.name || "").toLowerCase().includes("red_edge_params");
});
const isImage = computed(() =>
  ["png", "raster_falsecolor", "raster_index", "raster_class"].includes(vis.value),
);
const colorNote = computed(() => {
  if (isRedEdgeParamsStack.value) {
    return "这张彩图只用来扫一眼空间上有没有成片差异，不是长势图。红不等于差、绿不等于好。要看绿势，看 Guyot 红边位置预览图，或只打开本文件第 1 层。";
  }
  if (vis.value === "raster_index" || colorScale.value) {
    return "上图右侧色条和下面这行数字，就是这种颜色对应的指数值，和 TIF 格子里的数是同一套。绿=这张图里相对高，红=相对低。特别暗或特别亮的少数格子会顶到色带两端。不能只靠颜色当读数，要看色条上的数字。";
  }
  if (vis.value === "raster_falsecolor") {
    return "假彩色：每个波段先不管特别暗、特别亮的少数格子，再赋给红、绿、蓝通道。颜色只用来看空间结构，不是地物真实颜色。";
  }
  if (vis.value === "raster_class") {
    return "分类色块只用来区分编号。颜色深浅不表示面积、置信度或业务等级。";
  }
  return "";
});
const isMap = computed(() => vis.value === "geojson_map");
const needChart = computed(() =>
  ["csv_track", "csv_spectrum", "csv_table", "json_table"].includes(vis.value),
);

function formatIndex(value: number): string {
  if (!Number.isFinite(value)) return "—";
  const abs = Math.abs(value);
  if (abs >= 100) return value.toFixed(0);
  if (abs >= 10) return value.toFixed(1);
  return value.toFixed(3);
}

function disposeAll() {
  map?.remove();
  map = null;
  chart?.dispose();
  chart = null;
  specChart?.dispose();
  specChart = null;
  textBlock.value = "";
  spectrumHint.value = "";
  spectrumReady.value = false;
  colorScale.value = null;
}

function parseCsv(text: string): { headers: string[]; rows: string[][] } {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  if (!lines.length) return { headers: [], rows: [] };
  const headers = lines[0].split(",").map((s) => s.trim());
  const rows = lines.slice(1).map((ln) => ln.split(",").map((s) => s.trim()));
  return { headers, rows };
}

function colIndex(headers: string[], names: string[]): number {
  const lower = headers.map((h) => h.toLowerCase());
  for (const n of names) {
    const i = lower.indexOf(n);
    if (i >= 0) return i;
  }
  return -1;
}

function renderTable(headers: string[], rows: string[][]) {
  const el = chartEl.value;
  if (!el) return;
  chart = echarts.init(el);
  const show = rows.slice(0, 40);
  chart.setOption({
    tooltip: { trigger: "item" },
    dataset: { source: [headers, ...show] },
    xAxis: { type: "category" },
    yAxis: {},
    series: headers.slice(1, 4).map((_, i) => ({
      type: "line",
      encode: { x: 0, y: i + 1 },
    })),
  });
}

function addBaseMap(target: L.Map) {
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 19,
    attribution: "OSM",
  }).addTo(target);
}

function drawTrackMap(rows: string[][], lonI: number, latI: number) {
  if (!mapEl.value) return;
  const latlngs: L.LatLngExpression[] = rows
    .map((r) => [Number(r[latI]), Number(r[lonI])] as [number, number])
    .filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
  map = L.map(mapEl.value, { zoomControl: true, attributionControl: false });
  addBaseMap(map);
  if (!latlngs.length) {
    map.setView([22.54, 114.06], 12);
    return;
  }
  const line = L.polyline(latlngs, { color: "#c9a227", weight: 3 }).addTo(map);
  L.circleMarker(latlngs[0], { radius: 5, color: "#1f4d3a" }).addTo(map);
  L.circleMarker(latlngs[latlngs.length - 1], { radius: 5, color: "#9b2c2c" }).addTo(map);
  map.fitBounds(line.getBounds().pad(0.2));
  window.setTimeout(() => map?.invalidateSize(), 80);
}

async function drawChart() {
  const url = props.asset?.url;
  if (!url) return;
  if (vis.value === "json_table") {
    const data = await fetchJson(url);
    textBlock.value = JSON.stringify(data, null, 2);
    if (!chartEl.value) return;
    const obj = data as Record<string, unknown>;
    if (obj && typeof obj === "object" && !Array.isArray(obj)) {
      const keys = Object.keys(obj).filter((k) => typeof obj[k] !== "object");
      if (keys.length) {
        chart = echarts.init(chartEl.value);
        chart.setOption({
          tooltip: {},
          xAxis: { type: "category", data: keys, axisLabel: { rotate: 30 } },
          yAxis: { type: "value" },
          series: [
            {
              type: "bar",
              data: keys.map((k) => Number(obj[k])),
              itemStyle: { color: "#2d6a4f" },
            },
          ],
        });
      }
    }
    return;
  }
  const text = await fetchText(url);
  const { headers, rows } = parseCsv(text);
  if (vis.value === "csv_spectrum" && chartEl.value) {
    const y = rows.map((r) => Number(r[r.length - 1]));
    const x = rows.map((r, i) => Number(r[0]) || i);
    chart = echarts.init(chartEl.value);
    chart.setOption({
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: x, name: "波段/波长" },
      yAxis: { name: "反射率/DN" },
      series: [{ type: "line", data: y, showSymbol: false, lineStyle: { color: "#1f4d3a" } }],
    });
    return;
  }
  if (vis.value === "csv_track") {
    const lonI = colIndex(headers, ["lon", "longitude", "lng"]);
    const latI = colIndex(headers, ["lat", "latitude"]);
    if (lonI >= 0 && latI >= 0) {
      drawTrackMap(rows, lonI, latI);
      if (chartEl.value) {
        const altI = colIndex(headers, ["alt", "altitude", "height"]);
        chart = echarts.init(chartEl.value);
        chart.setOption({
          tooltip: { trigger: "axis" },
          legend: { data: altI >= 0 ? ["高度"] : ["纬度"] },
          xAxis: { type: "category", data: rows.map((_, i) => i), name: "历元" },
          yAxis: {},
          series: [
            {
              name: altI >= 0 ? "高度" : "纬度",
              type: "line",
              showSymbol: false,
              data: rows.map((r) => Number(r[altI >= 0 ? altI : latI])),
              lineStyle: { color: "#1f4d3a" },
            },
          ],
        });
      }
      return;
    }
  }
  if (chartEl.value) renderTable(headers, rows);
}

async function drawMap() {
  const url = props.asset?.url;
  if (!url || !mapEl.value) return;
  const gj = (await fetchJson(url)) as GeoJSON.GeoJsonObject;
  map = L.map(mapEl.value, { zoomControl: true, attributionControl: false });
  addBaseMap(map);
  const layer = L.geoJSON(gj as GeoJSON.GeoJSON, {
    style: { color: "#c9a227", weight: 2, fillColor: "#2d6a4f", fillOpacity: 0.25 },
    pointToLayer: (_f, latlng) =>
      L.circleMarker(latlng, { radius: 4, color: "#1f4d3a", fillOpacity: 0.9 }),
  }).addTo(map);
  const b = layer.getBounds();
  if (b.isValid()) map.fitBounds(b.pad(0.15));
  else map.setView([22.54, 114.06], 12);
  window.setTimeout(() => map?.invalidateSize(), 80);
  spectrumHint.value = "图中黄色范围表示测区或地块，支持滚轮缩放。此处为输入数据，算法结果将显示于右侧。";
}

async function prepareRaster() {
  if (!props.asset?.url || !isImage.value) return;
  if (!props.asset.url.includes("/preview/raster")) {
    spectrumHint.value = "预览图像由算法生成。";
    return;
  }
  try {
    const meta = await fetchRasterMeta(props.asset.url);
    rasterBands.value = meta.bands;
    if (
      typeof meta.colorLow === "number" &&
      typeof meta.colorHigh === "number" &&
      typeof meta.colorMid === "number"
    ) {
      colorScale.value = { low: meta.colorLow, mid: meta.colorMid, high: meta.colorHigh };
    }
    spectrumHint.value =
      meta.bands >= 3
        ? `数据立方体 ${meta.width}×${meta.height}×${meta.bands}。点击图像可查看该像元光谱。`
        : `栅格尺寸 ${meta.width}×${meta.height}，共 ${meta.bands} 个波段。`;
  } catch {
    spectrumHint.value = "预览图已加载";
  }
}

async function onClickRaster(ev: MouseEvent) {
  if (!props.asset?.url?.includes("/preview/raster") || rasterBands.value < 3) return;
  const img = imgEl.value;
  if (!img) return;
  const rect = img.getBoundingClientRect();
  try {
    const meta = await fetchRasterMeta(props.asset.url);
    const cell = rasterClickToCell(
      ev.clientX,
      ev.clientY,
      { left: rect.left, top: rect.top, width: rect.width, height: rect.height },
      img.naturalWidth,
      img.naturalHeight,
      meta.width,
      meta.height,
    );
    if (!cell) {
      spectrumHint.value = `数据立方体 ${meta.width}×${meta.height}×${meta.bands}。请点彩色格子，不要点两侧黑边。`;
      return;
    }
    const { row, col } = cell;
    const spec = await fetchSpectrum(props.asset.url, row, col);
    spectrumReady.value = true;
    await nextTick();
    specChart?.dispose();
    if (!specEl.value) return;
    specChart = echarts.init(specEl.value);
    specChart.setOption({
      title: { text: `像元 (${row}, ${col})`, left: 8, textStyle: { fontSize: 12 } },
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: spec.wavelengths_nm, name: "nm" },
      yAxis: { name: "值" },
      series: [
        {
          type: "line",
          showSymbol: false,
          data: spec.values,
          lineStyle: { color: "#c9a227", width: 2 },
        },
      ],
    });
  } catch (e) {
    spectrumHint.value = e instanceof Error ? e.message : "光谱读取失败";
  }
}

async function render() {
  disposeAll();
  await nextTick();
  try {
    if (isMap.value) await drawMap();
    else if (needChart.value) await drawChart();
    else if (isImage.value) await prepareRaster();
  } catch (e) {
    textBlock.value = e instanceof Error ? e.message : "可视化失败";
  }
}

watch(
  () => [props.asset?.url, props.asset?.vis],
  () => {
    void render();
  },
  { immediate: true },
);

onBeforeUnmount(disposeAll);
</script>
