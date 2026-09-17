<template>
  <div class="ai-x">
    <p class="kicker">AI 探索</p>
    <p class="lede">
      大模型不重算、不看影像。「赋能分析」说明如何提高本次运行、如何接到应用；「赋能效果」用左右对照看实际加了什么。
    </p>

    <div v-if="loadError" class="banner-box warn">{{ loadError }}</div>
    <template v-else-if="doc">
      <nav class="page-tabs ai-tabs" aria-label="赋能页切换">
        <button type="button" :class="{ on: pane === 'analysis' }" @click="pane = 'analysis'">
          大模型赋能分析
        </button>
        <button type="button" :class="{ on: pane === 'effect' }" @click="pane = 'effect'">
          大模型赋能效果
        </button>
      </nav>

      <div v-if="pane === 'effect'" class="prompt-bar">
        <button class="btn ghost" type="button" @click="openPrompt">编辑提示词</button>
        <span class="detail">{{ promptSaved ? "已用本机保存的提示词，对照时会发给大模型。" : "当前为知识库默认提示词。" }}</span>
      </div>

      <section v-if="pane === 'analysis'" class="box">
        <ol v-if="doc.llmLeverage?.sections?.length" class="places">
          <li v-for="(sec, i) in doc.llmLeverage.sections" :key="sec.id">
            <span class="n">{{ i + 1 }}</span>
            <div>
              <strong>{{ sec.label }}</strong>
              <p>{{ sec.text }}</p>
            </div>
          </li>
        </ol>
        <ol v-else-if="doc.llmLeverage" class="places">
          <li v-for="(dim, i) in doc.llmLeverage.dims" :key="dim.id">
            <span class="n">{{ i + 1 }}</span>
            <div>
              <strong>{{ dim.label }}</strong>
              <p>大模型会{{ dim.why }}</p>
            </div>
          </li>
        </ol>
        <p class="detail">效果不在这里打分。切到「大模型赋能效果」，左边是数字、右边是大模型写的，对照即可见。</p>
      </section>

      <section v-else class="box">
        <ol class="flow">
          <li :class="{ on: algoOk }">① 用「运行演示」最新返回</li>
          <li :class="{ on: phase === 'llm' || phase === 'done' }">② 左边放数字，右边交给大模型</li>
          <li :class="{ on: phase === 'done' }">③ 对照看出加了什么</li>
        </ol>
        <div v-if="!result" class="banner-box warn">
          须先在「运行演示」跑通算法，再看赋能效果。
          <button class="btn gold jump" type="button" @click="emit('gotoRun')">去运行演示</button>
        </div>
        <div v-else-if="!algoOk" class="banner-box warn">
          最近一次算法未成功{{ algoMessage ? "：" + algoMessage : "" }}。须重新运行后再测。
          <button class="btn gold jump" type="button" @click="emit('gotoRun')">去运行演示</button>
        </div>
        <template v-else>
          <button class="btn gold" type="button" :disabled="busy" @click="submitLatest">
            {{ busy ? "正在生成对照…" : "对照本次返回" }}
          </button>
          <div v-if="runError" class="banner-box warn">{{ runError }}</div>
          <div class="compare" v-if="interpret || algoOk">
            <article class="side-off">
              <p class="sub">没有大模型时你看到的</p>
              <dl v-if="rawRows.length" class="raw">
                <div v-for="row in rawRows" :key="row.name">
                  <dt>{{ row.name }}</dt>
                  <dd>{{ row.value }}</dd>
                </div>
              </dl>
              <p v-else class="hook">本次返回没有可展示的短字段。</p>
              <p class="hook">数字本身不会告诉你字段含义、公式限制，也不会拦住说错。</p>
            </article>
            <article class="side-on">
              <p class="sub">有大模型时加上去的</p>
              <template v-if="interpret?.llm.used">
                <p class="quality ok-line">本次已生效（{{ interpret.llm.model || "已配置模型" }}）</p>
                <MarkdownBody :text="interpret.runComment" />
              </template>
              <template v-else-if="interpret?.llm.fallback">
                <p class="quality">本次未生效：{{ reasonLabel(interpret.llm.reason) }}{{ interpret.llm.detail ? " · " + interpret.llm.detail : "" }}</p>
                <p class="hook">没有大模型时系统只能套规则，赋能差异看不出来。</p>
                <p v-if="interpret.templateComment" class="hook muted">规则会写成：{{ interpret.templateComment }}</p>
              </template>
              <p v-else-if="busy" class="hook">正在把返回交给大模型…</p>
              <p v-else class="hook">点「对照本次返回」后，右侧会出现大模型写的字段含义、方法限制和误用拦截。</p>
            </article>
          </div>
          <p v-if="interpret?.llm.used" class="banner-box ok">
            对照结果：左侧只有返回数字；右侧多了字段含义、方法限制和误用拦截。这就是本算法上的赋能。
          </p>
          <p v-else-if="interpret?.llm.fallback" class="banner-box muted">
            本次没有大模型参与，左右没有赋能差异。启用密钥后再测。
          </p>
        </template>
      </section>

      <Teleport to="body">
        <div v-if="promptOpen" class="prompt-mask" @click.self="closePrompt">
          <div class="prompt-modal" role="dialog" aria-modal="true" aria-label="编辑提示词">
            <header>
              <h3>编辑提示词</h3>
              <button class="btn ghost" type="button" @click="closePrompt">关闭</button>
            </header>
            <p class="detail">
              只存在本机浏览器。保存后再点「对照本次返回」，即可看到改词对大模型输出的影响。
            </p>
            <label>
              系统提示词
              <textarea v-model="draftSystem" rows="10" spellcheck="false" />
            </label>
            <label>
              用户提示词
              <textarea v-model="draftUser" rows="10" spellcheck="false" />
            </label>
            <p class="detail">用户提示词留空时，对照会按本次算法返回自动生成。</p>
            <footer>
              <button class="btn ghost" type="button" @click="restorePrompt">恢复默认</button>
              <span class="prompt-spacer" />
              <button class="btn ghost" type="button" @click="closePrompt">取消</button>
              <button class="btn gold" type="button" @click="savePrompt">保存</button>
              <button v-if="algoOk" class="btn gold" type="button" :disabled="busy" @click="saveAndRun">
                保存并对照
              </button>
            </footer>
          </div>
        </div>
      </Teleport>
    </template>
    <p v-else class="detail">正在加载算法说明…</p>
  </div>
