<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">SPECTRUM</div>
        <h1>高光谱算法控制台</h1>
        <p>覆盖采集至地块结论全流程，共 45 项算法</p>
      </div>
      <router-link class="nav-home" to="/">全流程</router-link>
      <div class="nav-scroll">
        <details
          v-for="g in grouped"
          :key="g.level"
          class="nav-group"
          :open="openGroups.has(g.level)"
        >
          <summary @click.prevent="toggle(g.level)">
            <span class="g-name">{{ g.title }}</span>
            <span class="g-note">{{ g.level }} · {{ g.items.length }}</span>
          </summary>
          <router-link
            v-for="a in g.items"
            :key="a.id"
            class="nav-item"
            :to="`/algo/${a.id}`"
            :title="navTip(a)"
          >
            <span class="nav-text">
              <span class="nav-name">{{ a.title }}</span>
              <span v-if="navZh(a)" class="nav-zh">{{ navZh(a) }}</span>
            </span>
            <span class="nav-no">{{ a.id.split("_")[0] }}</span>
          </router-link>
        </details>
      </div>
    </aside>
    <div class="main">
      <div v-if="!healthy" class="banner">
        算法服务暂不可用。请确认后端服务已在 127.0.0.1:28800 启动。
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { fetchHealth, listAlgorithms } from "../api";
import { GROUP_ORDER, groupTitle } from "../levels";
import { navZhLine, termsForAlgorithm, tooltipForTerms } from "../glossary";
import type { AlgorithmCard } from "../types";

const route = useRoute();
const healthy = ref(true);
const algorithms = ref<AlgorithmCard[]>([]);
const openGroups = reactive(new Set<string>(["L0前", "L0", "L3"]));

const grouped = computed(() =>
  GROUP_ORDER.map((level) => ({
    level,
    title: groupTitle(level),
    items: algorithms.value.filter((a) => a.level === level),
  })).filter((g) => g.items.length),
);

function toggle(level: string) {
  if (openGroups.has(level)) openGroups.delete(level);
  else openGroups.add(level);
}

function algoTerms(a: AlgorithmCard) {
  return termsForAlgorithm(a.id, a.title, a.method);
}

function navZh(a: AlgorithmCard): string {
  return navZhLine(algoTerms(a));
}

function navTip(a: AlgorithmCard): string {
  return tooltipForTerms(algoTerms(a));
}

function expandCurrent() {
  const id = String(route.params.id || "");
  const hit = algorithms.value.find((a) => a.id === id);
  if (hit) openGroups.add(hit.level);
}

onMounted(async () => {
  healthy.value = await fetchHealth();
  try {
    algorithms.value = await listAlgorithms();
    expandCurrent();
  } catch {
    healthy.value = false;
  }
});

watch(
  () => route.params.id,
  () => expandCurrent(),
);
</script>
