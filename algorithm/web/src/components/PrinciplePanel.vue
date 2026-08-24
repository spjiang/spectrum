<template>
  <div v-if="doc" class="pr">
    <div class="pr-hero">
      <div>
        <p class="kicker">领导摘要 · 一句话定义</p>
        <h3>{{ doc.summary?.definition || doc.purpose }}</h3>
        <p class="pr-why">{{ doc.summary?.value || doc.why }}</p>
        <div class="pr-tags" aria-label="算法定位">
          <span>{{ level }}</span>
          <span v-if="method">{{ method }}</span>
        </div>
      </div>
      <div class="pr-summary-grid">
        <div><span>关键输入</span><strong>{{ doc.summary?.keyInput || doc.inputs[0]?.meaning || "待补充" }}</strong></div>
        <div><span>主要输出</span><strong>{{ doc.summary?.keyOutput || doc.outputs[0]?.meaning || "待补充" }}</strong></div>
        <div class="pr-summary-limit"><span>关键限制</span><strong>{{ doc.summary?.keyLimit || doc.industryGap }}</strong></div>
      </div>
    </div>

    <AbbrGlossary :terms="terms" />

    <section>
      <h4>问题背景</h4>
      <ul class="pr-list">
        <li v-for="item in doc.background" :key="item">{{ item }}</li>
      </ul>
    </section>

    <section>
      <h4>原理依据与核心公式</h4>
      <p class="pr-why">{{ doc.why }}</p>
      <div class="pr-formula">
        <p class="pr-eq">{{ doc.formula }}</p>
        <p v-if="doc.formulaNote" class="pr-fn">{{ doc.formulaNote }}</p>
      </div>
    </section>

    <section>
      <h4>数据前提</h4>
      <ul class="pr-list">
        <li v-for="item in doc.prerequisites" :key="item">{{ item }}</li>
      </ul>
    </section>

    <section class="pr-viz-wrap">
      <h4>原理示意</h4>
      <PrincipleViz :viz="doc.viz" />
    </section>

    <section>
      <h4>计算步骤</h4>
      <ol class="pr-steps">
        <li v-for="s in doc.steps" :key="s">{{ s }}</li>
      </ol>
    </section>

    <div class="pr-io">
      <section>
        <h4>输入要看懂什么</h4>
        <ul>
          <li v-for="row in doc.inputs" :key="row.name">
            <code class="mono">{{ row.name }}</code>
            <span>{{ row.meaning }}</span>
          </li>
        </ul>
      </section>
      <section>
        <h4>输出得到什么</h4>
        <ul>
          <li v-for="row in doc.outputs" :key="row.name">
            <code class="mono">{{ row.name }}</code>
            <span>{{ row.meaning }}</span>
          </li>
        </ul>
      </section>
    </div>

    <section>
      <h4>结果解读</h4>
      <ul class="pr-list">
        <li v-for="item in doc.resultInterpretation" :key="item">{{ item }}</li>
      </ul>
    </section>

    <div class="pr-details">
      <details>
        <summary>参数敏感性</summary>
        <article v-for="item in doc.parameterNotes" :key="item.name" class="pr-param-note">
          <h5><code class="mono">{{ item.name }}</code> · {{ item.role }}</h5>
          <p><strong>选择方法：</strong>{{ item.guidance }}</p>
          <p><strong>变化影响：</strong>{{ item.effect }}</p>
          <p class="risk"><strong>误配风险：</strong>{{ item.risk }}</p>
        </article>
      </details>
      <details>
        <summary>适用边界</summary>
        <div class="pr-boundary">
          <div>
            <h5>适用条件</h5>
            <ul class="pr-list"><li v-for="item in doc.applicable" :key="item">{{ item }}</li></ul>
          </div>
          <div>
            <h5>不适用条件</h5>
            <ul class="pr-list risk"><li v-for="item in doc.notApplicable" :key="item">{{ item }}</li></ul>
          </div>
        </div>
      </details>
      <details>
        <summary>误差与风险</summary>
        <ul class="pr-list risk"><li v-for="item in doc.risks" :key="item">{{ item }}</li></ul>
      </details>
      <details>
        <summary>上下游关系</summary>
        <div class="pr-boundary">
          <div><h5>上游依赖</h5><ul class="pr-list"><li v-for="item in doc.upstream" :key="item">{{ item }}</li></ul></div>
          <div><h5>下游用途</h5><ul class="pr-list"><li v-for="item in doc.downstream" :key="item">{{ item }}</li></ul></div>
        </div>
      </details>
      <details>
        <summary>本仓库实现与行业完整做法</summary>
        <p>{{ doc.industryGap }}</p>
      </details>
      <details>
        <summary>学习自检</summary>
        <ul class="pr-check"><li v-for="c in doc.checks" :key="c">{{ c }}</li></ul>
      </details>
    </div>
  </div>
  <div v-else class="empty">暂无该算法的原理页。</div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import PrincipleViz from "./PrincipleViz.vue";
import AbbrGlossary from "./AbbrGlossary.vue";
import { getPrinciple } from "../principles";
import { termsForAlgorithm } from "../glossary";

const props = defineProps<{ algorithmId: string; level: string; method?: string }>();
const doc = computed(() => getPrinciple(props.algorithmId));
const terms = computed(() => {
  const d = doc.value;
  if (!d) return termsForAlgorithm(props.algorithmId);
  return termsForAlgorithm(
    props.algorithmId,
    d.purpose,
    d.why,
    d.formula,
    d.formulaNote,
    d.industryGap,
    d.summary?.definition,
    d.summary?.value,
    ...(d.background || []),
    ...(d.prerequisites || []),
    ...(d.resultInterpretation || []),
    ...(d.applicable || []),
    ...(d.notApplicable || []),
    ...(d.risks || []),
    ...d.steps,
    ...d.inputs.map((r) => `${r.name} ${r.meaning}`),
    ...d.outputs.map((r) => `${r.name} ${r.meaning}`),
  );
});
</script>
