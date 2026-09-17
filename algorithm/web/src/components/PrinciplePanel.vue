<template>
  <div v-if="doc" class="pr">
    <div class="pr-hero">
      <div>
        <p class="kicker">算法定义</p>
        <h3>{{ doc.summary?.definition || doc.purpose }}</h3>
        <p class="pr-why">{{ doc.summary?.value || doc.why }}</p>
      </div>
      <div class="pr-summary-grid">
        <div><span>关键输入</span><strong>{{ doc.summary?.keyInput || doc.inputs[0]?.meaning || "待补充" }}</strong></div>
        <div><span>主要输出</span><strong>{{ doc.summary?.keyOutput || doc.outputs[0]?.meaning || "待补充" }}</strong></div>
        <div class="pr-summary-limit"><span>关键限制</span><strong>{{ doc.summary?.keyLimit || doc.industryGap }}</strong></div>
      </div>
    </div>

    <section>
      <h4>问题背景</h4>
      <ul class="pr-list">
        <li v-for="item in doc.background" :key="item">{{ item }}</li>
      </ul>
    </section>

    <section>
      <h4>原理依据与核心公式</h4>
      <p v-if="formulaTakeaway" class="pr-takeaway">
        <span class="pr-takeaway-kicker">一句话理解</span>
        <mark>{{ formulaTakeaway }}</mark>
      </p>
      <p class="pr-why">{{ doc.why }}</p>
      <ol v-if="doc.formulaItems?.length" class="pr-formula-list">
        <li v-for="item in doc.formulaItems" :key="item.name" class="pr-formula">
          <p class="pr-formula-name">{{ item.name }}</p>
          <p class="pr-eq">{{ item.eq }}</p>
          <p class="pr-fn">{{ item.note }}</p>
        </li>
      </ol>
      <div v-else class="pr-formula">
        <p class="pr-eq">{{ doc.formula }}</p>
        <p v-if="formulaNote" class="pr-fn">{{ formulaNote }}</p>
      </div>
      <div v-if="formulaProcess" class="pr-formula-flow">
        <p class="pr-formula-flow-kicker">处理过程</p>
        <PrincipleViz :viz="formulaProcess" />
      </div>
      <aside v-if="doc.formulaTogether" class="pr-together">
        <p class="pr-together-kicker">特别说明</p>
        <p>{{ doc.formulaTogether }}</p>
      </aside>
    </section>

    <section v-if="doc.scenarioCases?.length">
      <h4>场景使用案例</h4>
      <ol class="pr-scenario-list">
        <li v-for="item in doc.scenarioCases" :key="item.title">
          <strong>{{ item.title }}</strong>
          <p>{{ item.body }}</p>
        </li>
      </ol>
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
        <h4>输入说明</h4>
        <ul>
          <li v-for="row in doc.inputs" :key="row.name">
            <code class="mono">{{ row.name }}</code>
            <span>{{ row.meaning }}</span>
          </li>
        </ul>
      </section>
      <section>
        <h4>输出说明</h4>
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
        <summary>验证要点</summary>
        <ul class="pr-check"><li v-for="c in doc.checks" :key="c">{{ c }}</li></ul>
      </details>
    </div>
  </div>
  <div v-else class="empty">暂无该算法的原理页。</div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import PrincipleViz from "./PrincipleViz.vue";
import { getPrinciple } from "../principles";
import { FORMULA_PROCESSES } from "../principles/formulaProcesses";
import { FORMULA_TAKEAWAYS } from "../principles/formulaTakeaways";

const props = defineProps<{ algorithmId: string }>();
const doc = computed(() => getPrinciple(props.algorithmId));
const formulaNote = computed(
  () => doc.value?.formulaNote || doc.value?.summary?.keyLimit || "",
);
const formulaProcess = computed(() => {
  const current = doc.value;
  if (!current) return undefined;
  return current.formulaProcess ?? FORMULA_PROCESSES[current.id];
});
const formulaTakeaway = computed(() => {
  const current = doc.value;
  if (!current) return "";
  return current.formulaTakeaway ?? FORMULA_TAKEAWAYS[current.id] ?? "";
});
</script>
