<template>
  <section class="card llm-board">
    <p class="step">大模型这一次 · 先看这里</p>
    <h2>{{ didTitle }}</h2>
    <p class="did">{{ didText }}</p>
    <button class="go" type="button" :disabled="running || !healthy" @click="$emit('start')">
      {{ running ? "正在跑…" : run ? "再跑一次" : "跑一次，看输入和输出" }}
    </button>
    <p v-if="error" class="banner warn inner">{{ error }}</p>

    <div v-if="!run" class="empty-io">
      还没有跑。点按钮后，<strong>左边是发给模型的原文</strong>，<strong>右边是模型吐出来的原文</strong>（没开密钥则右边是模板，并标明「模型没被调用」）。
    </div>

    <div v-else class="io">
      <article>
        <p class="io-kicker">输入了什么</p>
        <p class="badge" :data-on="used">{{ used ? "已发给模型" : sent ? "已发给模型，输出被丢掉" : "已打包，没有发出去" }}</p>
        <p class="hook">没有照片、没有 GeoTIFF。只有文字和数字。</p>
        <table v-if="evidenceRows.length" class="io-table">
          <thead>
            <tr>
              <th>图</th>
              <th>最小</th>
              <th>最大</th>
              <th>平均</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in evidenceRows" :key="row.id">
              <td>{{ row.id }}</td>
              <td>{{ row.min }}</td>
              <td>{{ row.max }}</td>
              <td>{{ row.mean }}</td>
            </tr>
          </tbody>
        </table>
        <details class="io-details">
          <summary>看发给模型的原文（系统提示 + JSON）</summary>
          <p class="sub">系统提示</p>
          <pre class="prompt">{{ run.prompt?.system || "（无）" }}</pre>
          <p class="sub">用户 JSON（输入本体）</p>
          <pre class="prompt">{{ prettyUser }}</pre>
        </details>
      </article>
      <article class="out">
        <p class="io-kicker">输出了什么</p>
        <p class="badge" :data-on="sent && used">{{ outputBadge }}</p>
        <h3>{{ run.ai.headline }}</h3>
        <MarkdownBody :text="run.ai.markdown" />
        <details v-if="used && run.templateAi" class="io-details">
          <summary>对照：没走模型时的模板</summary>
          <p class="sub">{{ run.templateAi.headline }}</p>
          <MarkdownBody :text="run.templateAi.markdown" />
        </details>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
/** 把这一次大模型的输入原文、输出原文、有没有被调用摊开。 */
import { computed } from "vue";
import MarkdownBody from "./MarkdownBody.vue";
import type { LayerRun } from "../types";

const props = defineProps<{
  run: LayerRun | null;
  running: boolean;
  healthy: boolean;
  error: string;
}>();

defineEmits<{ start: [] }>();

const used = computed(() => Boolean(props.run?.llm.used));
const sent = computed(() => Boolean(props.run?.llm.used || (props.run && props.run.llm.reason !== "no_key" && props.run.prompt)));

const didTitle = computed(() => {
  if (!props.run) return "大模型还没上场";
  if (props.run.llm.used) return "大模型读了左边 JSON，写出了右边中文";
  if (props.run.llm.reason === "no_key") return "大模型没有被调用";
  return "大模型被调用了，但输出被丢掉";
});

const didText = computed(() => {
  if (!props.run) {
    return "它不选图、不算 NDVI/NDRE。上场时只做一件事：读输入 JSON，改写成中文说明。开密钥才会真的发出去。";
  }
  if (props.run.llm.used) {
    const model = props.run.llm.model || "已配置模型";
    return `这一次用了 ${model}。它没有看影像，也没有改主图。输出就是右边这一栏。`;
  }
  if (props.run.llm.reason === "no_key") {
    return "顶栏未启用密钥。输入已在左边打包好，但没有发给任何模型。右边是规则模板，不是模型写的。";
  }
  const why =
    props.run.llm.reason === "invalid"
      ? "输出不合规（例如写了公斤/亩）"
      : props.run.llm.reason === "timeout"
        ? "模型超时"
        : props.run.llm.reason === "http_error"
          ? "模型请求失败"
          : props.run.llm.reason;
  return `模型有过一次返回，但 ${why}，整段丢掉。右边现在是模板。`;
});

const outputBadge = computed(() => {
  if (!props.run) return "";
  if (props.run.llm.used) return "模型原文";
  if (props.run.llm.reason === "no_key") return "模板 · 模型没被调用";
  return "模板 · 模型输出已丢弃";
});

const prettyUser = computed(() => {
  const raw = props.run?.prompt?.user || "";
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return raw || "（无）";
  }
});

const evidenceRows = computed(() => {
  const raw = props.run?.prompt?.user || "";
  try {
    const parsed = JSON.parse(raw) as {
      evidence?: {
        demoAlgorithmId?: string;
        results?: Array<{ algorithmId?: string; min?: number; max?: number; mean?: number }>;
        stats?: { min?: number; max?: number; mean?: number };
      };
    };
    const ev = parsed.evidence || {};
    const rows = ev.results || [];
    if (rows.length) {
      return rows
        .filter((row) => row.algorithmId)
        .map((row) => ({
          id: String(row.algorithmId),
          min: fmt(row.min),
          max: fmt(row.max),
          mean: fmt(row.mean),
        }));
    }
    if (ev.stats && ev.demoAlgorithmId) {
      return [
        {
          id: String(ev.demoAlgorithmId),
          min: fmt(ev.stats.min),
          max: fmt(ev.stats.max),
          mean: fmt(ev.stats.mean),
        },
      ];
    }
    return [];
  } catch {
    return [];
  }
});

function fmt(n: number | undefined): string {
  return typeof n === "number" && Number.isFinite(n) ? n.toFixed(3) : "—";
}
</script>
