<template>
  <div class="page-container">
    <div class="convert-card">
      <h1 class="page-title">
        {{ currentCategory === 'image' ? '图片格式转换' : '文档格式转换' }}
      </h1>
      <p class="page-subtitle">上传文件，选择目标格式，一键完成转换</p>

      <!-- 上传表单 -->
      <div class="upload-box">
        <!-- 文件选择区 -->
        <label class="file-upload" :class="{ 'has-file': selectedFile }">
          <input type="file" @change="onFileChange" hidden/>
          <span class="upload-icon">📁</span>
          <span v-if="!selectedFile" class="upload-text">点击选择要转换的文件</span>
          <span v-else class="upload-text">{{ selectedFile.name }}</span>
        </label>

        <!-- 自定义下拉：触发框 + 选项面板 -->
        <div class="custom-select" ref="selectRef">
          <div class="select-trigger" :class="{ placeholder: !targetFormat }" @click="open = !open">
            <span>{{ currentLabel || '请选择目标转换格式' }}</span>
            <span class="select-arrow">▾</span>
          </div>

          <ul v-show="open" class="select-panel">
            <li
                v-for="item in currentItems"
                :key="`${item.source}-${item.target}`"
                :class="{ active: `${item.source}-${item.target}` === selectedKey }"
                @click="chooseItem(item)"
            >
              {{ item.label }}
            </li>

          </ul>
        </div>


        <!-- 转换按钮 -->
        <button
            class="convert-btn"
            @click="handleConvert"
            :disabled="!selectedFile || !targetFormat"
        >
          开始转换
        </button>
      </div>

      <!-- 转换成功后的下载区 -->
      <div v-if="downloadUrl" class="result-box">
        <div class="result-icon">✅</div>
        <p class="result-title">转换成功！</p>
        <a :href="downloadUrl" target="_blank" class="download-link">
          点击下载转换后的文件
        </a>
      </div>
      <router-link to="/convert" class="back-btn">
        🔙 返回格式分类
      </router-link>

    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, onBeforeUnmount} from 'vue'
import {useRoute} from 'vue-router'


// 响应式变量
const route = useRoute()
// 根据当前路由判断是图片页还是文档页
// 路径是 /convert/image → 取 image 分组；/convert/document → 取 document 分组
const currentCategory = route.path.includes('image') ? 'image' : 'document'
const selectedFile = ref(null)
const currentItems = ref([])
const targetFormat = ref('')
const downloadUrl = ref('')

const open = ref(false)
const selectRef = ref(null)
// 存选中项的唯一标识：source-target，避免不同转换对后缀撞车
const selectedKey = ref('')

const currentLabel = computed(() => {
  const hit = currentItems.value.find(
      i => `${i.source}-${i.target}` === selectedKey.value
  )
  return hit ? hit.label : ''
})

const chooseItem = (item) => {
  selectedKey.value = `${item.source}-${item.target}`
  targetFormat.value = item.target
  open.value = false
}

// 选中文件时触发：把选到的文件存进 selectedFile
const onFileChange = (e) => {
  selectedFile.value = e.target.files[0]
}

// 点击组件外部时自动收起面板
const onDocClick = (e) => {
  if (selectRef.value && !selectRef.value.contains(e.target)) {
    open.value = false
  }
}
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))


// 页面刚加载的时候，就去后端拉支持的格式列表
onMounted(async () => {
  const res = await fetch('/api/converter/supported/')
  const data = await res.json()
  // 直接拿当前分类下的格式选项列表，不再保留分组结构
  currentItems.value = data.data[currentCategory]?.items || []
})

// 点开始转换按钮
const handleConvert = async () => {
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('target_format', targetFormat.value)

  const res = await fetch('/api/converter/convert/', {
    method: 'POST',
    body: formData
  })
  const result = await res.json()
  if (result.code === 200) {
    downloadUrl.value = result.data.download_url
  } else {
    alert(result.message)
  }
}
</script>

<style scoped>
/* 自定义下拉 */
.custom-select {
  position: relative;
}

.select-trigger {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 13px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 15px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

/* 没选时提示词显示灰色 */
.select-trigger.placeholder {
  color: #999999;
}

.select-arrow {
  color: #999999;
  font-size: 12px;
}

/* 弹出的选项面板 */
.select-panel {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 10;
  list-style: none;
  margin: 0;
  padding: 6px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.select-panel li {
  margin: 0;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 15px;
  color: #1a1a1a;
  cursor: pointer;
}

.select-panel li:hover {
  background: #f5f7f6;
}

.select-panel li.active {
  background: linear-gradient(135deg, #eef1fe 0%, #f3eefc 100%);
  color: #5b7cfa;
}


.page-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 60px 20px;
}

.convert-card {
  /* 半透明白底 + 背景模糊，磨砂玻璃质感 */
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  padding: 40px 32px;
  box-shadow: 0 12px 40px rgba(20, 25, 60, 0.18);
}

.page-title {
  font-size: 28px;
  text-align: center;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.page-subtitle {
  text-align: center;
  color: #666;
  font-size: 15px;
  margin-bottom: 32px;
}

.upload-box {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 文件选择区美化 */
.file-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 36px 20px;
  border: 2px dashed #dcdfe6;
  border-radius: 14px;
  background: #f6f8ff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-upload:hover {
  background: #f6f8ff;
}

.file-upload.has-file {
  border-style: solid;
  background: #f6f8ff;
}

.upload-icon {
  font-size: 32px;
}

.upload-text {
  color: #666;
  font-size: 15px;
}

/* 下拉框美化 */
.format-select {
  padding: 13px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 15px;
  color: #1a1a1a;
  background: white;
  outline: none;
  transition: border-color 0.2s ease;
}

/* 按钮美化 */
.convert-btn {
  padding: 14px;
  /* 淡蓝 → 蓝紫，从上到下渐变，整体偏蓝、带一点通透感 */
  background: linear-gradient(180deg, rgba(122, 168, 255, 0.92) 0%, rgba(110, 130, 240, 0.92) 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.convert-btn:hover:not(:disabled) {
  background: linear-gradient(180deg, rgba(96, 140, 245, 0.95) 0%, rgba(92, 112, 224, 0.95) 100%);
  box-shadow: 0 6px 18px rgba(80, 120, 237, 0.3);
  transform: translateY(-1px);
}

.convert-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

/* 成功结果区 */
.result-box {
  margin-top: 28px;
  padding: 24px;
  background: linear-gradient(135deg, #eef1fe 0%, #f3eefc 100%);
  border-radius: 14px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-icon {
  font-size: 28px;
}

.result-title {
  color: #1a1a1a;
  font-size: 16px;
  font-weight: 500;
}

.download-link {
  color: #666666;
  font-size: 15px;
  text-decoration: none;
  font-weight: 500;
}

.download-link:hover {
  text-decoration: underline;
}

.back-btn {
  display: block;
  width: fit-content;
  margin: 24px auto 0;
  padding: 10px 22px;
  border-radius: 999px;
  background: #f5f7f6;
  border: 1px solid #e4e7e6;
  color: #666666;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: linear-gradient(135deg, #eef1fe 0%, #f3eefc 100%);
  color: #5b7cfa;
  transform: translateY(-2px);
}


</style>
