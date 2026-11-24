<template>
  <div class="home-container">
    <h1 class="page-title">L F S 工 具 箱</h1>
    <p class="page-subtitle">实用小工具，一站搞定</p>

    <div class="card-grid">
      <!-- 格式转换卡片 -->
      <router-link to="/convert" class="tool-card">
        <div class="card-icon">🎨</div>
        <h3>文件格式转换</h3>
        <p>图片、文档、音频格式一键互转</p>
      </router-link>

      <!-- 备忘录：已登录进备忘录页，未登录跳登录页 -->
      <div class="tool-card" @click="gotoMemo">
        <div class="card-icon">📝</div>
        <h3>在线备忘录</h3>
        <p>记录你的私人备忘事项</p>
      </div>

      <div class="tool-card disabled">
        <div class="card-icon">⏱️</div>
        <h3>番茄专注钟</h3>
        <p>即将上线，敬请期待</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { isLogin } = useAuth()

// 点备忘录：已登录直接进，未登录跳登录页并记下回来的地址
const gotoMemo = () => {
  if (isLogin.value) {
    router.push('/memo')
  } else {
    router.push({ name: 'login', query: { redirect: '/memo' } })
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 72px 24px 80px;
}
.page-title {
  font-size: 52px;
  letter-spacing: 3px;
  text-align: center;
  color: #ffffff;
  margin-bottom: 16px;
}
.page-subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.85);
  font-size: 18px;
  margin-bottom: 52px;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1080px;
  margin: 0 auto;
}
.tool-card {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 32px 28px;
  text-decoration: none;
  color: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
  cursor: pointer;
}
.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  background: rgba(255, 255, 255, 0.92);
}
.tool-card.disabled {
  opacity: 0.5;
  cursor: default;
}
.card-icon {
  font-size: 36px;
  line-height: 1;
  height: 36px;
  margin-bottom: 18px;
}
.tool-card h3 {
  font-size: 20px;
  line-height: 1.3;
  margin-bottom: 10px;
}
.tool-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}
@media (max-width: 900px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .card-grid { grid-template-columns: 1fr; }
}
</style>
