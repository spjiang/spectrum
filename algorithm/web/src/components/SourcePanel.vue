<template>
  <section v-if="src" class="src-box">
    <h4>算法来源</h4>
    <p class="src-method">本仓库方法：{{ src.method }}</p>
    <ol class="src-list">
      <li v-for="(c, i) in src.cites" :key="i">
        <span>{{ c.authors }} ({{ c.year }}). {{ c.title }}. <em>{{ c.venue }}</em>.</span>
        <a :href="c.url" target="_blank" rel="noopener noreferrer">原文链接</a>
      </li>
    </ol>
    <p class="src-note">{{ src.note }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getAlgoSource } from "../sources";

const props = defineProps<{ algorithmId: string }>();
const src = computed(() => getAlgoSource(props.algorithmId));
</script>
