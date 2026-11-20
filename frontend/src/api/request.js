// src/api/request.js
// 统一请求封装：自动带上 JWT 令牌，解析 JSON，401 时清空登录态
import { useAuth } from '../composables/useAuth'

export async function request(url, options = {}) {
  const { state, logout } = useAuth()
  const headers = { ...(options.headers || {}) }

  // 已登录就在请求头带上访问令牌
  if (state.access) headers['Authorization'] = `Bearer ${state.access}`

  const body = options.body
  // 普通 JSON 请求自动加 Content-Type；FormData（文件上传）交给浏览器自动设
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(url, { ...options, headers })
  const data = await res.json().catch(() => ({}))

  // 令牌失效/未登录：清空本地登录态
  if (res.status === 401) logout()

  return { ok: res.ok, status: res.status, data }
}
