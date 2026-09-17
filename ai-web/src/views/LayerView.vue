<template>
  <div class="layer-page">
    <div v-if="loadError" class="banner warn">{{ loadError }}</div>
    <template v-else-if="doc">
      <section class="card q-card">
        <p class="step">{{ doc.level }} · {{ doc.title }}</p>
        <h2>{{ doc.question }}</h2>
        <p class="hook">{{ leadText }}</p>
      </section>

      <LlmBoard :run="run" :running="running" :healthy="healthy" :error="runError" @start="start" />

      <section v-if="run?.results?.length || run?.demo" class="card">
        <p class="step">算法出的图 · 不进大模型</p>
        <div v-if="run.plan" class="plan-grid">
          <article class="plan primary">
            <strong>主图 {{ run.plan.primary.title }}</strong>
            <p>{{ run.plan.primary.reason }}</p>
          </article>
          <article class="plan">
            <strong>对照 {{ run.plan.contrast.title }}</strong>
            <p>{{ run.plan.contrast.reason }}</p>
          </article>
        </div>
        <div v-if="run.results?.length" class="result-grid">
          <article v-for="row in run.results" :key="row.algorithmId" class="result">
            <img v-if="row.previewUrl" :src="row.previewUrl" :alt="row.algorithmId + ' 预览'" />
            <div v-else class="missing">本图未算出{{ row.message ? "：" + row.message : "" }}</div>
            <p v-if="mapNote(row.algorithmId)" class="hook">{{ mapNote(row.algorithmId) }}</p>
            <p v-if="row.stats" class="stats">
              均值 {{ fmt(row.stats.mean) }} · 范围 {{ fmt(row.stats.min) }}～{{ fmt(row.stats.max) }}
            </p>
          </article>
        </div>
        <div v-else-if="run.demo" class="demo">
          <p class="sub">代表算法 {{ run.demo.algorithmId }}</p>
          <img v-if="run.demo.previewUrl" :src="run.demo.previewUrl" :alt="run.demo.algorithmId + ' 预览'" />
          <div v-else class="missing short">
            {{
              run.demo.success
                ? "本次以统计或报告为主，未出 PNG。"
                : "未产出预览" + (run.demo.message ? "：" + run.demo.message : "")
            }}
          </div>
          <ul v-if="demoFacts.length" class="fact-list">
            <li v-for="line in demoFacts" :key="line">{{ line }}</li>
          </ul>
        </div>
      </section>

      <details class="more">
        <summary>背景、对照和流程（可不看）</summary>
        <div v-if="doc.story?.length" class="story">
          <article v-for="beat in doc.story" :key="beat.title">
            <strong>{{ beat.title }}</strong>
            <p>{{ beat.text }}</p>
          </article>
        </div>
        <LlmFlow v-if="doc.id === 'l3'" />
        <section class="vs">
          <article class="card traditional">
            <p class="step">没有参谋时</p>
            <h3>{{ traditional.headline }}</h3>
            <ul>
              <li v-for="line in traditional.bullets" :key="line">{{ line }}</li>
            </ul>
          </article>
          <article class="card ai-col">
            <p class="step">规则模板（不是模型原文）</p>
            <h3>{{ doc.ai.headline }}</h3>
            <MarkdownBody :text="doc.ai.markdown" />
          </article>
        </section>
        <p class="foot">
          单算法解读请到
          <a href="http://127.0.0.1:5173">5173 算法控制台</a>
          。
        </p>
      </details>
    </template>
  </div>
</template>

<script setup lang="ts">
/** 一层只留问题、大模型输入输出、图；其余折进次要区。 */
import { computed, inject, onMounted, ref, watch } from "vue";
import { fetchLayer, runLayer } from "../api";
import LlmBoard from "../components/LlmBoard.vue";
import LlmFlow from "../components/LlmFlow.vue";
import MarkdownBody from "../components/MarkdownBody.vue";
import { defaultLlmConfig } from "../llmConfig";
import { LLM_CONFIG_KEY } from "../llmKey";
import type { LayerCase, LayerRun, LayerTraditional } from "../types";

const props = defineProps<{ id: string; healthy: boolean }>();
const llm = inject(LLM_CONFIG_KEY, ref(defaultLlmConfig()));

const doc = ref<LayerCase | null>(null);
const run = ref<LayerRun | null>(null);
const loadError = ref("");
const runError = ref("");
const running = ref(false);

const traditional = computed<LayerTraditional>(() => {
  return run.value?.traditional || doc.value?.traditional || { headline: "", bullets: [] };
});

const leadText = computed(() => {
  const first = doc.value?.story?.[0]?.text;
  return first || doc.value?.hook || "";
});

const demoFacts = computed(() => factsFromDemo(run.value?.demo?.data));

function mapNote(algorithmId: string): string {
  return doc.value?.resultNotes?.[algorithmId] || "";
}

function fmt(n: number): string {
  return n.toFixed(2);
}

function factsFromDemo(data: Record<string, unknown> | undefined): string[] {
  if (!data) return [];
  const prefer = ["passed", "suggest_refly", "saturated_ratio", "underexposed_ratio"];
  const lines: string[] = [];
  for (const key of prefer) {
    if (!(key in data)) continue;
    const value = data[key];
    if (value === null || typeof value === "object") continue;
    lines.push(`${key}：${String(value)}`);
  }
  return lines;
}

async function load(): Promise<void> {
  loadError.value = "";
  run.value = null;
  runError.value = "";
  try {
    doc.value = await fetchLayer(props.id);
  } catch (err) {
    doc.value = null;
    loadError.value = err instanceof Error ? err.message : "案例加载失败";
  }
}

async function start(): Promise<void> {
  runError.value = "";
  running.value = true;
  try {
    run.value = await runLayer(props.id, llm.value);
  } catch (err) {
    run.value = null;
    runError.value = err instanceof Error ? err.message : "运行失败";
  } finally {
    running.value = false;
  }
}

onMounted(() => {
  void load();
});

watch(
  () => props.id,
  () => {
    void load();
  },
);
</script>
