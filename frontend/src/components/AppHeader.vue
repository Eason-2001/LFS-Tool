<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="header-left">
        <router-link to="/" class="brand">
          <svg class="brand-logo" viewBox="0 0 48 48" fill="none" aria-label="LFS">
            <rect x="4" y="4" width="40" height="40" rx="10" stroke="currentColor" stroke-width="3.5"/>
            <text x="24" y="30" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-weight="900" font-size="15" fill="currentColor">LFS</text>
          </svg>
          <span>LFS 工具箱</span>
        </router-link>
        <!-- 顶栏天气小部件：点击进入天气详情页 -->
        <router-link
          v-if="weather"
          to="/life"
          class="weather-widget"
          :title="`${weather.city} ${weather.now.text} ${weather.now.temperature}°`"
        >
          <span class="w-emoji">{{ weatherEmoji(weather.now.text) }}</span>
          <span class="w-info">
            <span class="w-temp">{{ weather.now.temperature }}°</span>
            <span class="w-city">{{ weather.city }} · {{ weather.now.text }}</span>
          </span>
        </router-link>
      </div>

      <div class="header-right">
        <!-- 已登录：头像 + 下拉菜单 -->
        <div v-if="isLogin" class="avatar-wrap" @click="toggleMenu">
          <img :src="displayedAvatar" class="avatar" alt="用户头像" @error="onImgError" />
          <div v-show="menuOpen" class="dropdown" @click.stop>
            <div class="dropdown-user">
              <span class="drop-nick">{{ displayName }}</span>
              <span class="drop-name">@{{ state.user?.username }}</span>
            </div>
            <router-link to="/profile" class="drop-item" @click="closeMenu">👤 个人中心</router-link>
            <div class="drop-item" @click="onLogout">🚪 退出登录</div>
          </div>
        </div>

        <!-- 未登录：默认头像，点击去登录/注册 -->
        <router-link v-else to="/login" class="auth-link">
          <img :src="defaultAvatar" class="avatar sm" alt="默认头像" />
          <span>登录 / 注册</span>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useLife } from '../composables/useLife'
import { weatherEmoji } from '../utils/weather'

const router = useRouter()
const { state, isLogin, logout } = useAuth()
const { weather, loadWeather } = useLife()

const defaultAvatar = '/default-avatar.svg'
const menuOpen = ref(false)
const imgError = ref(false)

const avatarUrl = computed(() => state.user?.avatar || defaultAvatar)
const displayedAvatar = computed(() => (imgError.value ? defaultAvatar : avatarUrl.value))
const displayName = computed(() => state.user?.nickname || state.user?.username || '未登录')

// 切换账号后重置头像加载失败标记
watch(() => state.user?.avatar, () => { imgError.value = false })

const onImgError = () => { imgError.value = true }

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}
const closeMenu = () => {
  menuOpen.value = false
}

const onLogout = () => {
  logout()
  closeMenu()
  router.push('/')
}

// 点击头部以外的区域时收起下拉
const onDocClick = (e) => {
  if (!e.target.closest('.avatar-wrap')) closeMenu()
}
onMounted(() => {
  document.addEventListener('click', onDocClick)
  loadWeather()
})
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  background: rgba(28, 33, 62, 0.35);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-decoration: none;
  letter-spacing: 1px;
}

.brand-logo {
  width: 28px;
  height: 28px;
  display: block;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.weather-widget {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  text-decoration: none;
  padding: 0;
  border: none;
  background: transparent;
}

.weather-widget:hover {
  opacity: 0.8;
}

.w-emoji {
  font-size: 22px;
  line-height: 1;
}

.w-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  line-height: 1.1;
}

.w-temp {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.w-city {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.75);
}

.header-right {
  display: flex;
  align-items: center;
}

.avatar-wrap {
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.6);
  display: block;
}

.avatar.sm {
  width: 32px;
  height: 32px;
}

.auth-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
}

.dropdown {
  position: absolute;
  right: 0;
  top: 48px;
  min-width: 160px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  overflow: hidden;
  z-index: 110;
}

.dropdown-user {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.drop-nick {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

.drop-name {
  font-size: 12px;
  color: #888;
}

.drop-item {
  display: block;
  padding: 11px 16px;
  font-size: 14px;
  color: #333;
  text-decoration: none;
  cursor: pointer;
}

.drop-item:hover {
  background: rgba(96, 140, 245, 0.1);
}
</style>
