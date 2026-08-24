<template>
  <div class="page" v-if="algo">
    <div class="algo-head">
      <div>
        <h2>{{ algo.title }}</h2>
        <span class="pill">{{ groupTitle(algo.level) }}</span>
        <span class="pill quiet">{{ algo.level }}</span>
        <span class="pill quiet">{{ algo.method }}</span>
        <AbbrGlossary :terms="headTerms" compact />
        <p class="lede" style="margin: 12px 0 0">{{ purposeText }}</p>
        <div class="endpoint"><span>调用地址</span> <code class="mono">{{ algo.endpoint }}</code></div>
        <SourcePanel :algorithm-id="algo.id" />
      </div>
      <button class="btn ghost field-open" type="button" @click="openDrawer('inputs')">
        接口字段
      </button>
    </div>

    <nav class="page-tabs" aria-label="算法页面切换">
      <button type="button" :class="{ on: pageTab === 'principle' }" @click="pageTab = 'principle'">
        算法原理
      </button>
      <button type="button" :class="{ on: pageTab === 'run' }" @click="pageTab = 'run'">
        运行演示
      </button>
      <button type="button" :class="{ on: pageTab === 'product' }" @click="pageTab = 'product'">
        产品分析
      </button>
    </nav>

    <PrinciplePanel
      v-if="pageTab === 'principle'"
      :algorithm-id="algo.id"
      :level="algo.level"
      :method="algo.method"
    />
    <ProductPanel v-else-if="pageTab === 'product'" :algorithm-id="algo.id" />

    <template v-else>
    <div v-if="principle" class="run-intro">
      <section class="run-position">
        <p class="kicker">处理定位</p>
        <h3>{{ principle.summary?.definition || principle.purpose }}</h3>
        <p>{{ principle.purpose }}</p>
        <p class="run-value"><strong>业务价值：</strong>{{ principle.summary?.value || principle.why }}</p>
      </section>
      <section>
        <h4>使用前提</h4>
        <ul><li v-for="item in principle.prerequisites" :key="item">{{ item }}</li></ul>
      </section>
      <section>
        <h4>适用条件</h4>
        <ul><li v-for="item in principle.applicable" :key="item">{{ item }}</li></ul>
      </section>
      <section class="run-warning">
        <h4>不适用条件</h4>
        <ul><li v-for="item in principle.notApplicable" :key="item">{{ item }}</li></ul>
      </section>
      <section class="run-focus">
        <h4>演示重点</h4>
        <ol><li v-for="item in principle.demoFocus" :key="item">{{ item }}</li></ol>
      </section>
    </div>
    <div v-else class="cards">
      <div class="card">
        <h4>处理定位</h4>
        <p>该算法的结构化运行说明尚未补齐，请先依据接口字段与示例数据完成验证。</p>
      </div>
      <div class="card">
        <h4>使用边界</h4>
        <p>投入业务使用前，应核对输入数据级别、单位、波段与空间参考条件。</p>
      </div>
    </div>

    <div class="panel">
      <RunForm :algo="algo" @result="onRunResult" />
      <button
        v-if="result"
        class="status-line"
        type="button"
        :class="result.success ? 'status-ok' : 'status-bad'"
        @click="openDrawer('json')"
      >
        {{ result.success ? "执行成功" : "执行失败" }} · {{ result.message }}
        <span class="status-more">查看返回数据</span>
      </button>

      <div class="compare single">
        <div>
          <VisPanel
            v-for="item in outputAssets"
            :key="item.key"
            :title="`输出 · ${item.asset.name}`"
            :asset="item.asset"
            :algorithm-id="algo.id"
          />
          <div v-if="!outputAssets.length" class="vis-box">
            <h5>输出结果</h5>
            <div class="empty">尚未执行。加载示例或选择文件后点击「执行」，结果将在此展示。</div>
          </div>
        </div>
      </div>
    </div>
    </template>
    <Teleport to="body">
      <div v-if="drawerOpen" class="drawer-mask" @click="drawerOpen = false" />
      <aside class="drawer" :class="{ open: drawerOpen }" :aria-hidden="!drawerOpen">
        <header class="drawer-head">
          <div>
            <p class="kicker">字段说明</p>
            <h3>{{ algo.title }}</h3>
          </div>
          <button class="btn ghost" type="button" @click="drawerOpen = false">关闭</button>
        </header>
        <nav class="drawer-tabs">
          <button type="button" :class="{ on: drawerTab === 'inputs' }" @click="drawerTab = 'inputs'">
            输入字段
          </button>
          <button type="button" :class="{ on: drawerTab === 'outputs' }" @click="drawerTab = 'outputs'">
            输出字段
          </button>
          <button
            type="button"
            :class="{ on: drawerTab === 'json' }"
            :disabled="!result"
            @click="drawerTab = 'json'"
          >
            返回数据
          </button>
        </nav>
        <div class="drawer-body">
          <div v-if="drawerTab === 'inputs'" class="field-cards">
            <article v-for="f in algo.fields.inputs" :key="f.name" class="field-card">
              <header>
                <div><strong>{{ f.label || f.name }}</strong><code class="mono">{{ f.name }}</code></div>
                <span>{{ f.type }} · {{ f.required ? "必填" : "可选" }}</span>
              </header>
              <p>{{ f.description }}</p>
              <dl class="field-meta">
                <div v-if="f.format"><dt>格式</dt><dd>{{ f.format }}</dd></div>
                <div v-if="f.unit"><dt>单位</dt><dd>{{ f.unit }}</dd></div>
                <div v-if="f.range"><dt>范围</dt><dd>{{ f.range }}</dd></div>
                <div v-if="f.default !== undefined"><dt>默认值</dt><dd>{{ displayValue(f.default) }}</dd></div>
                <div v-if="f.example"><dt>示例</dt><dd>{{ f.example }}</dd></div>
                <div><dt>展示</dt><dd>{{ visZh(f.vis) }}</dd></div>
              </dl>
              <details v-if="hasFieldDetails(f)">
                <summary>专业说明</summary>
                <p v-if="f.defaultReason"><strong>默认依据：</strong>{{ f.defaultReason }}</p>
                <p v-if="f.selectionGuide"><strong>选择方法：</strong>{{ f.selectionGuide }}</p>
                <p v-if="f.effect"><strong>参数影响：</strong>{{ f.effect }}</p>
                <p v-if="f.risk" class="risk"><strong>误配风险：</strong>{{ f.risk }}</p>
              </details>
            </article>
          </div>
          <div v-else-if="drawerTab === 'outputs'" class="field-cards">
            <article v-for="f in algo.fields.outputs" :key="f.name" class="field-card">
              <header>
                <div><strong>{{ f.label || f.name }}</strong><code class="mono">{{ f.name }}</code></div>
                <span>{{ f.type }}</span>
              </header>
              <p>{{ f.description }}</p>
              <dl class="field-meta">
                <div v-if="f.format"><dt>格式</dt><dd>{{ f.format }}</dd></div>
                <div v-if="f.unit"><dt>单位</dt><dd>{{ f.unit }}</dd></div>
                <div v-if="f.range"><dt>合理范围</dt><dd>{{ f.range }}</dd></div>
                <div><dt>展示</dt><dd>{{ visZh(f.vis) }}</dd></div>
              </dl>
              <details v-if="f.qualityCheck || f.downstreamUse || f.selectionGuide">
                <summary>结果解释与用途</summary>
                <p v-if="f.selectionGuide"><strong>结果解读：</strong>{{ f.selectionGuide }}</p>
                <p v-if="f.qualityCheck"><strong>质量检查：</strong>{{ f.qualityCheck }}</p>
                <p v-if="f.downstreamUse"><strong>下游用途：</strong>{{ f.downstreamUse }}</p>
              </details>
            </article>
          </div>
          <pre v-else class="data">{{ JSON.stringify(result?.data || {}, null, 2) }}</pre>
        </div>
      </aside>
    </Teleport>
  </div>
  <div class="page" v-else-if="loadError">说明加载失败：{{ loadError }}</div>
  <div class="page" v-else>正在加载算法说明…</div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import VisPanel from "../components/VisPanel.vue";
