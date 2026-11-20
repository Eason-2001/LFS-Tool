<template>
  <header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="brand">🧰 LFS 工具箱</router-link>

      <div class="header-right">
        <!-- 已登录：头像 + 下拉菜单 -->
        <div v-if="isLogin" class="avatar-wrap" @click="toggleMenu">
          <img :src="avatarUrl" class="avatar" alt="用户头像" />
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { state, isLogin, logout } = useAuth()

const defaultAvatar = '/default-avatar.svg'
const menuOpen = ref(false)

const avatarUrl = computed(() => state.user?.avatar || defaultAvatar)
const displayName = computed(() => state.user?.nickname || state.user?.username || '未登录')

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
onMounted(() => document.addEventListener('click', onDocClick))
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-decoration: none;
  letter-spacing: 1px;
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