</template>

<script setup lang="ts">
/** L3 AI 探索：说明赋能位置与效果，再用对照测试看出来。 */
import { computed, inject, onUnmounted, ref, watch } from "vue";
import { fetchAideKnowledge, interpretAideAlgorithm } from "../api";
import { defaultLlmConfig } from "../llmConfig";
import { LLM_CONFIG_KEY } from "../llmKey";
import { clearPromptOverride, loadPromptOverride, savePromptOverride } from "../promptStore";
import type { AideAlgoRun, AideKnowledge, AlgorithmCard, RunResult } from "../types";
import MarkdownBody from "./MarkdownBody.vue";

const props = defineProps<{ algo: AlgorithmCard; result: RunResult | null }>();
const emit = defineEmits<{ gotoRun: [] }>();
const llm = inject(LLM_CONFIG_KEY, ref(defaultLlmConfig()));

const doc = ref<AideKnowledge | null>(null);
const loadError = ref("");
const phase = ref<"idle" | "llm" | "done">("idle");
const runError = ref("");
const interpret = ref<AideAlgoRun | null>(null);
const pane = ref<"analysis" | "effect">("analysis");
const promptOpen = ref(false);
const draftSystem = ref("");
const draftUser = ref("");
const promptTick = ref(0);

const busy = computed(() => phase.value === "llm");
const algoOk = computed(() => Boolean(props.result?.success));
const algoMessage = computed(() => props.result?.message || "");
const rawRows = computed(() => scalarRows(props.result?.data));
const promptSaved = computed(() => {
  promptTick.value;
  return Boolean(loadPromptOverride(props.algo.id));
});

