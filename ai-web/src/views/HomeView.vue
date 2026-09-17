<template>
  <div>
    <p class="lede">
      本站只做<strong>处理层</strong>对照：传统流水线怎么走，AI 大模型在这一层多写了什么边界。
      单算法解读已在
      <a href="http://127.0.0.1:5173">算法控制台 5173</a>
      的「AI探索」里完成，这里不再按 27–43 逐条接模型。
    </p>
    <p class="lede">
      大模型<strong>不算图、不改公式、不看原始影像</strong>。它干的是参谋：这场该看哪张图、建议说到哪一句、哪里必须停住。左边是没有参谋时人会怎么做。
    </p>
    <div v-if="error" class="banner warn">{{ error }}</div>
    <section class="layer-grid">
      <router-link v-for="row in layers" :key="row.id" class="layer-card" :to="'/layer/' + row.id">
        <p class="step">{{ row.level }} · {{ row.title }}</p>
        <h2>{{ row.kicker }}</h2>
        <p class="hook">{{ row.benefit }}</p>
        <span>看传统 vs AI →</span>
      </router-link>
    </section>
    <p class="foot">
      启用顶栏大模型后，进入任一层点「运行本层演示」，左侧仍是传统做法，右侧才是模型润色后的赋能说明。
    </p>
  </div>
</template>

<script setup lang="ts">
/** 首页：四层入口，不再钻单个算法。 */
import { onMounted, ref } from "vue";
import { fetchLayers } from "../api";
import type { LayerSummary } from "../types";

const layers = ref<LayerSummary[]>([]);
const error = ref("");

onMounted(async () => {
  try {
    layers.value = await fetchLayers();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "层目录加载失败";
  }
});
</script>
