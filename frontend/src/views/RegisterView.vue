<template>
  <div class="page-container">
    <div class="auth-card">
      <h1 class="page-title">注册</h1>
      <p class="page-subtitle">创建账号，开始记录你的备忘录</p>

      <div class="form-item">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="至少 3 位" />
      </div>

      <div class="form-item">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="至少 6 位" />
      </div>

      <div class="form-item">
        <label>确认密码</label>
        <input v-model="confirmPassword" type="password" placeholder="再输一次密码" @keyup.enter="handleRegister" />
      </div>

      <button class="auth-btn" :disabled="loading" @click="handleRegister">
        {{ loading ? '注册中…' : '注 册' }}
      </button>

      <p class="auth-switch">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>

      <router-link to="/" class="back-btn">🏠 返回主页</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../api/request'
import { useToast } from '../composables/useToast'

const router = useRouter()
const { toast } = useToast()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

const handleRegister = async () => {
  if (!username.value || !password.value) {
    toast('请填写用户名和密码', 'warning')
    return
  }
  if (password.value !== confirmPassword.value) {
    toast('两次输入的密码不一致', 'warning')
    return
  }
  loading.value = true
  const { data } = await request('/api/accounts/register/', {
    method: 'POST',
    body: JSON.stringify({
      username: username.value,
      password: password.value,
      confirm_password: confirmPassword.value,
    }),
  })
  loading.value = false

  if (data.code === 200) {
    toast('注册成功，请登录', 'success')
    router.push('/login')
  } else {
    // 序列化器错误可能是 {字段: [提示]}，兼容取出第一条
    const msg = data.message || Object.values(data)[0]?.[0] || '注册失败'
    toast(msg, 'error')
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
