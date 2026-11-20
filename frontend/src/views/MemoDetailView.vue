<template>
  <div class="page-container">
    <div class="memo-card">
      <div class="detail-header">
        <router-link to="/memo" class="back-btn">‹ 返回列表</router-link>
        <div v-if="!editing && memo" class="header-actions">
          <button class="ghost-btn" @click="startEdit">✏️ 编辑</button>
          <button class="del-link" @click="remove">🗑 删除</button>
        </div>
      </div>

      <!-- 查看态 -->
      <template v-if="!editing">
        <template v-if="memo">
          <h1 class="detail-title">{{ memo.title }}</h1>
          <div class="detail-time">{{ formatTime(memo.updated_at) }}</div>
          <div class="detail-content" v-html="memo.content"></div>
        </template>
        <div v-else class="empty">{{ notFound ? '备忘录不存在或已删除' : '加载中…' }}</div>
      </template>

      <!-- 编辑态 -->
      <div v-else class="form-box">
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
          <button class="add-btn" :disabled="!formTitle || saving" @click="saveEdit">
            {{ saving ? '保存中…' : '保存修改' }}
          </button>
          <button class="cancel-btn" @click="cancelEdit">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { request } from '../api/request'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

const route = useRoute()
const router = useRouter()
const { toast } = useToast()
const { confirmDialog } = useConfirm()

const memo = ref(null)
const notFound = ref(false)
const editing = ref(false)
const saving = ref(false)

const formTitle = ref('')
const formHtml = ref('')
const editorRef = shallowRef(null)

const toolbarConfig = {}

const editorConfig = {
  placeholder: '写点什么…支持加粗、字号、颜色、对齐、插入图片等排版',
  MENU_CONF: {
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

// 拉取单条备忘录
const loadDetail = async () => {
  const { data } = await request(`/api/accounts/memos/${route.params.id}/`)
  if (data.code === 200) {
    memo.value = data.data
  } else {
    notFound.value = true
    toast(data.message || '加载失败', 'error')
  }
}

// 进入编辑：v-model 赋值后由封装自动写入编辑器
const startEdit = () => {
  formTitle.value = memo.value.title
  formHtml.value = memo.value.content || ''
  editing.value = true
}

const cancelEdit = () => {
  editing.value = false
  formTitle.value = ''
  formHtml.value = ''
}

// 保存修改
const saveEdit = async () => {
  saving.value = true
  const payload = { title: formTitle.value, content: formHtml.value }
  const { data } = await request(`/api/accounts/memos/${route.params.id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
  saving.value = false
  if (data.code === 200) {
    memo.value = data.data
    editing.value = false
    toast('已保存', 'success')
  } else {
    toast(data.message || '保存失败', 'error')
  }
}

// 删除后返回列表
const remove = async () => {
  const ok = await confirmDialog({
    title: '删除备忘录',
    message: `确定删除「${memo.value.title}」吗？`,
  })
  if (!ok) return
  const { data } = await request(`/api/accounts/memos/${route.params.id}/`, {
    method: 'DELETE',
  })
  if (data.code === 200) {
    toast('已删除', 'success')
    router.push('/memo')
  } else {
    toast(data.message || '删除失败', 'error')
  }
}

const formatTime = (iso) => (iso ? iso.replace('T', ' ').slice(0, 16) : '')

onMounted(loadDetail)
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
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.back-btn {
  padding: 10px 18px;
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
.ghost-btn {
  padding: 10px 18px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  background: #fff;
  color: #5c70e0;
  font-size: 14px;
  cursor: pointer;
}
.del-link {
  border: none;
  background: transparent;
  color: #e06c6c;
  font-size: 14px;
  cursor: pointer;
  padding: 10px 12px;
}
.detail-title {
  font-size: 28px;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.detail-time {
  font-size: 13px;
  color: #999;
  margin-bottom: 20px;
}
.detail-content {
  font-size: 15px;
  color: #333;
  line-height: 1.8;
  word-break: break-word;
}
.detail-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
}
.detail-content :deep(p) {
  margin: 8px 0;
}
.form-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
.empty {
  text-align: center;
  color: #888;
  padding: 40px 0;
}
</style>
