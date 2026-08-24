<template>
  <form class="run-form" @submit.prevent="execute">
    <ol class="run-steps" aria-label="运行演示四步流程">
      <li><span>1</span><strong>选择数据</strong><small>加载示例或上传自有文件</small></li>
      <li><span>2</span><strong>检查条件</strong><small>核对格式、单位与字段要求</small></li>
      <li><span>3</span><strong>设置并执行</strong><small>确认参数后启动算法</small></li>
      <li><span>4</span><strong>解读结果</strong><small>检查输出与质量指标</small></li>
    </ol>
    <div class="run-toolbar">
      <button class="btn gold" type="button" :disabled="running" @click="loadSample">
        加载示例数据
      </button>
      <button class="btn ghost" type="button" :disabled="running" @click="clearCustom">
        清空为自定义
      </button>
      <p class="run-mode" :class="{ on: source === 'sample' }">
        当前：{{ sourceLabel }}
      </p>
    </div>
    <p class="run-desc">
      点「加载示例数据」会填入下列字段并预览文件内容，不会马上计算。不点则可自行选文件、改参数，再点执行。
      <strong>示例默认参数只适用于内置示例文件，不可直接照搬到其他传感器或数据。</strong>
    </p>

    <fieldset v-if="fileFields.length" class="form-section">
      <legend>输入文件</legend>
      <div v-for="f in fileFields" :key="f.name" class="form-field form-field-file">
        <div class="form-label-row">
          <span class="form-zh">{{ fieldTitle(f) }}</span>
          <code class="mono form-key">{{ f.name }}</code>
          <span class="form-type">{{ f.type }} · {{ fileKindLabel(f.type) }}</span>
          <span v-if="f.required" class="form-req">必填</span>
          <span v-else class="form-opt">可选</span>
        </div>
        <p class="form-help">{{ f.description }}</p>
        <div class="form-facts">
          <span v-if="f.unit">单位：{{ f.unit }}</span>
          <span v-if="f.range">范围：{{ f.range }}</span>
          <span v-if="fieldDefault(f) !== ''">默认值：{{ fieldDefault(f) }}</span>
        </div>
        <label class="file-card">
          <span class="file-kicker">{{ source === "sample" && !pickedName(f.name) ? "示例文件" : "选择本地文件" }}</span>
          <span class="file-name">{{ displayFileName(f) }}</span>
          <input
            type="file"
            :accept="fileAccept(f.type)"
            @change="onPickFile($event, f.name === 'file2' ? 'file2' : 'file')"
          />
        </label>
        <div v-if="source === 'sample' && sampleAsset(f.name)" class="form-file-vis">
          <VisPanel
            :title="`示例 · ${fileFieldTitle(f.name)}`"
            :asset="sampleAsset(f.name)"
            :algorithm-id="algo.id"
          />
        </div>
        <details v-if="hasProfessionalDetails(f)" class="form-details">
          <summary>详细说明</summary>
          <p v-if="f.defaultReason"><strong>默认依据：</strong>{{ f.defaultReason }}</p>
          <p v-if="f.selectionGuide"><strong>选择方法：</strong>{{ f.selectionGuide }}</p>
          <p v-if="f.effect"><strong>配置影响：</strong>{{ f.effect }}</p>
          <p v-if="f.risk" class="risk"><strong>误配风险：</strong>{{ f.risk }}</p>
          <p v-if="f.example"><strong>示例：</strong><code class="mono">{{ f.example }}</code></p>
        </details>
      </div>
    </fieldset>

    <fieldset v-if="paramFields.length" class="form-section">
      <legend>算法参数</legend>
      <div class="form-grid">
        <div
          v-for="f in paramFields"
          :key="f.name"
          class="form-field"
          :class="{ 'span-2': paramWidget(algo.id, f) === 'json' }"
        >
          <div class="form-label-row">
            <span class="form-zh">{{ fieldTitle(f) }}</span>
            <code class="mono form-key">{{ f.name }}</code>
            <span class="form-type">{{ f.type }}</span>
            <span v-if="f.required" class="form-req">必填</span>
            <span v-else class="form-opt">可选</span>
          </div>
          <p class="form-help">{{ f.description }}</p>
          <div class="form-facts">
            <span>单位：{{ f.unit || "未标注" }}</span>
            <span>范围：{{ f.range || "未标注" }}</span>
            <span>默认值：{{ fieldDefault(f) || "无" }}</span>
          </div>

          <select
            v-if="paramWidget(algo.id, f) === 'select'"
            class="form-control"
            :aria-label="fieldTitle(f)"
            :value="paramValues[paramKey(f.name)] ?? ''"
            @change="onTextInput(f, $event)"
          >
            <option value="">请选择</option>
            <option v-for="opt in selectOptions(algo.id, paramKey(f.name))" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>

          <label v-else-if="paramWidget(algo.id, f) === 'bool'" class="form-check">
            <input
              type="checkbox"
              :aria-label="fieldTitle(f)"
              :checked="paramValues[paramKey(f.name)] === 'true'"
              @change="onBoolInput(f, $event)"
            />
            启用
          </label>

          <input
            v-else-if="paramWidget(algo.id, f) === 'number'"
            class="form-control"
            type="number"
            :aria-label="fieldTitle(f)"
            :step="f.type === 'int' ? '1' : 'any'"
            :placeholder="placeholderOf(f)"
            :value="paramValues[paramKey(f.name)] ?? ''"
            @input="onTextInput(f, $event)"
          />

          <textarea
            v-else-if="paramWidget(algo.id, f) === 'json'"
            class="form-control form-json"
            :aria-label="fieldTitle(f)"
            spellcheck="false"
            :placeholder="placeholderOf(f)"
            :value="paramValues[paramKey(f.name)] ?? ''"
            @input="onTextInput(f, $event)"
          />

          <input
            v-else
            class="form-control"
            type="text"
            :aria-label="fieldTitle(f)"
            :placeholder="placeholderOf(f)"
            :value="paramValues[paramKey(f.name)] ?? ''"
            @input="onTextInput(f, $event)"
          />
          <details v-if="hasProfessionalDetails(f)" class="form-details">
            <summary>详细说明</summary>
            <p v-if="f.defaultReason"><strong>默认依据：</strong>{{ f.defaultReason }}</p>
            <p v-if="f.selectionGuide"><strong>选择方法：</strong>{{ f.selectionGuide }}</p>
            <p v-if="f.effect"><strong>调参影响：</strong>{{ f.effect }}</p>
            <p v-if="f.risk" class="risk"><strong>误配风险：</strong>{{ f.risk }}</p>
            <p v-if="f.example"><strong>示例：</strong><code class="mono">{{ f.example }}</code></p>
          </details>
        </div>
      </div>
    </fieldset>

    <div class="form-actions">
      <button class="btn" type="submit" :disabled="running">
        {{ running ? "正在执行…" : "执行" }}
      </button>
      <span v-if="source === 'sample'" class="form-hint">将使用内置示例文件 + 当前表单参数。</span>
      <span v-else class="form-hint">将使用你选择的文件 + 当前表单参数。</span>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import VisPanel from "./VisPanel.vue";
