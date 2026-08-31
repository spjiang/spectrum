<template>
  <section class="output-workbench" aria-label="输出分析工作台">
    <header class="workbench-summary">
      <p class="kicker">知识库说明</p>
      <h3>{{ algo.title }} 主要产物</h3>
      <p>{{ algo.output_summary.what }}</p>
      <p><strong>业务判断：</strong>{{ algo.output_summary.value }}</p>
      <p class="workbench-caution"><strong>使用边界：</strong>{{ algo.output_summary.caution }}</p>
      <p class="workbench-hint">
        「原始返回」按字段从上到下展示算法服务信封。
        「字段解读」对同一批字段做可视化与说明。
        「综合分析」合并核心指标、质量检查与下游应用。
        files_http 与 job_id 仅用于页面预览，不属于算法原始返回。
      </p>
      <p v-if="!hasRun" class="workbench-hint">尚未执行。运行后第一个标签显示原始信封；此前仅能查看预期产物说明。</p>
      <p v-else-if="!runOk" class="workbench-hint">本次执行未成功，原始返回中仍保留信封字段，不生成虚假质量结论。</p>
    </header>

    <nav class="workbench-tabs" role="tablist" aria-label="输出分析分类">
      <button
        v-for="item in tabs"
        :id="`workbench-tab-${item.id}`"
        :key="item.id"
        type="button"
        role="tab"
        :class="{ on: tab === item.id }"
        :aria-selected="tab === item.id"
        :aria-controls="`workbench-panel-${item.id}`"
        @click="tab = item.id"
      >
        {{ item.label }}
      </button>
    </nav>

    <div
      v-show="tab === 'api'"
      id="workbench-panel-api"
      class="workbench-panel workbench-panel-stack"
      role="tabpanel"
      aria-labelledby="workbench-tab-api"
    >
      <article class="workbench-card workbench-api-card">
        <header>
          <div>
            <strong>原始接口返回</strong>
            <code class="mono">{{ algo.endpoint }}</code>
          </div>
        </header>
        <p v-if="!apiPayload" class="workbench-hint">尚未执行，没有算法服务返回。运行后将按字段从上到下展示。</p>
        <template v-else>
          <p>算法服务原始字段仅包含 success、algorithm_id、algorithm、implemented、message、data、files。以下按返回顺序逐项展开。</p>
          <ol class="workbench-field-list">
            <li v-for="item in apiFields" :key="`raw-${item.path}`" class="workbench-field">
              <div class="workbench-field-head">
                <strong>{{ fieldTitle(item.path, knowledgeOf(item.path)) }}</strong>
                <code class="mono">{{ item.path }}</code>
              </div>
              <pre class="data workbench-field-value">{{ displayFieldValue(item.value) }}</pre>
            </li>
          </ol>
          <details class="workbench-json-details">
            <summary>完整 JSON</summary>
            <pre class="data workbench-api-json">{{ JSON.stringify(apiPayload, null, 2) }}</pre>
          </details>
        </template>
      </article>
    </div>

    <div
      v-show="tab === 'fields'"
      id="workbench-panel-fields"
      class="workbench-panel workbench-panel-stack"
      role="tabpanel"
      aria-labelledby="workbench-tab-fields"
    >
      <p v-if="!apiPayload" class="workbench-hint">尚未执行，无法对返回字段做可视化解读。</p>
      <article
        v-for="field in interpretedFields"
        :key="`vis-${field.path}`"
        class="workbench-card"
        :class="{ pending: field.help.source === 'pending' }"
      >
        <header>
          <div>
            <strong>{{ field.title }}</strong>
            <code class="mono">{{ field.path }}</code>
          </div>
          <span
            v-if="field.help.source === 'pending'"
            class="workbench-status unknown"
          >说明待补充</span>
          <span
            v-else-if="field.status"
            class="workbench-status"
            :class="field.status"
          >{{ statusLabel(field.status) }}</span>
        </header>

        <p class="workbench-api-line">
          <span class="kicker">接口返回值</span>
          <strong>{{ field.display }}</strong>
        </p>

        <div class="field-vis" :data-kind="field.visKind">
          <template v-if="field.visKind === 'boolean'">
            <span class="bool-chip" :class="{ on: field.value === true }">true</span>
            <span class="bool-chip" :class="{ on: field.value === false }">false</span>
          </template>
          <template v-else-if="field.domain">
            <div class="num-axis" :aria-label="`${field.path} 数值轴`">
              <span>{{ field.domain.min }}</span>
              <div class="num-bar">
                <i :style="{ left: `${field.domainPct}%` }" />
              </div>
              <span>{{ field.domain.max }}</span>
            </div>
            <p class="field-vis-caption">标记位置为当前返回值 {{ field.display }}</p>
          </template>
          <template v-else-if="field.shape">
            <div class="shape-vis">
              <div
                class="shape-box"
                :style="{ aspectRatio: `${field.shape.cols} / ${field.shape.rows}` }"
              />
              <p>{{ field.shape.rows }} × {{ field.shape.cols }} 像元</p>
            </div>
          </template>
          <template v-else-if="field.visKind === 'file'">
            <p v-if="field.fileAsset" class="workbench-hint">下方预览使用控制台派生的 files_http，不是 files 中的原始路径。</p>
            <VisPanel
              v-if="field.fileAsset"
              :title="field.title"
              :asset="field.fileAsset"
              :algorithm-id="algo.id"
            />
            <p v-else class="workbench-hint">已返回本地路径，当前没有可预览的派生资源。</p>
          </template>
          <template v-else-if="field.arrayItems">
            <ol class="array-vis">
              <li v-for="entry in field.arrayItems" :key="`${field.path}-${entry.index}`">
                <span>{{ entry.index }}</span>
                <code>{{ entry.text }}</code>
              </li>
            </ol>
          </template>
          <p v-else-if="field.visKind === 'number'" class="num-plain">
            <span>{{ field.display }}</span>
          </p>
          <p v-else-if="field.visKind === 'empty'" class="workbench-hint">该字段为空。</p>
          <pre v-else class="data workbench-field-value">{{ field.display }}</pre>
        </div>

        <div class="workbench-knowledge">
          <p class="kicker">{{ helpSourceLabel(field.help.source) }}</p>
          <p>{{ field.help.text }}</p>
          <template v-if="field.row">
            <dl class="field-meta">
              <div v-if="field.row.format"><dt>格式</dt><dd>{{ field.row.format }}</dd></div>
              <div v-if="field.row.unit"><dt>单位</dt><dd>{{ field.row.unit }}</dd></div>
              <div v-if="field.row.range"><dt>范围</dt><dd>{{ field.row.range }}</dd></div>
              <div v-if="field.row.conditional"><dt>条件</dt><dd>{{ field.row.conditional }}</dd></div>
            </dl>
            <p><strong>效果：</strong>{{ field.row.effect }}</p>
            <p><strong>业务含义：</strong>{{ field.row.businessMeaning }}</p>
            <p><strong>如何解读：</strong>{{ field.row.interpretation }}</p>
          </template>
        </div>
        <details v-if="field.row?.bands?.length">
          <summary>波段结构</summary>
          <ul>
            <li
              v-for="(band, index) in field.row.bands"
              :key="`${field.path}-${bandIndex(band, index)}`"
            >
              波段 {{ bandIndex(band, index) }} · {{ bandTitle(band) }}
              <span v-if="band.unit">（{{ band.unit }}）</span>
              ：{{ bandMeaning(band) }}
            </li>
          </ul>
        </details>
      </article>
    </div>

    <div
      v-show="tab === 'analysis'"
      id="workbench-panel-analysis"
      class="workbench-panel"
      role="tabpanel"
      aria-labelledby="workbench-tab-analysis"
    >
      <section class="analysis-section">
        <h4>核心指标</h4>
        <div class="analysis-grid">
          <article v-for="row in metricRows" :key="row.name" class="workbench-card">
            <header>
              <div>
                <strong>{{ row.label }}</strong>
                <code class="mono">{{ row.name }}</code>
              </div>
              <span
                v-if="hasRun"
                class="workbench-status"
                :class="rowStatus(row)"
              >{{ statusLabel(rowStatus(row)) }}</span>
            </header>
            <p class="workbench-api-line">
              <span class="kicker">接口返回值</span>
              <code class="mono">{{ row.name }}</code>
              <strong>{{ hasRun ? displayFieldValue(resolveOutputValue(row, result)) : "尚未执行" }}</strong>
            </p>
            <div class="workbench-knowledge">
              <p class="kicker">知识库说明</p>
              <p>{{ row.description }}</p>
              <dl class="field-meta">
                <div v-if="row.unit"><dt>单位</dt><dd>{{ row.unit }}</dd></div>
                <div v-if="row.range"><dt>范围</dt><dd>{{ row.range }}</dd></div>
                <div v-if="row.qualityRule?.basis"><dt>判定依据</dt><dd>{{ row.qualityRule.basis }}</dd></div>
              </dl>
              <p><strong>效果：</strong>{{ row.effect }}</p>
              <p><strong>业务含义：</strong>{{ row.businessMeaning }}</p>
              <p><strong>如何解读：</strong>{{ row.interpretation }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="analysis-section">
        <h4>质量检查</h4>
        <p v-if="!hasRun" class="workbench-hint">执行后将依据结构化规则评估，当前不可判定。</p>
        <template v-else>
          <section v-for="group in qualityGroups" :key="group.status" class="workbench-quality-group">
            <h5>
              <span class="workbench-status" :class="group.status">{{ statusLabel(group.status) }}</span>
              {{ group.rows.length }} 项
            </h5>
            <div class="analysis-grid">
              <article v-for="row in group.rows" :key="row.name" class="workbench-card">
                <header>
                  <div>
                    <strong>{{ row.label }}</strong>
                    <code class="mono">{{ row.name }}</code>
                  </div>
                </header>
                <p><strong>检查方法：</strong>{{ row.qualityCheck }}</p>
                <ul v-if="row.abnormalSigns?.length">
                  <li v-for="sign in row.abnormalSigns" :key="sign">{{ sign }}</li>
                </ul>
                <p v-if="row.qualityRule?.basis"><strong>规则依据：</strong>{{ row.qualityRule.basis }}</p>
                <p v-else class="workbench-hint">没有可机器判定的统一阈值，状态保持为不可判定。</p>
              </article>
            </div>
          </section>
        </template>
      </section>

      <section class="analysis-section">
        <h4>下游应用</h4>
        <div class="analysis-grid">
          <article v-for="row in allRows" :key="`down-${row.name}`" class="workbench-card">
            <header>
              <div>
                <strong>{{ row.label }}</strong>
                <code class="mono">{{ row.name }}</code>
              </div>
            </header>
            <p><strong>下游用途：</strong>{{ row.downstreamUse }}</p>
            <p v-if="row.misuseWarning" class="workbench-caution"><strong>禁止误用：</strong>{{ row.misuseWarning }}</p>
            <p v-if="row.relatedOutputs?.length">
              <strong>关联输出：</strong>{{ row.relatedOutputs.join("、") }}
            </p>
          </article>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import VisPanel from "./VisPanel.vue";
import {
  asShape,
  asTestdataHttp,
  displayFieldValue,
  domainPercent,
  evaluateOutputStatus,
  fieldHelp,
  fieldTitle,
  fieldVisKind,
  flattenApiFields,
  knowledgeRowForPath,
  numericDomain,
  originalApiPayload,
  resolveOutputValue,
  statusLabel,
} from "../outputWorkbench";
import type { AlgorithmCard, OutputBand, OutputFieldRow, OutputStatus, RunResult, TestdataHttp } from "../types";
import type {
  FieldHelpSource,
  FieldVisKind,
  FlattenedApiField,
  NumericDomain,
} from "../outputWorkbench";

const props = defineProps<{
  algo: AlgorithmCard;
  result: RunResult | null;
}>();

type WorkbenchTab = "api" | "fields" | "analysis";

const tabs: Array<{ id: WorkbenchTab; label: string }> = [
  { id: "api", label: "原始返回" },
  { id: "fields", label: "字段解读" },
  { id: "analysis", label: "综合分析" },
];

const tab = ref<WorkbenchTab>("api");

const hasRun = computed(() => Boolean(props.result));
const runOk = computed(() => props.result?.success === true);
const apiPayload = computed(() => originalApiPayload(props.result));
const apiFields = computed(() => flattenApiFields(apiPayload.value));
const allRows = computed(() => props.algo.fields.outputs);
const metricRows = computed(() => allRows.value.filter((row) => row.parent === "data"));

type InterpretedField = {
  path: string;
  value: unknown;
  title: string;
  visKind: FieldVisKind;
  help: { source: FieldHelpSource; text: string };
  row?: OutputFieldRow;
  status: OutputStatus | null;
  domain: NumericDomain | null;
  domainPct: number;
  shape: { rows: number; cols: number } | null;
  fileAsset: TestdataHttp | null;
  display: string;
  arrayItems: Array<{ index: number; text: string }> | null;
};

const interpretedFields = computed<InterpretedField[]>(() => {
  const fields = apiFields.value;
  return fields.map((item: FlattenedApiField) => {
    const row = knowledgeRowForPath(allRows.value, item.path);
    const domain =
      typeof item.value === "number" && Number.isFinite(item.value)
        ? numericDomain(item.path, item.value, row, fields)
        : null;
    return {
      path: item.path,
      value: item.value,
      title: fieldTitle(item.path, row),
      visKind: fieldVisKind(item.path, item.value),
      help: fieldHelp(item.path, row),
      row,
      status: row && hasRun.value ? evaluateOutputStatus(row, resolveOutputValue(row, props.result)) : null,
      domain,
      domainPct: domain ? domainPercent(domain) : 0,
      shape: asShape(item.value),
      fileAsset: fileAssetOf(item.path),
      display: displayFieldValue(item.value),
      arrayItems: Array.isArray(item.value)
        ? item.value.map((entry, index) => ({ index, text: displayFieldValue(entry) }))
        : null,
    };
  });
});

watch(
  () => props.result,
  (value) => {
    if (value) tab.value = "api";
  },
);

const STATUS_ORDER: OutputStatus[] = ["attention", "unknown", "not-produced", "pass"];

const qualityGroups = computed(() => {
  const groups: Array<{ status: OutputStatus; rows: OutputFieldRow[] }> = [];
  for (const status of STATUS_ORDER) {
    const rows = allRows.value.filter((row) => rowStatus(row) === status);
    if (rows.length) groups.push({ status, rows });
  }
  return groups;
});

function knowledgeOf(path: string): OutputFieldRow | undefined {
  return knowledgeRowForPath(allRows.value, path);
}

function helpSourceLabel(source: FieldHelpSource): string {
  if (source === "envelope") return "信封说明";
  if (source === "knowledge") return "知识库说明";
  return "说明待补充";
}

function rowStatus(row: OutputFieldRow): OutputStatus {
  if (!hasRun.value) return "unknown";
  return evaluateOutputStatus(row, resolveOutputValue(row, props.result));
}

function fileAssetOf(path: string): TestdataHttp | null {
  if (!path.startsWith("files.")) return null;
  const key = path.slice("files.".length);
  return asTestdataHttp(props.result?.files_http?.[key]);
}

function bandIndex(band: OutputBand, index: number): number {
  return band.index ?? index;
}

function bandTitle(band: OutputBand): string {
  return band.label || band.name || `波段 ${band.index ?? ""}`.trim();
}

function bandMeaning(band: OutputBand): string {
  return band.meaning || band.description || "";
}
</script>
