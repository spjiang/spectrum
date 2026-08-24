<template>
  <div class="story">
    <p class="story-one">一句话：你在网页上点「执行」，请求钻进一台算法服务，45 个抽屉里有一个被打开，算完把图画回来。</p>

    <svg class="story-wide" viewBox="0 0 1040 320" role="img" aria-label="技术路径示意">
      <rect width="1040" height="320" fill="var(--paper-3)" />

      <!-- 人 + 浏览器 -->
      <g class="hit" @click="goHome">
        <rect x="24" y="48" width="210" height="200" fill="#fff" stroke="var(--line)" />
        <rect x="40" y="64" width="178" height="118" fill="var(--nav-bg)" />
        <rect x="52" y="80" width="70" height="10" fill="var(--viz-warm)" />
        <rect x="52" y="98" width="154" height="6" fill="var(--forest-2)" />
        <rect x="52" y="112" width="120" height="6" fill="var(--forest-2)" opacity="0.5" />
        <rect x="52" y="148" width="64" height="18" fill="var(--viz-warm)" />
        <circle cx="88" cy="268" r="22" fill="var(--forest)" />
        <rect x="70" y="288" width="36" height="22" fill="var(--forest-2)" />
        <text x="128" y="276" fill="var(--ink)" font-size="14" font-family="PingFang SC, sans-serif">你点按钮</text>
        <text x="40" y="236" fill="var(--ink-soft)" font-size="12">控制台 :5173</text>
      </g>

      <path d="M248 148 L318 148" stroke="var(--viz-warm)" stroke-width="4" />
      <polygon points="318,140 338,148 318,156" fill="var(--viz-warm)" />
      <text x="252" y="132" fill="var(--viz-warm)" font-size="12">/api</text>

      <!-- 服务箱子 -->
      <g>
        <rect x="350" y="56" width="200" height="184" fill="var(--forest)" />
        <rect x="366" y="74" width="168" height="28" fill="var(--forest-2)" />
        <circle cx="384" cy="88" r="6" fill="var(--ok)" />
        <text x="400" y="92" fill="var(--gold-soft)" font-size="13">算法服务 :28800</text>
        <text x="366" y="132" fill="var(--nav-text)" font-size="12">收到文件 + 参数</text>
        <text x="366" y="154" fill="var(--nav-text)" font-size="12">打开对应算法抽屉</text>
        <text x="366" y="190" fill="var(--gold-soft)" font-size="13">POST /run</text>
        <text x="366" y="214" fill="#9aa394" font-size="11">一台进程，45 个入口</text>
      </g>

      <path d="M564 148 L630 148" stroke="var(--viz-warm)" stroke-width="4" />
      <polygon points="630,140 650,148 630,156" fill="var(--viz-warm)" />

      <!-- 45 抽屉墙 -->
      <g>
        <text x="668" y="48" fill="var(--ink-soft)" font-size="12">45 个算法抽屉</text>
        <g v-for="r in 5" :key="'r' + r">
          <g v-for="c in 9" :key="'c' + r + c">
            <rect
              :x="662 + (c - 1) * 26"
              :y="62 + (r - 1) * 26"
              width="22"
              height="22"
              :fill="drawerColor(r, c)"
              stroke="var(--paper)"
            />
          </g>
        </g>
        <rect x="662" y="198" width="126" height="36" fill="var(--viz-warm)" />
        <text x="674" y="220" fill="var(--ink)" font-size="12">当前打开的一项</text>
      </g>

      <path d="M820 148 L878 148" stroke="var(--viz-warm)" stroke-width="4" />
      <polygon points="878,140 898,148 878,156" fill="var(--viz-warm)" />

      <!-- 结果画回来 -->
      <g class="hit" @click="go('27_ndvi')">
        <rect x="910" y="70" width="108" height="86" fill="#2b3d32" />
        <rect x="922" y="84" width="40" height="58" fill="var(--ok)" />
        <rect x="966" y="84" width="40" height="58" fill="#d4a24a" />
        <text x="910" y="182" fill="var(--ink)" font-size="13">把图画回网页</text>
        <text x="910" y="202" fill="var(--ink-soft)" font-size="11">GeoTIFF / JSON</text>
      </g>
    </svg>

    <p class="story-foot">
      不必记端口号：左边是人用的网页，中间是算的机器，右边是算完的图。点「看图」类抽屉可进入 NDVI 示例。
    </p>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

function drawerColor(r: number, c: number): string {
  if (r === 3 && c === 5) return "var(--viz-warm)";
  if (r <= 2) return "var(--forest-2)";
  if (r === 3) return "#4a7c76";
  return "#8fb3ae";
}

function goHome() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function go(id: string) {
  void router.push(`/algo/${id}`);
}
</script>
