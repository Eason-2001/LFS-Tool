<template>
  <div class="page-container">
    <div class="memo-card">
      <div class="memo-header">
        <h1 class="page-title">📝 我的备忘录</h1>
        <router-link to="/" class="back-btn">🏠 返回主页</router-link>
      </div>

      <!-- 新建 / 编辑表单 -->
      <div class="form-box">
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
            {{ loading ? '保存中…' : editingId ? '💾 保存修改' : '＋ 新建备忘录' }}
          </button>
          <button v-if="editingId" class="cancel-btn" @click="resetForm">取消编辑</button>
        </div>
      </div>

      <!-- 备忘录列表 -->
      <div v-if="memos.length" class="memo-list">
        <div v-for="memo in memos" :key="memo.id" class="memo-item">
          <div class="memo-main">
            <h3>{{ memo.title }}</h3>
            <div v-if="memo.content" class="memo-content" v-html="memo.content"></div>
            <span class="memo-time">{{ formatTime(memo.updated_at) }}</span>
          </div>
          <div class="item-actions">
            <button class="edit-btn" @click="startEdit(memo)">编辑</button>
            <button class="del-btn" @click="removeMemo(memo)">删除</button>
          </div>
        </div>
      </div>

      <div v-else class="empty">还没有备忘录，写一条吧～</div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onBeforeUnmount } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { request } from '../api/request'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'
import { useAuth } from '../composables/useAuth'

const { toast } = useToast()
const { confirmDialog } = useConfirm()
const { isLogin } = useAuth()

const memos = ref([])
const formTitle = ref('')
const formHtml = ref('')
const editingId = ref(null) // null=新建；数字=正在编辑哪条
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

// 清空表单，回到新建状态
const resetForm = () => {
  editingId.value = null
  formTitle.value = ''
  formHtml.value = ''
  editorRef.value?.setHtml('')
}

// 点“编辑”：把原内容填进编辑器
const startEdit = (memo) => {
  editingId.value = memo.id
  formTitle.value = memo.title
  formHtml.value = memo.content || ''
  editorRef.value?.setHtml(memo.content || '')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 新建或保存修改
const submitMemo = async () => {
  loading.value = true
  const payload = { title: formTitle.value, content: formHtml.value }
  let res
  if (editingId.value) {
    res = await request(`/api/accounts/memos/${editingId.value}/`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  } else {
    res = await request('/api/accounts/memos/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }
  loading.value = false
  const { data } = res
  if (data.code === 200) {
    resetForm()
    fetchMemos()
  } else {
    toast(data.message || '保存失败', 'error')
  }
}

// 删除
const removeMemo = async (memo) => {
  const ok = await confirmDialog({
    title: '删除备忘录',
    message: `确定删除「${memo.title}」吗？`,
  })
  if (!ok) return
  const { data } = await request(`/api/accounts/memos/${memo.id}/`, { method: 'DELETE' })
  if (data.code === 200) {
    if (editingId.value === memo.id) resetForm()
    fetchMemos()
  } else {
    toast(data.message || '删除失败', 'error')
  }
}

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
  padding: 40px 20px;
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
  align-items: flex-start;
  gap: 16px;
  background: #f6f8ff;
  border-radius: 12px;
  padding: 16px 18px;
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
.memo-content {
  font-size: 14px;
  color: #333;
  line-height: 1.7;
  margin-bottom: 6px;
  word-break: break-word;
}
.memo-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}
.memo-time {
  font-size: 12px;
  color: #999;
}
.item-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  white-space: nowrap;
}
.edit-btn {
  border: none;
  background: transparent;
  color: #5c70e0;
  font-size: 14px;
  cursor: pointer;
}
.del-btn {
  border: none;
  background: transparent;
  color: #e06c6c;
  font-size: 14px;
  cursor: pointer;
}
.empty {
  text-align: center;
  color: #888;
  padding: 40px 0;
}
</style>
