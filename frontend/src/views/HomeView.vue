<template>
  <div class="home-container">
    <!-- 右上角：未登录显示登录/注册，已登录显示用户名和退出 -->
    <div class="top-bar">
      <div class="auth-area">
        <template v-if="isLogin">
          <span class="username">👤 {{ state.user.username }}</span>
          <button class="ghost-btn" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <router-link to="/login" class="ghost-btn">登录</router-link>
          <router-link to="/register" class="primary-btn">注册</router-link>
        </template>
      </div>
    </div>

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
const { state, isLogin, logout } = useAuth()

// 点备忘录：已登录直接进，未登录跳登录页并记下回来的地址
const gotoMemo = () => {
  if (isLogin.value) {
    router.push('/memo')
  } else {
    router.push({ name: 'login', query: { redirect: '/memo' } })
  }
}

const handleLogout = () => {
  logout()
  router.push('/')
}
</script>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px 80px;
}
.top-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 40px;
}
.auth-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  color: #fff;
  font-size: 15px;
}
.ghost-btn {
  padding: 8px 18px;
  border-radius: 10px;
  font-size: 14px;
  color: #fff;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.35);
  cursor: pointer;
}
.primary-btn {
  padding: 8px 18px;
  border-radius: 10px;
  font-size: 14px;
  color: #fff;
  text-decoration: none;
  background: linear-gradient(180deg, rgba(96, 140, 245, 0.95), rgba(92, 112, 224, 0.95));
}
.page-title {
  font-size: 60px;
  text-align: center;
  color: #ffffff;
  margin-bottom: 12px;
}
.page-subtitle {
  text-align: center;
  color: #ffffff;
  font-size: 22px;
  margin-bottom: 60px;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
.tool-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 32px 24px;
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
  margin-bottom: 16px;
}
.tool-card h3 {
  font-size: 20px;
  margin-bottom: 8px;
}
.tool-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}
</style>