import RunForm from "../components/RunForm.vue";
import PrinciplePanel from "../components/PrinciplePanel.vue";
import ProductPanel from "../components/ProductPanel.vue";
import AbbrGlossary from "../components/AbbrGlossary.vue";
import SourcePanel from "../components/SourcePanel.vue";
import { getAlgorithm } from "../api";
import { groupTitle } from "../levels";
import { termsForAlgorithm } from "../glossary";
import { getPrinciple } from "../principles";
import type { AlgorithmCard, FieldRow, RunResult } from "../types";

const props = defineProps<{ id: string }>();

const algo = ref<AlgorithmCard | null>(null);
const loadError = ref("");
const result = ref<RunResult | null>(null);
const drawerOpen = ref(false);
const drawerTab = ref<"inputs" | "outputs" | "json">("inputs");
const pageTab = ref<"principle" | "run" | "product">("principle");
const principle = computed(() => getPrinciple(props.id));

function visZh(vis: string): string {
  const map: Record<string, string> = {
    geojson_map: "地图",
    json_table: "表格",
    csv_track: "轨迹",
    csv_spectrum: "光谱",
    csv_table: "表格",
    raster_falsecolor: "假彩色",
    raster_index: "指数图",
    raster_class: "分类图",
    png: "图片",
    none: "—",
  };
  return map[vis] || vis;
}

function openDrawer(tab: "inputs" | "outputs" | "json") {
  drawerTab.value = tab;
  drawerOpen.value = true;
}

function displayValue(value: unknown): string {
  return typeof value === "string" ? value : JSON.stringify(value);
}

function hasFieldDetails(field: FieldRow): boolean {
  return Boolean(field.defaultReason || field.selectionGuide || field.effect || field.risk);
}

function withPeriod(text: string): string {
  const t = text.trim().replace(/[。；;]+$/g, "");
  return t ? `${t}。` : "";
}

const purposeText = computed(() => withPeriod(algo.value?.purpose || algo.value?.title || ""));

const headTerms = computed(() => {
  const a = algo.value;
  if (!a) return [];
  return termsForAlgorithm(a.id, a.title, a.method, a.purpose);
});

const outputAssets = computed(() => {
  const http = result.value?.files_http || {};
  return Object.entries(http).map(([key, asset]) => ({ key, asset }));
});

function onRunResult(value: RunResult) {
  result.value = value;
}

async function load() {
  loadError.value = "";
  algo.value = null;
  result.value = null;
  drawerOpen.value = false;
  drawerTab.value = "inputs";
  try {
    const item = await getAlgorithm(props.id);
    algo.value = item;
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : "未知错误";
  }
}

watch(
  () => props.id,
  () => {
    void load();
  },
  { immediate: true },
);
</script>
