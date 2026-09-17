<template>
  <div class="shell">
    <aside class="side">
      <router-link class="brand" to="/">
        <span>中达瑞和 × AI 团队</span>
        <strong>按层赋能</strong>
      </router-link>
      <nav class="nav-group">
        <p>处理层案例</p>
        <router-link
          v-for="row in layers"
          :key="row.id"
          :to="'/layer/' + row.id"
          :class="{ on: currentId === row.id }"
        >
          {{ row.level }} {{ row.title }}
        </router-link>
      </nav>
      <p v-if="catalogError" class="side-err">{{ catalogError }}</p>
    </aside>
    <div class="main">
      <header class="hero">
        <div>
          <p class="kicker">传统流水线 vs LLM · 不算公式</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <p class="hero-meta">独立站点 · 单算法解读请用 5173</p>
        <div class="llm-menu" ref="menuRoot">
          <button class="llm-trigger" type="button" :data-on="savedOn" @click="toggleMenu">
            大模型配置
            <span>{{ savedOn ? "已启用" : "未启用" }}</span>
          </button>
          <div v-if="menuOpen" class="llm-panel" role="dialog" aria-label="大模型调试配置">
            <p class="step">大模型调试配置</p>
            <p class="detail">
              点保存后才会用于各层「运行本层演示」。密钥只存在本机浏览器，不写仓库。
            </p>
            <label class="llm-on">
              <input v-model="draft.enabled" type="checkbox" />
              启用真实大模型
            </label>
            <div class="llm-grid">
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
            <p class="meta">默认 DeepSeek：https://api.deepseek.com · deepseek-chat。</p>
            <div class="llm-actions">
              <button class="ghost" type="button" @click="closeMenu">取消</button>
              <button class="go" type="button" @click="saveMenu">保存</button>
            </div>
          </div>
        </div>
      </header>
      <div v-if="!healthy" class="banner warn">无法连接 127.0.0.1:28800。请先启动算法服务。</div>
      <router-view v-slot="{ Component, route: viewRoute }">
        <component
          :is="Component"
          :healthy="healthy"
          :id="typeof viewRoute.params.id === 'string' ? viewRoute.params.id : ''"
        />
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
/** 左侧四层目录，右侧首页或一层对照。 */
import { computed, onMounted, onUnmounted, provide, ref } from "vue";
import { useRoute } from "vue-router";
import { fetchAideHealth, fetchLayers } from "./api";
import { loadLlmConfig, saveLlmConfig, type LlmConfig } from "./llmConfig";
import { LLM_CONFIG_KEY } from "./llmKey";
import type { LayerSummary } from "./types";

const healthy = ref(true);
const layers = ref<LayerSummary[]>([]);
const catalogError = ref("");
const llm = ref(loadLlmConfig());
const draft = ref<LlmConfig>({ ...llm.value });
const menuOpen = ref(false);
const menuRoot = ref<HTMLElement | null>(null);
const route = useRoute();

provide(LLM_CONFIG_KEY, llm);

const savedOn = computed(() => llm.value.enabled && !!llm.value.apiKey.trim());

function copyConfig(src: LlmConfig): LlmConfig {
  return { ...src };
}

function openMenu(): void {
  draft.value = copyConfig(llm.value);
  menuOpen.value = true;
}

function closeMenu(): void {
  draft.value = copyConfig(llm.value);
  menuOpen.value = false;
}

function toggleMenu(): void {
  if (menuOpen.value) {
    closeMenu();
  } else {
    openMenu();
  }
}

function saveMenu(): void {
  llm.value = copyConfig(draft.value);
  saveLlmConfig(llm.value);
  menuOpen.value = false;
}

function onDocClick(event: MouseEvent): void {
  const root = menuRoot.value;
  if (root && !root.contains(event.target as Node)) {
    closeMenu();
  }
}

const currentId = computed(() => (typeof route.params.id === "string" ? route.params.id : ""));
const pageTitle = computed(() => {
  const hit = layers.value.find((row) => row.id === currentId.value);
  return hit ? `${hit.level} ${hit.title}` : "处理层案例";
});

async function ping(): Promise<void> {
  healthy.value = await fetchAideHealth();
}

async function loadCatalog(): Promise<void> {
  catalogError.value = "";
  try {
    layers.value = await fetchLayers();
  } catch {
    catalogError.value = "层目录未加载";
    layers.value = [];
  }
}

onMounted(() => {
  void ping();
  void loadCatalog();
  document.addEventListener("click", onDocClick);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
});
</script>