function formatScalar(raw: unknown): string | null {
  if (raw == null || Array.isArray(raw) || typeof raw === "object") return null;
  if (typeof raw === "number") {
    if (!Number.isFinite(raw)) return null;
    return Number.isInteger(raw) ? String(raw) : raw.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
  }
  if (typeof raw === "boolean") return raw ? "true" : "false";
  const text = String(raw).trim();
  if (!text || text.length > 80) return null;
  return text;
}

function scalarRows(data: Record<string, unknown> | undefined): { name: string; value: string }[] {
  if (!data) return [];
  const rows: { name: string; value: string }[] = [];
  for (const [name, raw] of Object.entries(data)) {
    const value = formatScalar(raw);
    if (value == null) continue;
    if (/preview|url|path|\.tif|\.png|\.npy/i.test(`${name}${value}`)) continue;
    rows.push({ name, value });
  }
  return rows.slice(0, 12);
}

function prettyJson(text: string): string {
  try {
    return JSON.stringify(JSON.parse(text), null, 2);
  } catch {
    return text;
  }
}

function defaultSystem(): string {
  return doc.value?.llmPrompt || "";
}

function defaultUser(): string {
  return prettyJson(interpret.value?.prompt?.user || "");
}

function openPrompt(): void {
  const saved = loadPromptOverride(props.algo.id);
  draftSystem.value = saved?.system || defaultSystem();
  draftUser.value = saved?.user || defaultUser();
  promptOpen.value = true;
}

function closePrompt(): void {
  promptOpen.value = false;
}

function savePrompt(): void {
  savePromptOverride(props.algo.id, {
    system: draftSystem.value,
    user: draftUser.value,
  });
  promptTick.value += 1;
  promptOpen.value = false;
}

function restorePrompt(): void {
  clearPromptOverride(props.algo.id);
  promptTick.value += 1;
  draftSystem.value = defaultSystem();
  draftUser.value = defaultUser();
}

async function saveAndRun(): Promise<void> {
  savePrompt();
  await submitLatest();
}

function onEscape(event: KeyboardEvent): void {
  if (event.key === "Escape" && promptOpen.value) closePrompt();
}

window.addEventListener("keydown", onEscape);
onUnmounted(() => window.removeEventListener("keydown", onEscape));

function reasonLabel(reason: string): string {
  const map: Record<string, string> = {
    no_key: "未启用或未填密钥",
    invalid: "模型输出不合规，已回退模板",
    plan_override_rejected: "模型试图改推其他算法，已丢弃",
    timeout: "模型超时",
    http_error: "模型接口失败",
    no_balance: "模型账户余额不足",
  };
  return map[reason] || reason;
}

async function load(): Promise<void> {
  loadError.value = "";
  doc.value = null;
  resetInterpret();
  if (!props.algo?.id) return;
  try {
    doc.value = await fetchAideKnowledge(props.algo.id);
  } catch (err) {
    loadError.value = err instanceof Error ? err.message : "无法加载该算法的解读知识";
  }
}

function resetInterpret(): void {
  phase.value = "idle";
  runError.value = "";
  interpret.value = null;
}

async function submitLatest(): Promise<void> {
  if (!props.result?.success) {
    runError.value = "须先运行算法获取结果";
    return;
  }
  runError.value = "";
  interpret.value = null;
  phase.value = "llm";
  try {
    interpret.value = await interpretAideAlgorithm(
      props.algo.id,
      props.result,
      llm.value,
      loadPromptOverride(props.algo.id) || undefined,
    );
    phase.value = "done";
  } catch (err) {
    runError.value = err instanceof Error ? err.message : "解读失败";
    phase.value = "idle";
  }
}

watch(
  () => props.algo.id,
  () => {
    pane.value = "analysis";
    promptOpen.value = false;
    void load();
  },
  { immediate: true },
);

watch(
  () => props.result?.job_id ?? props.result,
  () => {
    resetInterpret();
  },
);
</script>

