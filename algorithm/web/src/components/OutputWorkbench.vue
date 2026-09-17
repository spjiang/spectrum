<template>
  <section class="output-workbench" aria-label="输出分析工作台">
    <header class="workbench-summary">
      <h3>{{ algo.title }} 主要产物</h3>
      <p>{{ algo.output_summary.what }}</p>
      <p class="workbench-caution">{{ algo.output_summary.caution }}</p>
      <p v-if="!hasRun" class="workbench-hint">尚未执行。运行后显示接口返回。</p>
      <p v-else-if="!runOk" class="workbench-hint">本次执行未成功。仍列出返回字段，不生成虚假质量结论。</p>
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
        <p v-if="!apiPayload" class="workbench-hint">尚未执行，没有算法服务返回。</p>
        <template v-else>
          <section
            v-for="group in apiGroups"
            :key="group.id"
            class="workbench-kv-group"
          >
            <h4>{{ group.label }}</h4>
            <table class="workbench-kv">
              <thead>
                <tr>
                  <th>字段</th>
                  <th>键</th>
                  <th>值</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in group.fields" :key="`raw-${item.path}`">
                  <td>{{ fieldTitle(item.path, knowledgeOf(item.path)) }}</td>
                  <td><code class="mono">{{ item.path }}</code></td>
                  <td>
                    <code
                      v-if="isInlineApiValue(item.value)"
                      class="mono workbench-kv-value"
                    >{{ displayFieldValue(item.value) }}</code>
                    <pre
                      v-else
                      class="workbench-kv-block"
                    >{{ displayStructuredValue(item.value) }}</pre>
                  </td>
                </tr>
              </tbody>
            </table>
          </section>
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
      <p v-else-if="!interpretedFields.length" class="workbench-hint">本次返回没有 data / files 产物字段。</p>
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
          <div class="workbench-card-aside">
            <code class="mono workbench-kv-value">{{ field.display }}</code>
            <span
              v-if="field.help.source === 'pending'"
              class="workbench-status unknown"
            >说明待补充</span>
            <template v-else-if="field.status">
              <span class="workbench-status" :class="field.status">{{ statusLabel(field.status) }}</span>
              <p class="workbench-status-why">{{ statusExplain(field.status, field.row) }}</p>
            </template>
          </div>
        </header>

        <div
          v-if="showsFieldVis(field)"
          class="field-vis"
          :data-kind="field.visKind"
        >
          <template v-if="field.domain">
            <div class="num-axis" :aria-label="`${field.path} 数值轴`">
              <span>{{ field.domain.min }}</span>
              <div class="num-bar">
                <i :style="{ left: `${field.domainPct}%` }" />
              </div>
              <span>{{ field.domain.max }}</span>
            </div>
            <p class="field-vis-caption">当前值 {{ field.display }}</p>
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
            <p v-if="field.fileAsset" class="workbench-hint">预览使用控制台派生的 files_http，不是 files 中的原始路径。</p>
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
          <pre v-else class="workbench-kv-block">{{ field.display }}</pre>
        </div>

        <p class="workbench-field-help">{{ field.help.text }}</p>
        <dl v-if="field.row" class="field-meta">
          <div v-if="field.row.format"><dt>格式</dt><dd>{{ field.row.format }}</dd></div>
          <div v-if="field.row.unit"><dt>单位</dt><dd>{{ field.row.unit }}</dd></div>
          <div v-if="field.row.range"><dt>范围</dt><dd>{{ field.row.range }}</dd></div>
          <div v-if="field.row.conditional"><dt>条件</dt><dd>{{ field.row.conditional }}</dd></div>
        </dl>
        <details v-if="field.row" class="workbench-more">
          <summary>补充说明</summary>
          <p><strong>效果：</strong>{{ field.row.effect }}</p>
          <p><strong>字段含义：</strong>{{ field.row.businessMeaning }}</p>
          <p><strong>解读：</strong>{{ field.row.interpretation }}</p>
        </details>
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
              <div v-if="hasRun" class="workbench-card-aside">
                <span class="workbench-status" :class="rowStatus(row)">{{ statusLabel(rowStatus(row)) }}</span>
                <p class="workbench-status-why">{{ statusExplain(rowStatus(row), row) }}</p>
              </div>
            </header>
            <p class="workbench-api-line">
              <span class="kicker">返回值</span>
              <strong>{{ hasRun ? displayFieldValue(resolveOutputValue(row, result)) : "尚未执行" }}</strong>
            </p>
            <p class="workbench-field-help">{{ row.description }}</p>
            <dl class="field-meta">
              <div v-if="row.unit"><dt>单位</dt><dd>{{ row.unit }}</dd></div>
              <div v-if="row.range"><dt>范围</dt><dd>{{ row.range }}</dd></div>
              <div v-if="row.qualityRule?.basis"><dt>判定依据</dt><dd>{{ row.qualityRule.basis }}</dd></div>
            </dl>
            <details class="workbench-more">
              <summary>补充说明</summary>
              <p><strong>效果：</strong>{{ row.effect }}</p>
              <p><strong>字段含义：</strong>{{ row.businessMeaning }}</p>
              <p><strong>解读：</strong>{{ row.interpretation }}</p>
            </details>
          </article>
        </div>
      </section>

      <section class="analysis-section">
        <h4>质量检查</h4>
        <dl class="workbench-status-legend">
          <div>
            <dt>符合门槛</dt>
            <dd>返回值落在知识库登记的可计算范围内。</dd>
          </div>
          <div>
            <dt>未设门槛</dt>
            <dd>该字段没有自动阈值，需按说明人工核对。</dd>
          </div>
          <div>
            <dt>超出门槛</dt>
            <dd>返回值越出登记范围。</dd>
          </div>
          <div>
            <dt>未产生</dt>
            <dd>条件输出本次没有写出。</dd>
          </div>
        </dl>
        <p v-if="!hasRun" class="workbench-hint">尚未执行，无法对照门槛。</p>
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
                <p class="workbench-status-why">{{ statusExplain(rowStatus(row), row) }}</p>
                <p><strong>检查方法：</strong>{{ row.qualityCheck }}</p>
                <ul v-if="row.abnormalSigns?.length">
                  <li v-for="sign in row.abnormalSigns" :key="sign">{{ sign }}</li>
                </ul>
                <p v-if="row.qualityRule">
                  <strong>登记门槛：</strong>{{ formatQualityThreshold(row.qualityRule) }}
                  · {{ row.qualityRule.basis }}
                </p>
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
  displayStructuredValue,
  domainPercent,
  evaluateOutputStatus,
  fieldHelp,
  fieldTitle,
  fieldVisKind,
  flattenApiFields,
  formatQualityThreshold,
  groupApiFields,
  isInlineApiValue,
  isProductApiPath,
  knowledgeRowForPath,
  numericDomain,
  originalApiPayload,
  resolveOutputValue,
  statusExplain,
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
const apiGroups = computed(() => groupApiFields(apiFields.value));
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
  const fields = apiFields.value.filter((item) => isProductApiPath(item.path) && item.path !== "data" && item.path !== "files");
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

/** 标量已在标题行展示，解读页只保留轴、栅格、文件和结构体 */
function showsFieldVis(field: InterpretedField): boolean {
  if (field.domain || field.shape || field.fileAsset) return true;
  return field.visKind === "file" || field.visKind === "array" || field.visKind === "json";
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
