<template>
  <div class="profile-container">
    <div class="profile-card">
      <h1 class="page-title">👤 个人中心</h1>

      <!-- 头像区：点击上传新头像 -->
      <div class="avatar-section">
        <div class="avatar-big" @click="onPickAvatar">
          <img :src="avatarUrl" alt="头像" @error="onAvatarError" />
          <span class="avatar-mask">{{ uploading ? '上传中…' : '更换头像' }}</span>
        </div>
        <input ref="fileInput" type="file" accept="image/*" hidden @change="onAvatarChange" />
      </div>

      <!-- 昵称编辑 -->
      <div class="form-item">
        <label>昵称</label>
        <input v-model="nickname" type="text" maxlength="30" placeholder="给自己起个昵称" />
      </div>

      <!-- 用户名（登录名，不可改） -->
      <div class="form-item readonly">
        <label>用户名</label>
        <div class="readonly-value">@{{ username || '—' }}</div>
      </div>

      <div class="actions">
        <button class="primary-btn" :disabled="savingNick" @click="saveNickname">
          {{ savingNick ? '保存中…' : '保存昵称' }}
        </button>
        <router-link to="/" class="ghost-btn">🏠 返回主页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { request } from '../api/request'
import { useAuth } from '../composables/useAuth'
import { useToast } from '../composables/useToast'

const { state, setUser } = useAuth()
const { toast } = useToast()

const DEFAULT_AVATAR = '/default-avatar.svg'
const username = ref('')
const nickname = ref('')
const avatarUrl = ref(DEFAULT_AVATAR)
const savingNick = ref(false)
const uploading = ref(false)
const fileInput = ref(null)

// 拉取当前用户资料
const loadProfile = async () => {
  const { data } = await request('/api/accounts/profile/')
  if (data.code === 200) {
    const p = data.data
    username.value = p.username
    nickname.value = p.nickname || ''
    avatarUrl.value = p.avatar || DEFAULT_AVATAR
    setUser(p) // 同步到本地登录态
  } else {
    toast(data.message || '资料加载失败', 'error')
  }
}

// 头像加载失败（文件 404 等）时回退默认头像，避免露出裂图 alt 文字
const onAvatarError = () => {
  if (avatarUrl.value !== DEFAULT_AVATAR) avatarUrl.value = DEFAULT_AVATAR
}

// 保存昵称
const saveNickname = async () => {
  const nick = nickname.value.trim()
  if (!nick) {
    toast('昵称不能为空', 'warning')
    return
  }
  savingNick.value = true
  const { data } = await request('/api/accounts/profile/', {
    method: 'PUT',
    body: JSON.stringify({ nickname: nick }),
  })
  savingNick.value = false
  if (data.code === 200) {
    setUser(data.data)
    toast('昵称已保存', 'success')
  } else {
    toast(data.message || '保存失败', 'error')
  }
}

// 触发文件选择
const onPickAvatar = () => fileInput.value?.click()

// 选择头像：先本地预览，再上传后端
const onAvatarChange = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  const localUrl = URL.createObjectURL(file)
  avatarUrl.value = localUrl // 先上本地预览

  uploading.value = true
  const fd = new FormData()
  fd.append('avatar', file)
  const { data } = await request('/api/accounts/avatar/', { method: 'POST', body: fd })
  uploading.value = false

  if (data.code === 200) {
    setUser(data.data)
    avatarUrl.value = data.data.avatar || '/default-avatar.svg'
    toast('头像已更新', 'success')
  } else {
    avatarUrl.value = state.user?.avatar || '/default-avatar.svg' // 失败回退
    toast(data.message || '上传失败', 'error')
  }
  e.target.value = ''
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-container {
  max-width: 460px;
  margin: 0 auto;
  padding: 56px 20px 80px;
}

.profile-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 36px 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 26px;
  text-align: center;
  color: #1a1a1a;
  margin-bottom: 28px;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 28px;
}

.avatar-big {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}

.avatar-big img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-mask {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.avatar-big:hover .avatar-mask {
  opacity: 1;
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

.readonly-value {
  padding: 12px 14px;
  border-radius: 10px;
  background: #f2f3f5;
  color: #888;
  font-size: 15px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 26px;
}

.primary-btn {
  flex: 1;
  padding: 13px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(180deg, rgba(96, 140, 245, 0.95), rgba(92, 112, 224, 0.95));
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ghost-btn {
  padding: 13px 20px;
  border-radius: 10px;
  font-size: 14px;
  color: #666;
  text-decoration: none;
  background: #f5f7f6;
  border: 1px solid #e4e7e6;
}
</style>