<style scoped>
.ai-x {
  margin-top: 20px;
}

.ai-tabs {
  margin: 0 0 12px;
}

.prompt-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 16px;
  margin: -4px 0 12px;
}

.prompt-bar .detail {
  margin: 0;
}

.prompt-mask {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 24px;
  background: var(--overlay);
}

.prompt-modal {
  width: min(720px, 94vw);
  max-height: 90vh;
  overflow: auto;
  background: var(--paper-2);
  border: 1px solid var(--line);
  padding: 16px 18px 18px;
  box-shadow: 0 16px 40px rgba(22, 20, 16, 0.12);
}

.prompt-modal header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.prompt-modal h3 {
  margin: 0;
  font-size: 16px;
}

.prompt-modal label {
  display: block;
  margin-top: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--forest);
}

.prompt-modal textarea {
  display: block;
  width: 100%;
  margin-top: 6px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  background: #102428;
  color: #d7e2e6;
  border-radius: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.5;
  resize: vertical;
}

.prompt-modal footer {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 16px;
}

.prompt-spacer {
  flex: 1 1 auto;
}

.lede {
  margin: 8px 0 18px;
  color: var(--ink-soft);
  font-size: 14px;
  line-height: 1.6;
  max-width: 720px;
}

.places {
  margin: 12px 0 0;
  padding: 0;
  list-style: none;
}

.places li {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
  align-items: start;
  padding: 10px 0;
  border-top: 1px solid var(--line);
}

.places li:first-child {
  border-top: 0;
  padding-top: 0;
}

.places .n {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--forest);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  line-height: 28px;
  text-align: center;
}

.places strong {
  display: block;
  font-size: 14px;
}

.places p {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--ink-soft);
}

.box {
  background: var(--paper-2);
  border: 1px solid var(--line);
  padding: 16px 18px;
  margin-bottom: 12px;
}

.box h3 {
  margin: 6px 0 8px;
  font-size: 15px;
  font-weight: 600;
}

.step {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--forest);
}

.meta,
.detail {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--ink-soft);
}

.box ul {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.5;
}

.sub {
  margin: 10px 0 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--forest);
}

.sub.risk,
.risk-list {
  color: var(--warn);
}

.flow {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin: 10px 0 14px;
  padding: 0;
  list-style: none;
  font-size: 13px;
  color: var(--ink-soft);
}

.flow li.on {
  color: var(--forest);
  font-weight: 600;
}

.jump {
  display: inline-block;
  margin: 10px 0 0;
}

.banner-box {
  margin: 12px 0 0;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
}

.banner-box.warn {
  background: #fff1eb;
  color: var(--warn);
}

.banner-box.muted {
  background: #eef3f6;
  color: var(--ink-soft);
}

.banner-box.ok {
  background: #e8f6f3;
  color: var(--forest);
}

.demo img {
  width: 100%;
  max-height: 240px;
  object-fit: contain;
  background: #eef3f6;
  border-radius: 8px;
  margin-top: 12px;
}

.missing,
.stats {
  margin: 12px 0 0;
  font-size: 13px;
}

.quality {
  margin: 12px 0 0;
  font-size: 14px;
  font-weight: 600;
}

.quality[data-status="warn"] {
  color: var(--warn);
}

.compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.compare article {
  background: var(--paper);
  border-radius: 8px;
  padding: 10px 12px;
}

.side-off {
  border: 1px solid var(--line);
}

.side-on {
  border: 1px solid var(--forest);
}

.raw {
  display: grid;
  gap: 6px;
  margin: 8px 0 0;
}

.raw div {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  font-size: 13px;
}

.raw dt {
  color: var(--ink-soft);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}

.raw dd {
  margin: 0;
  font-variant-numeric: tabular-nums;
}

.ok-line {
  color: var(--forest);
}

.hook.muted {
  color: var(--ink-soft);
}

.hook {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 880px) {
  .compare {
    grid-template-columns: 1fr;
  }
}
</style>
