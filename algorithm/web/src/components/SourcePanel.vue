<template>
  <template v-if="view">
    <section class="src-box">
      <h4>核心主张</h4>
      <p v-if="view.method" class="src-method">本仓库方法：{{ view.method }}</p>
      <p v-if="view.gradeLabel" class="src-note">{{ view.gradeLabel }}</p>
      <ol v-if="view.claims.length" class="src-list">
        <li v-for="claim in view.claims" :key="claim.claimId">
          <p class="src-cite">
            <strong>{{ claim.title }}。</strong>{{ claim.text }}
          </p>
          <p class="src-summary">
            {{ claim.statusLabel }}<template v-if="claim.gradeLabel">。{{ claim.gradeLabel }}</template>
          </p>
          <ul v-if="claim.sources.length" class="src-claim-refs">
            <li v-for="source in claim.sources" :key="source.referenceId">
              {{ source.authors }} ({{ source.year }}). {{ source.title }}
              <a :href="source.url" target="_blank" rel="noopener noreferrer">原文链接</a>
            </li>
          </ul>
        </li>
      </ol>
      <p v-else class="src-note">本页暂无面向文献页的核心主张。</p>
    </section>

    <section class="src-box">
      <h4>参考文献</h4>
      <ol v-if="view.references.length" class="src-list">
        <li v-for="cite in view.references" :key="cite.referenceId">
          <p class="src-cite">
            {{ cite.authors }} ({{ cite.year }}). {{ cite.title }}. <em>{{ cite.venue }}</em>.
            <a :href="cite.url" target="_blank" rel="noopener noreferrer">原文链接</a>
          </p>
          <p class="src-summary">{{ cite.summary }}</p>
          <p class="src-note">支持主张：{{ supportedClaimLabel(cite) }}</p>
        </li>
      </ol>
      <p v-else class="src-note">本页暂无已绑定主张的参考文献。</p>
    </section>

    <section class="src-box">
      <h4>本仓库实现差异</h4>
      <ol v-if="view.implementationDiffs.length" class="src-diffs">
        <li v-for="(diff, i) in view.implementationDiffs" :key="i">{{ diff }}</li>
      </ol>
      <p v-else class="src-note">计算过程与文献公式一致，没有额外改写。</p>
    </section>
  </template>
  <section v-else class="src-box">
    <h4>算法文献</h4>
    <p class="src-note">本页暂未挂可打开的文献条目。原理与输出说明只引用已登记知识，不在此编造出处。</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getSourcePanelView } from "../sources";
import type { SourcePanelReferenceItem } from "../types";

const props = defineProps<{ algorithmId: string }>();
const view = computed(() => getSourcePanelView(props.algorithmId));

function supportedClaimLabel(cite: SourcePanelReferenceItem): string {
  return cite.supportedClaims
    .map((claim) => (claim.title ? `${claim.title}：${claim.text}` : claim.text))
    .join("；");
}
</script>
