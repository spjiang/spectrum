<template>
  <div class="md-body" v-html="html"></div>
</template>

<script setup lang="ts">
/** 渲染大模型 Markdown 结论。 */
import { computed } from "vue";
import { renderMarkdown } from "../markdown";

const props = defineProps<{ text: string }>();
const html = computed(() => renderMarkdown(props.text || ""));
</script>

<style scoped>
.md-body {
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--ink);
  overflow-wrap: anywhere;
}

.md-body :deep(p) {
  margin: 0 0 0.7em;
}

.md-body :deep(p:last-child) {
  margin-bottom: 0;
}

.md-body :deep(h1),
.md-body :deep(h2),
.md-body :deep(h3) {
  margin: 0.4em 0 0.5em;
  font-size: 15px;
  font-weight: 650;
  line-height: 1.4;
}

.md-body :deep(ul),
.md-body :deep(ol) {
  margin: 0 0 0.7em;
  padding-left: 1.3em;
}

.md-body :deep(li) {
  margin: 0.2em 0;
}

.md-body :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
  background: #eef3f6;
  padding: 0.1em 0.35em;
  border-radius: 4px;
}

.md-body :deep(pre) {
  margin: 0 0 0.7em;
  padding: 10px 12px;
  background: #102428;
  color: #d7e2e6;
  border-radius: 8px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.5;
}

.md-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.md-body :deep(blockquote) {
  margin: 0 0 0.7em;
  padding: 0 0 0 12px;
  border-left: 3px solid var(--gold, #c9a227);
  color: var(--ink-soft);
}

.md-body :deep(a) {
  color: var(--forest);
}
</style>
