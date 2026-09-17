<template>
  <section class="card">
    <p class="step">流程图 · 大模型在哪一步出现</p>
    <h2>绿色框才是大模型；前面几步都不进模型</h2>
    <ol class="llm-flow">
      <li>
        <span class="who">人</span>
        <strong>点「算出两张图」</strong>
      </li>
      <li>
        <span class="who">算法</span>
        <strong>算出 NDVI、NDRE 两张彩图</strong>
        <em>图给页面看，影像到此为止</em>
      </li>
      <li>
        <span class="who">规则</span>
        <strong>写死：主图必须是 NDRE</strong>
        <em>大模型不能改成主看 NDVI</em>
      </li>
      <li class="in">
        <span class="who">打包</span>
        <strong>打成一段 JSON</strong>
        <em>问题 + 规则 + 两张图的 min / max / mean。这才是大模型输入</em>
      </li>
    </ol>
    <p class="fork-label">顶栏开了密钥？</p>
    <div class="fork">
      <article>
        <p class="who">否 · 模型没干活</p>
        <strong>右侧用我们写好的模板</strong>
        <em>JSON 准备好了，但没有发出去</em>
      </article>
      <article class="yes">
        <p class="who">是 · 大模型上场</p>
        <strong>读 JSON，写出中文说明</strong>
        <em>吐出标题 + 正文，用来填右侧</em>
        <p class="sub-fork">写了公斤或亩？</p>
        <ul>
          <li>是：整段丢掉，改回模板</li>
          <li>否：右侧换成模型写的说明</li>
        </ul>
      </article>
    </div>
    <p class="flow-end">人看到：两张图（算法算的）+ 右侧说明（模板或模型改写）</p>
  </section>
</template>

<script setup lang="ts">
/** L3：把「谁出图、谁选图、谁写字」画成流程。 */
</script>
