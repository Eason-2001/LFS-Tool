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

// 是否已登录：access 未过期即登录；access 过期但 refresh 仍有效，视为可续期的登录态
// （真正发请求时由 request 层静默换新；refresh 也过期才彻底退出）
const isLogin = computed(() => {
  const accessExp = state.access ? getTokenExp(state.access) : null
  if (accessExp == null || accessExp > Date.now()) {
    // access 有效，或解不出 exp 时不轻易判死（交后端兜底）
    if (accessExp == null) return !!state.access
    return true
  }
  // access 已过期：看 refresh 是否还在有效期内
  const refreshExp = state.refresh ? getTokenExp(state.refresh) : null
  return refreshExp != null && refreshExp > Date.now()
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

// 仅更新本地用户资料（昵称/头像变更后同步），保留原有令牌
function setUser(user) {
  state.user = user
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

// 刷新令牌后保存新的 access（refresh 沿用，不动用户信息）
function saveTokens(access, refresh) {
  state.access = access
  state.refresh = refresh
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
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
  return { state, isLogin, setAuth, setUser, saveTokens, logout }
}
