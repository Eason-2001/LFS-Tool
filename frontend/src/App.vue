<template>
  <!-- 固定在最底层的磨砂背景层 -->
  <div class="bg-layer"></div>
  <!-- 页面内容出口 -->
  <router-view />
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: system-ui, -apple-system, sans-serif;
  min-height: 100vh;
}

/* 磨砂背景层：固定铺满整个屏幕，放在最底层 */
.bg-layer {
  position: fixed;
  inset: 0; /* 上下左右全贴边，铺满全屏 */
  z-index: -1; /* 压在所有页面内容下面 */
  background-image: url('/bg.jpg'); /* 换成你自己的图片名 */
  background-size: cover;
  background-position: center;

  /* 核心：给背景图本身加磨砂模糊 */
  filter: blur(2px) brightness(0.95);
  /* 模糊之后图片边缘会露白，放大1.1倍盖住边缘 */
  transform: scale(1.1);

  /* 叠一层冷深蓝遮罩，压暗画面、烘托深夜氛围，避免太花抢文字 */
  background-color: rgba(28, 33, 62, 0.38);
}
</style>
