<template>
  <section v-if="terms.length" class="abbr-box" :class="{ compact }">
    <h4 v-if="!compact">名词对照</h4>
    <p v-if="!compact" class="abbr-lead">标题和原理里的简称，英文全称与中文译名如下。</p>
    <table>
      <thead>
        <tr>
          <th>简称</th>
          <th>英文全称</th>
          <th>中文</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in terms" :key="t.abbr">
          <td class="mono">{{ t.abbr }}</td>
          <td>{{ t.en }}</td>
          <td>{{ t.zh }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import type { Term } from "../glossary";

defineProps<{
  terms: Term[];
  compact?: boolean;
}>();
</script>
