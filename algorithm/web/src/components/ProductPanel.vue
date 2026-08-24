<template>
  <div v-if="doc" class="pa">
    <div class="pa-hero">
      <div>
        <p class="kicker">面向中达瑞和合作</p>
        <h3>{{ doc.verdict }}</h3>
        <p class="pa-hook">{{ doc.hook }}</p>
      </div>
      <div class="pa-counts">
        <p class="kicker">本算法适配</p>
        <p class="pa-count-line">
          <strong>{{ counts.direct }}</strong> 直接 ·
          <strong>{{ counts.adapt }}</strong> 改编 ·
          <span class="pa-muted">{{ counts.no }} 不建议</span>
        </p>
        <p class="pa-links">
          <a :href="WAYHO_HOME" target="_blank" rel="noopener noreferrer">公司官网</a>
          <a :href="WAYHO_CATALOG" target="_blank" rel="noopener noreferrer">产品筛选</a>
        </p>
      </div>
    </div>

    <div class="pa-dims">
      <section>
        <h4>产品</h4>
        <p>{{ doc.product }}</p>
      </section>
      <section>
        <h4>业务</h4>
        <p>{{ doc.business }}</p>
      </section>
      <section>
        <h4>应用</h4>
        <p>{{ doc.application }}</p>
      </section>
    </div>

    <section class="pa-table-wrap">
      <div class="pa-table-head">
        <h4>适用产品</h4>
        <label class="pa-toggle">
          <input v-model="showNo" type="checkbox" />
          显示不建议的型号
        </label>
      </div>
      <table class="pa-table">
        <thead>
          <tr>
            <th>匹配</th>
            <th>型号</th>
            <th>系列</th>
            <th>波段 / 方式</th>
            <th>理由</th>
            <th>链接</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in visibleRows" :key="row.product.id">
            <td>
              <span class="pa-fit" :data-level="row.level">{{ fitLabel(row.level) }}</span>
            </td>
            <td>
              <a class="pa-ext" :href="row.product.url" target="_blank" rel="noopener noreferrer">{{
                row.product.name
              }}</a>
            </td>
            <td>{{ row.product.series }}</td>
            <td>{{ row.product.band }} · {{ row.product.mode }}</td>
            <td>{{ row.why }}</td>
            <td>
              <a class="pa-ext" :href="row.product.url" target="_blank" rel="noopener noreferrer">官网详情</a>
            </td>
          </tr>
        </tbody>
      </table>
      <p class="pa-note">
        型号与「官网详情」均指向
        <a :href="WAYHO_HOME" target="_blank" rel="noopener noreferrer">wayho.cn</a>
        现网产品页。产品总览见
        <a :href="WAYHO_CATALOG" target="_blank" rel="noopener noreferrer">产品中心</a>。
      </p>
    </section>
  </div>
  <div v-else class="empty">暂无该算法的中达瑞和产品分析。</div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { getWayhoAnalysis } from "../wayho";
import { getWayhoProduct, WAYHO_CATALOG, WAYHO_HOME } from "../wayho/products";
import type { FitLevel } from "../wayho/types";

const props = defineProps<{ algorithmId: string }>();
const showNo = ref(false);

const doc = computed(() => getWayhoAnalysis(props.algorithmId));

const counts = computed(() => {
  const fits = doc.value?.fits || [];
  return {
    direct: fits.filter((f) => f.level === "direct").length,
    adapt: fits.filter((f) => f.level === "adapt").length,
    no: fits.filter((f) => f.level === "no").length,
  };
});

const visibleRows = computed(() => {
  const d = doc.value;
  if (!d) return [];
  const order: Record<FitLevel, number> = { direct: 0, adapt: 1, no: 2 };
  return d.fits
    .filter((f) => showNo.value || f.level !== "no")
    .map((f) => {
      const product = getWayhoProduct(f.productId);
      return product ? { ...f, product } : null;
    })
    .filter((row): row is NonNullable<typeof row> => !!row)
    .sort((a, b) => order[a.level] - order[b.level]);
});

function fitLabel(level: FitLevel): string {
  if (level === "direct") return "直接";
  if (level === "adapt") return "改编";
  return "不建议";
}
</script>
