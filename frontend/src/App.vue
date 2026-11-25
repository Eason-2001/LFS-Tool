<template>
  <!-- 固定在最底层的磨砂背景层 -->
  <div class="bg-layer"></div>
  <!-- 全局头部：首页入口 + 头像/登录状态，所有页面共享 -->
  <AppHeader />
  <!-- 页面内容出口：顶部留出固定导航的高度，避免被 fixed 导航压住 -->
  <main class="app-main">
    <router-view />
  </main>
  <!-- 全局轻提示 + 确认弹窗 -->
  <Toast />
  <ConfirmDialog />
</template>

<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import Toast from './components/Toast.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { useAuth } from './composables/useAuth'
import { request } from './api/request'

const { isLogin, setUser, logout } = useAuth()

// 启动时向后端确认本地登录态仍有效；令牌失效则清掉残留，并同步最新用户资料
onMounted(async () => {
  if (!isLogin.value) return
  const { ok, data } = await request('/api/accounts/profile/')
  if (ok && data.code === 200) {
    setUser(data.data)
  } else {
    logout()
  }
})
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

/* 固定导航高度；内容区顶部留出对应间距，防止被 fixed 导航遮挡 */
.app-main {
  padding-top: 72px;
}

/* 磨砂背景层：固定铺满整个屏幕，放在最底层 */
.bg-layer {
  position: fixed;
  inset: 0; /* 上下左右全贴边，铺满全屏 */
  z-index: -1; /* 压在所有页面内容下面 */
  background-image: url('/bg.webp');
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
