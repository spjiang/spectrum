<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">SPECTRUM</div>
        <h1>高光谱算法控制台</h1>
        <p>覆盖采集至地块结论全流程，共 55 项算法</p>
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
              <span class="nav-name">
                {{ a.title }}
                <span
                  v-if="isAlgorithmVerified(a.id)"
                  class="nav-ok"
                  title="已人工核实"
                  aria-label="已人工核实"
                >✓</span>
              </span>
              <span v-if="navZh(a)" class="nav-zh">{{ navZh(a) }}</span>
            </span>
            <span class="nav-no">{{ a.id.split("_")[0] }}</span>
          </router-link>
        </details>
      </div>
    </aside>
    <div class="main">
      <header class="console-top">
        <SpectrumBandGuide :algorithm-id="currentAlgoId" />
        <div class="console-settings" ref="menuRoot">
          <button
            class="console-settings-trigger"
            type="button"
            :aria-expanded="menuOpen"
            aria-haspopup="menu"
            @click="toggleMenu"
          >
            设置
          </button>
          <div v-if="menuOpen" class="console-settings-menu" role="menu">
            <button
              class="console-settings-item"
              type="button"
              role="menuitem"
              :data-on="savedOn"
              @click="openLlmDialog"
            >
              <span class="console-settings-item-label">大模型配置</span>
              <span class="console-settings-state">{{ savedOn ? "已启用" : "未启用" }}</span>
            </button>
          </div>
        </div>
        <Teleport to="body">
          <div
            v-if="dialogOpen"
            class="console-llm-overlay"
            @click.self="closeDialog"
          >
            <div class="console-llm-dialog" role="dialog" aria-modal="true" aria-labelledby="llm-dialog-title">
              <p id="llm-dialog-title" class="console-llm-step">大模型配置</p>
              <p class="console-llm-detail">
                点保存后才会用于「AI探索」。密钥只存在本机浏览器，不写仓库。
              </p>
              <label class="console-llm-on">
                <input v-model="draft.enabled" type="checkbox" />
                启用真实大模型
              </label>
              <div class="console-llm-grid">
                <label>
                  Base URL
                  <input v-model="draft.baseUrl" type="url" autocomplete="off" />
                </label>
                <label>
                  模型
                  <input v-model="draft.model" type="text" autocomplete="off" />
                </label>
                <label class="wide">
                  API Key
                  <input v-model="draft.apiKey" type="password" autocomplete="off" />
                </label>
              </div>
              <p class="console-llm-meta">默认 DeepSeek：https://api.deepseek.com · deepseek-chat。</p>
              <div class="console-llm-actions">
                <button class="btn ghost" type="button" @click="closeDialog">取消</button>
                <button class="btn gold" type="button" @click="saveDialog">保存</button>
              </div>
            </div>
          </div>
        </Teleport>
      </header>
      <div v-if="!healthy" class="banner">
        算法服务暂不可用。请确认后端服务已在 127.0.0.1:28800 启动。
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, provide, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { fetchHealth, listAlgorithms } from "../api";
import { GROUP_ORDER, groupTitle } from "../levels";
import { navZhLine, termsForAlgorithm, tooltipForTerms } from "../glossary";
import { loadLlmConfig, saveLlmConfig, type LlmConfig } from "../llmConfig";
import { LLM_CONFIG_KEY } from "../llmKey";
import { isAlgorithmVerified } from "../verified";
import SpectrumBandGuide from "./SpectrumBandGuide.vue";
import type { AlgorithmCard } from "../types";

const route = useRoute();
const healthy = ref(true);
const algorithms = ref<AlgorithmCard[]>([]);
const openGroups = reactive(new Set<string>(["L0前", "L0", "L3"]));
const llm = ref(loadLlmConfig());
const draft = ref<LlmConfig>({ ...llm.value });
const menuOpen = ref(false);
const dialogOpen = ref(false);
const menuRoot = ref<HTMLElement | null>(null);

provide(LLM_CONFIG_KEY, llm);

const savedOn = computed(() => llm.value.enabled && !!llm.value.apiKey.trim());
const currentAlgoId = computed(() => {
  const id = route.params.id;
  return typeof id === "string" ? id : undefined;
});

function copyConfig(src: LlmConfig): LlmConfig {
  return { ...src };
}

function closeMenu(): void {
  menuOpen.value = false;
}

function toggleMenu(): void {
  menuOpen.value = !menuOpen.value;
}

function openLlmDialog(): void {
  draft.value = copyConfig(llm.value);
  menuOpen.value = false;
  dialogOpen.value = true;
}

function closeDialog(): void {
  draft.value = copyConfig(llm.value);
  dialogOpen.value = false;
}

function saveDialog(): void {
  llm.value = copyConfig(draft.value);
  saveLlmConfig(llm.value);
  dialogOpen.value = false;
}

function onDocClick(event: MouseEvent): void {
  const root = menuRoot.value;
  if (root && !root.contains(event.target as Node)) {
    closeMenu();
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key !== "Escape") return;
  if (dialogOpen.value) {
    closeDialog();
    return;
  }
  closeMenu();
}

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
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onKeydown);
  healthy.value = await fetchHealth();
  try {
    algorithms.value = await listAlgorithms();
    expandCurrent();
  } catch {
    healthy.value = false;
  }
});

onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onKeydown);
});

watch(
  () => route.params.id,
  () => expandCurrent(),
);
</script>