import { runConsole } from "../api";
import {
  fileAccept,
  fileFieldTitle,
  fileKindLabel,
  isFileField,
  isParamField,
  paramKey,
  paramWidget,
  parseFormParams,
  selectOptions,
  stringifyParam,
} from "../runForm";
import type { AlgorithmCard, FieldRow, RunResult, TestdataHttp } from "../types";

const props = defineProps<{
  algo: AlgorithmCard;
}>();

const emit = defineEmits<{
  result: [value: RunResult];
}>();

const running = ref(false);
const source = ref<"empty" | "sample" | "custom">("empty");
const file = ref<File | null>(null);
const file2 = ref<File | null>(null);
const paramValues = reactive<Record<string, string>>({});

const fileFields = computed(() => props.algo.fields.inputs.filter(isFileField));
const paramFields = computed(() => props.algo.fields.inputs.filter(isParamField));

const sourceLabel = computed(() => {
  if (source.value === "sample") return "已加载示例，可改参数后执行";
  if (source.value === "custom") return "自定义数据";
  return "未选择数据（请加载示例或自行选文件）";
});

function fieldTitle(field: FieldRow): string {
  if (field.label) return field.label;
  if (isFileField(field)) return fileFieldTitle(field.name);
  const desc = field.description.split("，")[0] || field.description;
  return desc || paramKey(field.name);
}

