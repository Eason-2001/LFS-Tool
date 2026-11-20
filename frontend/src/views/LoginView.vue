<template>
  <div class="page-container">
    <div class="auth-card">
      <h1 class="page-title">登录</h1>
      <p class="page-subtitle"></p>

      <div class="form-item">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="请输入用户名" />
      </div>

      <div class="form-item">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
      </div>

      <button class="auth-btn" :disabled="loading" @click="handleLogin">
        {{ loading ? '登录中…' : '登 录' }}
      </button>

      <p class="auth-switch">
        还没有账号？<router-link to="/register">去注册</router-link>
      </p>

      <router-link to="/" class="back-btn">🏠 返回主页</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { request } from '../api/request'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const { setAuth } = useAuth()
const { toast } = useToast()

const username = ref('')
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    toast('请输入用户名和密码', 'warning')
    return
  }
  loading.value = true
  const { data } = await request('/api/accounts/login/', {
    method: 'POST',
    body: JSON.stringify({ username: username.value, password: password.value }),
  })
  loading.value = false

  if (data.code === 200) {
    setAuth(data.data)
    // 登录后回到原本要去的页面，没有则进备忘录
    router.push(route.query.redirect || '/memo')
  } else {
    toast(data.message || '登录失败', 'error')
  }
}
</script>

<style scoped>
.page-container {
  max-width: 420px;
  margin: 0 auto;
  padding: 80px 20px;
}
.auth-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 36px 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}
.page-title {
  font-size: 30px;
  text-align: center;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.page-subtitle {
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-bottom: 28px;
}
.form-item {
  margin-bottom: 18px;
}
.form-item label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
}
.form-item input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 15px;
  background: white;
  outline: none;
  box-sizing: border-box;
}
.form-item input:focus {
  border-color: #6c88f0;
}
.auth-btn {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(180deg, rgba(96, 140, 245, 0.95), rgba(92, 112, 224, 0.95));
  transition: opacity 0.2s ease;
}
.auth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.auth-switch {
  text-align: center;
  margin-top: 18px;
  font-size: 14px;
  color: #666;
}
.auth-switch a {
  color: #5c70e0;
  text-decoration: none;
}
.back-btn {
  display: block;
  width: fit-content;
  margin: 18px auto 0;
  padding: 10px 22px;
  border-radius: 999px;
  background: #f5f7f6;
  border: 1px solid #e4e7e6;
  color: #666;
  text-decoration: none;
  font-size: 14px;
}
.back-btn:hover {
  background: linear-gradient(135deg, #eef1fe 0%, #f3eefc 100%);
}
</style>
