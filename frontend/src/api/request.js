// src/api/request.js
// 统一请求封装：自动带 JWT；access 过期时用 refresh 静默换新并重放请求，都失败才退出登录
import { useAuth } from '../composables/useAuth'

// 并发锁：多个请求同时 401 时共享同一个刷新 Promise，避免重复调 refresh
let refreshPromise = null

// 用 refresh 令牌换新 access，成功返回 true
async function refreshAccessToken() {
  const { state, saveTokens } = useAuth()
  if (!state.refresh) return false

  const res = await fetch('/api/accounts/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: state.refresh }),
  })
  if (!res.ok) return false

  const data = await res.json().catch(() => ({}))
  const newAccess = data?.access
  if (!newAccess) return false

  // refresh 若返回了新的就一并保存，否则沿用旧的
  saveTokens(newAccess, data.refresh || state.refresh)
  return true
}

function getRefreshPromise() {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

// 实际发请求；access 为空则不带 Authorization
async function doFetch(url, options, access) {
  const headers = { ...(options.headers || {}) }
  if (access) headers['Authorization'] = `Bearer ${access}`

  const body = options.body
  // 普通 JSON 请求自动加 Content-Type；FormData（文件上传）交给浏览器自动设
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(url, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  return { res, data }
}

export async function request(url, options = {}) {
  const { state, logout } = useAuth()

  let { res, data } = await doFetch(url, options, state.access)

  // access 过期（401）：非 refresh 接口本身、且有 refresh 令牌时，先静默换新一次再重放
  if (res.status === 401 && state.refresh && !url.includes('/refresh/')) {
    const refreshed = await getRefreshPromise()
    if (refreshed) {
      ;({ res, data } = await doFetch(url, options, state.access))
    }
  }

  // 换新也失败 / 没有 refresh：清空本地登录态
  if (res.status === 401) logout()

  return { ok: res.ok, status: res.status, data }
}