function fieldDefault(field: FieldRow): string {
  if (field.default !== undefined) return stringifyParam(field.default);
  if (!isParamField(field)) return "";
  return stringifyParam(props.algo.testdata.params?.[paramKey(field.name)]);
}

function hasProfessionalDetails(field: FieldRow): boolean {
  return Boolean(field.defaultReason || field.selectionGuide || field.effect || field.risk || field.example);
}

function placeholderOf(field: FieldRow): string {
  const value = fieldDefault(field);
  return value ? `默认 ${value}` : "";
}

function pickedName(which: string): string {
  if (which === "file2") return file2.value?.name || "";
  return file.value?.name || "";
}

function displayFileName(field: FieldRow): string {
  const picked = pickedName(field.name);
  if (picked) return picked;
  if (source.value === "sample") {
    const sample = field.name === "file2" ? props.algo.testdata.file2 : props.algo.testdata.file;
    return sample || "示例文件";
  }
  return "请选择文件";
}

function sampleAsset(name: string): TestdataHttp | null {
  const http = props.algo.testdata_http;
  if (!http) return null;
  return name === "file2" ? http.file2 ?? null : http.file ?? null;
}

function setParam(field: FieldRow, value: string) {
  paramValues[paramKey(field.name)] = value;
}

function onTextInput(field: FieldRow, ev: Event) {
  const el = ev.target as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
  setParam(field, el.value);
}

function onBoolInput(field: FieldRow, ev: Event) {
  const el = ev.target as HTMLInputElement;
  setParam(field, el.checked ? "true" : "false");
}

function resetParams(fillSample: boolean) {
  for (const key of Object.keys(paramValues)) delete paramValues[key];
  if (!fillSample) return;
  for (const field of paramFields.value) {
    const key = paramKey(field.name);
    paramValues[key] = stringifyParam(props.algo.testdata.params?.[key]);
  }
}

function loadSample() {
  source.value = "sample";
  file.value = null;
  file2.value = null;
  resetParams(true);
}

function clearCustom() {
  source.value = "empty";
  file.value = null;
  file2.value = null;
  resetParams(false);
}

function onPickFile(ev: Event, which: "file" | "file2") {
  const input = ev.target as HTMLInputElement;
  const picked = input.files?.[0] || null;
  if (which === "file2") file2.value = picked;
  else file.value = picked;
  source.value = "custom";
}

async function execute() {
  if (source.value !== "sample") {
    const missingFiles = fileFields.value
      .filter((field) => field.required)
      .filter((field) => (field.name === "file2" ? !file2.value : !file.value));
    if (missingFiles.length) {
      const names = missingFiles.map(fieldTitle).join("、");
      emit("result", { success: false, message: `请先加载示例数据，或选择必填文件：${names}。` });
      return;
    }
  }
  let params: Record<string, unknown>;
  try {
    params = parseFormParams(paramFields.value, paramValues);
  } catch (e) {
    emit("result", { success: false, message: e instanceof Error ? e.message : "参数格式错误" });
    return;
  }
  running.value = true;
  try {
    const useTestdata = source.value === "sample";
    const result = await runConsole({
      id: props.algo.id,
      useTestdata,
      file: useTestdata ? null : file.value,
      file2: useTestdata ? null : file2.value,
      params: JSON.stringify(params),
    });
    emit("result", result);
  } catch (e) {
    emit("result", { success: false, message: e instanceof Error ? e.message : "失败" });
  } finally {
    running.value = false;
  }
}

watch(
  () => props.algo.id,
  () => {
    source.value = "empty";
    file.value = null;
    file2.value = null;
    resetParams(false);
  },
  { immediate: true },
);
</script>
