<template>
  <div class="page">
    <p class="kicker">全流程</p>
    <h2>从采集到结论</h2>
    <p class="lede">
      三张图用故事来讲同一条产线：业务是「飞 → 校 → 看图 → 出表」；技术是「网页按钮钻进算法抽屉」；数据是「计数变成地块上的一个数」。点图画可进入算法。
    </p>

    <nav class="page-tabs" aria-label="架构图切换">
      <button type="button" :class="{ on: tab === 'biz' }" @click="tab = 'biz'">业务架构</button>
      <button type="button" :class="{ on: tab === 'tech' }" @click="tab = 'tech'">技术架构</button>
      <button type="button" :class="{ on: tab === 'data' }" @click="tab = 'data'">数据架构</button>
    </nav>

    <BusinessArch v-if="tab === 'biz'" />
    <TechArch v-else-if="tab === 'tech'" />
    <DataArch v-else />

    <p class="kicker" style="margin-top: 48px">按菜单进入</p>
    <h2 class="section-h">九段产线</h2>
    <div class="flow">
      <div v-for="(s, i) in stages" :key="s.id" class="stage" @click="go(s.first)">
        <div class="stage-top">
          <span class="stage-idx">{{ String(i + 1).padStart(2, "0") }}</span>
          <span class="lvl">{{ s.id }}</span>
        </div>
        <h3>{{ s.title }}</h3>
        <p>{{ s.desc }}</p>
        <div class="tags">
          <router-link
            v-for="t in s.tags"
            :key="t.id"
            class="tag"
            :to="`/algo/${t.id}`"
            @click.stop
          >
            {{ t.label }}
          </router-link>
        </div>
      </div>
    </div>
    <p class="legend">
      下图九段与左侧菜单同名。算法页默认打开「算法原理」，可切换「运行演示」对照输入与输出，或打开「产品分析」查看与中达瑞和各型号的合作适配。
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import BusinessArch from "../components/arch/BusinessArch.vue";
import TechArch from "../components/arch/TechArch.vue";
import DataArch from "../components/arch/DataArch.vue";
import { GROUP_ORDER, groupTitle } from "../levels";

const router = useRouter();
const tab = ref<"biz" | "tech" | "data">("biz");

/** 与左侧菜单同一套九段；标题走 groupTitle，避免两处各写各的。 */
const STAGE_META: Record<
  string,
  { desc: string; first: string; tags: { id: string; label: string }[] }
> = {
  L0前: {
    desc: "按测区算航高、GSD 与航带重叠，铺出可飞的航点。",
    first: "01_flight_planning",
    tags: [{ id: "01_flight_planning", label: "航线" }],
  },
  L0: {
    desc: "曝光对时、POS 解算、过曝/SNR 质检与云影检测，确认这趟数能不能用。",
    first: "02_sync_timestamp",
    tags: [
      { id: "03_pos_solution", label: "POS" },
      { id: "05_cloud_shadow", label: "云检测" },
    ],
  },
  "L0→L1": {
    desc: "暗电流、坏点、条带、smile 校正后，把 DN 定标成辐亮度。",
    first: "06_dark_current",
    tags: [
      { id: "06_dark_current", label: "暗电流" },
      { id: "10_radiance_calibration", label: "辐射定标" },
    ],
  },
  L1: {
    desc: "多架次直方图匹配，让不同条带亮度可对比。",
    first: "11_relative_radiometric",
    tags: [{ id: "11_relative_radiometric", label: "直方图匹配" }],
  },
  "L1→L2": {
    desc: "白板/大气到反射率，再做定位与正射，像素落到地图上。",
    first: "13_atmospheric_correction",
    tags: [
      { id: "13_atmospheric_correction", label: "大气校正" },
      { id: "16_orthorectify", label: "正射" },
    ],
  },
  L2: {
    desc: "镶嵌匀色配准做成整景，再清洗波段、降维、切样本。",
    first: "17_mosaic",
    tags: [
      { id: "17_mosaic", label: "镶嵌" },
      { id: "23_pca", label: "MNF" },
    ],
  },
  L3: {
    desc: "植被指数、物理反演、分类与目标探测。",
    first: "27_ndvi",
    tags: [
      { id: "27_ndvi", label: "NDVI" },
      { id: "34_svm_rf_classify", label: "SVM/RF" },
      { id: "40_detect_segment", label: "目标探测" },
    ],
  },
  "L3→L4": {
    desc: "众数滤波与小斑剔除，分类图斑更干净。",
    first: "44_postprocess_smooth",
    tags: [{ id: "44_postprocess_smooth", label: "平滑" }],
  },
  L4: {
    desc: "按地块多边形汇总指数或分类，得到一块地一个数。",
    first: "45_parcel_zonal_stats",
    tags: [{ id: "45_parcel_zonal_stats", label: "地块统计" }],
  },
};

const stages = GROUP_ORDER.map((id) => ({
  id,
  title: groupTitle(id),
  ...STAGE_META[id],
}));

function go(id: string) {
  void router.push(`/algo/${id}`);
}
</script>
