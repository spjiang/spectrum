<template>
  <div class="page">
    <header class="hero">
      <div>
        <p class="kicker">中达瑞和 × AI 团队</p>
        <h1>L3 参谋 · 长势与氮素</h1>
      </div>
      <div class="hero-meta">
        <p>独立站点 · 不算图，只选型、解读、建议</p>
        <p>分类 / 水质同一编排器，本期不接</p>
      </div>
    </header>

    <div v-if="!healthy" class="banner warn">无法连接 127.0.0.1:28800。请先启动算法服务，再点开始参谋。</div>
    <div v-if="error" class="banner warn">{{ error }}</div>
    <div v-if="payload?.llm.fallback" class="banner muted">本次为规则叙事（大模型未改选型，文案走模板）。</div>

    <div class="toolbar">
      <button class="go" type="button" :disabled="loading || !healthy" @click="start">
        {{ loading ? "正在选型并出图…" : "开始参谋" }}
      </button>
    </div>

    <section class="card">
      <p class="step">① 问题</p>
      <h2>{{ question.title }}</h2>
      <p class="meta">
        作物：{{ question.crop }} · 冠层：{{ question.canopy }} · 相机：{{ question.sensor }}（7 通道，含 720/750 nm
        红边）· 任务：{{ question.task }}
      </p>
      <p class="hook">{{ question.hook }}</p>
    </section>

    <section v-if="payload" class="card">
      <p class="step">② 选型 · 规则权威，大模型只写理由</p>
      <h2>密冠层主看 NDRE，NDVI 只做对照</h2>
      <div class="plan-grid">
        <article class="plan primary">
          <strong>主跑 {{ payload.plan.primary.title }}</strong>
          <p>{{ payload.plan.primary.reason }}</p>
        </article>
        <article class="plan">
          <strong>对照 {{ payload.plan.contrast.title }}</strong>
          <p>{{ payload.plan.contrast.reason }}</p>
        </article>
        <article v-for="row in payload.plan.skipped" :key="row.algorithmId" class="plan skip">
          <strong>不跑 {{ row.title }}</strong>
          <p>{{ row.reason }}</p>
        </article>
      </div>
    </section>

    <section v-if="payload" class="card">
      <p class="step">③ 出图解释 · 调用现有算法 API，原始影像不进大模型</p>
      <div class="result-grid">
        <article v-for="row in payload.results" :key="row.algorithmId" class="result">
          <img v-if="row.previewUrl" :src="row.previewUrl" :alt="row.algorithmId + ' 预览'" />
          <div v-else class="missing">本图未算出{{ row.message ? "：" + row.message : "" }}</div>
          <p v-if="row.stats" class="stats">
            <strong>
              均值 {{ fmt(row.stats.mean) }} · 范围 {{ fmt(row.stats.min) }}～{{ fmt(row.stats.max) }}
            </strong>
          </p>
          <p class="detail">{{ row.quality.detail }}</p>
          <p class="quality" :data-status="row.quality.status">判断：{{ row.quality.label }}</p>
        </article>
      </div>
    </section>

    <section v-if="payload" class="advice">
      <p class="step light">④ 建议 · 辅助，不是处方</p>
      <h2>{{ payload.advice.headline }}</h2>
      <ul>
        <li v-for="(line, i) in payload.advice.bullets" :key="i">{{ line }}</li>
      </ul>
    </section>

    <footer class="foot">分类、水质可接同一编排器，本期不跑这些算法。</footer>
  </div>
</template>

<script setup lang="ts">
/** 一页四段：问题常驻，其余在一次参谋请求后填入。 */
import { onMounted, ref } from "vue";
import { defaultQuestion, fetchAideHealth, runAide } from "./api";
import type { AideQuestion, AideResponse } from "./types";

const healthy = ref(true);
const loading = ref(false);
const error = ref("");
const question = ref<AideQuestion>(defaultQuestion);
const payload = ref<AideResponse | null>(null);

function fmt(n: number): string {
  return n.toFixed(2);
}

async function ping(): Promise<void> {
  healthy.value = await fetchAideHealth();
}

async function start(): Promise<void> {
  error.value = "";
  loading.value = true;
  try {
    const data = await runAide();
    payload.value = data;
    question.value = data.question;
  } catch (err) {
    payload.value = null;
    error.value = err instanceof Error ? err.message : "运行失败";
    await ping();
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void ping();
});
</script>
