// src/composables/useAuth.js
// 登录态管理：令牌与用户信息存 localStorage，刷新页面不丢
import { reactive, computed } from 'vue'

const ACCESS_KEY = 'lfs_access'
const REFRESH_KEY = 'lfs_refresh'
const USER_KEY = 'lfs_user'

const state = reactive({
  access: localStorage.getItem(ACCESS_KEY),
  refresh: localStorage.getItem(REFRESH_KEY),
  user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
})

/** 解码 access 令牌里的过期时间 exp（仅做前端体验判断，安全仍以后端校验为准） */
function getTokenExp(token) {
  if (!token) return null
  try {
    const seg = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(atob(seg))
    return payload.exp ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

// 是否已登录：有 access 令牌，且令牌尚未过期
const isLogin = computed(() => {
  if (!state.access) return false
  const exp = getTokenExp(state.access)
  // 解不出 exp 时不轻易判死，交给后端 401 兜底
  return exp == null || exp > Date.now()
})

// 登录成功后保存令牌和用户信息
function setAuth({ access, refresh, ...user }) {
  state.access = access
  state.refresh = refresh
  state.user = user
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

// 退出登录：清空内存和本地存储
function logout() {
  state.access = null
  state.refresh = null
  state.user = null
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(USER_KEY)
}

export function useAuth() {
  return { state, isLogin, setAuth, logout }
}
