<template>
  <section v-if="terms.length" class="abbr-box" :class="{ compact }">
    <table>
      <caption>名词对照</caption>
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
  <section v-else class="abbr-box">
    <table>
      <caption>名词对照</caption>
    </table>
    <p class="src-note">本页正文没有需要对照的字母简称。</p>
  </section>
</template>

<script setup lang="ts">
import type { Term } from "../glossary";

defineProps<{
  terms: Term[];
  compact?: boolean;
}>();
</script>
