<template>
  <div class="page-container">
    <div class="memo-card">
      <div class="memo-header">
        <h1 class="page-title">📝 我的备忘录</h1>
        <div class="header-actions">
          <button v-if="!showForm" class="add-btn" @click="openCreate">＋ 写备忘</button>
          <router-link to="/" class="back-btn">🏠 主页</router-link>
        </div>
      </div>

      <!-- 新建表单 -->
      <div v-if="showForm" class="form-box">
        <input v-model="formTitle" type="text" placeholder="标题" class="title-input" />

        <Toolbar
          :editor="editorRef"
          :default-config="toolbarConfig"
          mode="default"
          class="toolbar"
        />
        <div class="editor-wrap">
          <Editor
            v-model="formHtml"
            :default-config="editorConfig"
            mode="default"
            @on-created="handleCreated"
          />
        </div>

        <div class="form-actions">
          <button class="add-btn" :disabled="!formTitle || loading" @click="submitMemo">
            {{ loading ? '保存中…' : '保存备忘' }}
          </button>
          <button class="cancel-btn" @click="cancelForm">取消</button>
        </div>
      </div>

      <!-- 备忘录列表：只展示概览，点击进详情 -->
      <div v-if="memos.length" class="memo-list">
        <div
          v-for="memo in memos"
          :key="memo.id"
          class="memo-item"
          @click="goDetail(memo)"
        >
          <div class="memo-main">
            <h3>{{ memo.title }}</h3>
            <p class="memo-excerpt">{{ excerpt(memo.content, 80) || '（无正文）' }}</p>
            <span class="memo-time">{{ formatTime(memo.updated_at) }}</span>
          </div>
          <span class="item-arrow">›</span>
        </div>
      </div>

      <div v-else class="empty">还没有备忘录，写一条吧～</div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { request } from '../api/request'
import { useToast } from '../composables/useToast'
import { useAuth } from '../composables/useAuth'
import { excerpt } from '../utils/html'

const router = useRouter()
const { toast } = useToast()
const { isLogin } = useAuth()

const memos = ref([])
const showForm = ref(false)
const formTitle = ref('')
const formHtml = ref('')
const loading = ref(false)
const editorRef = shallowRef(null)

const toolbarConfig = {}

const editorConfig = {
  placeholder: '写点什么…支持加粗、字号、颜色、对齐、插入图片等排版',
  MENU_CONF: {
    // 图片不走编辑器默认上传，自定义调我们后端接口，回填图片 URL
    uploadImage: {
      async customUpload(file, insertFn) {
        const fd = new FormData()
        fd.append('image', file)
        const { data } = await request('/api/accounts/memos/upload-image/', {
          method: 'POST',
          body: fd,
        })
        if (data.code === 200) {
          insertFn(data.data.url, '', '')
        } else {
          toast(data.message || '图片上传失败', 'error')
        }
      },
    },
  },
}

const handleCreated = (editor) => {
  editorRef.value = editor
}

// 拉取当前用户的备忘录列表
const fetchMemos = async () => {
  if (!isLogin.value) return
  const { data } = await request('/api/accounts/memos/')
  if (data.code === 200) memos.value = data.data
}

const openCreate = () => {
  showForm.value = true
}

const cancelForm = () => {
  showForm.value = false
  formTitle.value = ''
  formHtml.value = ''
}

// 新建备忘
const submitMemo = async () => {
  loading.value = true
  const payload = { title: formTitle.value, content: formHtml.value }
  const { data } = await request('/api/accounts/memos/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  loading.value = false
  if (data.code === 200) {
    toast('备忘已保存', 'success')
    cancelForm()
    fetchMemos()
  } else {
    toast(data.message || '保存失败', 'error')
  }
}

const goDetail = (memo) => router.push(`/memo/${memo.id}`)

// 时间格式化：只取年月日 时分
const formatTime = (iso) => (iso ? iso.replace('T', ' ').slice(0, 16) : '')

onMounted(fetchMemos)
onBeforeUnmount(() => {
  editorRef.value?.destroy()
})
</script>

<style scoped>
.page-container {
  max-width: 760px;
  margin: 0 auto;
  padding: 56px 20px;
}
.memo-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}
.memo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-title {
  font-size: 26px;
  color: #1a1a1a;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.back-btn {
  padding: 10px 22px;
  border-radius: 999px;
  background: #f5f7f6;
  border: 1px solid #e4e7e6;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  white-space: nowrap;
}
.back-btn:hover {
  background: linear-gradient(135deg, #eef1fe 0%, #f3eefc 100%);
}
.form-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.title-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 15px;
  background: white;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}
.toolbar {
  border: 1px solid #e4e7e6;
  border-bottom: none;
  border-radius: 10px 10px 0 0;
  background: #fff;
}
.editor-wrap {
  height: 440px;
  border: 1px solid #e4e7e6;
  border-radius: 0 0 10px 10px;
  background: #fff;
  overflow: hidden;
}
.editor-wrap :deep(.w-e-text-container) {
  height: 100%;
}
.editor-wrap :deep(.w-e-scroll) {
  overflow-y: auto;
}
.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.add-btn {
  align-self: flex-start;
  padding: 11px 20px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(180deg, rgba(96, 140, 245, 0.95), rgba(92, 112, 224, 0.95));
}
.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.cancel-btn {
  padding: 11px 18px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  background: #fff;
  color: #666;
  font-size: 15px;
  cursor: pointer;
}
.memo-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.memo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: #f6f8ff;
  border-radius: 12px;
  padding: 18px 20px;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}
.memo-item:hover {
  background: #ecefff;
  transform: translateY(-2px);
}
.memo-main {
  flex: 1;
  min-width: 0;
}
.memo-main h3 {
  font-size: 17px;
  color: #1a1a1a;
  margin-bottom: 6px;
}
.memo-excerpt {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 6px;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.memo-time {
  font-size: 12px;
  color: #999;
}
.item-arrow {
  font-size: 22px;
  color: #b3bcd6;
  flex-shrink: 0;
}
.empty {
  text-align: center;
  color: #888;
  padding: 40px 0;
}
</style>
