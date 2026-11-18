<template>
  <div class="page-container">
    <div class="convert-card">
      <h1 class="page-title">文件格式转换</h1>
      <p class="page-subtitle">上传文件，选择目标格式，一键完成转换</p>

      <!-- 上传表单 -->
      <div class="upload-box">
        <!-- 文件选择区 -->
        <label class="file-upload" :class="{ 'has-file': selectedFile }">
          <input type="file" @change="onFileChange" hidden />
          <span class="upload-icon">📁</span>
          <span v-if="!selectedFile" class="upload-text">点击选择要转换的文件</span>
          <span v-else class="upload-text">{{ selectedFile.name }}</span>
        </label>

        <!-- 格式选择下拉框 -->
        <select v-model="targetFormat" class="format-select">
          <option value="">请选择目标转换格式</option>
          <!-- 遍历所有分类分组 -->
          <optgroup v-for="(group, catKey) in formatList" :key="catKey" :label="group.name">
          <option v-for="item in group.items" :value="item.target">
          {{ item.label }}
          </option>
        </optgroup>
          </select>

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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 响应式变量
const formatList = ref([])
const selectedFile = ref(null)
const targetFormat = ref('')
const downloadUrl = ref('')

// 页面刚加载的时候，就去后端拉支持的格式列表
onMounted(async () => {
  const res = await fetch('http://127.0.0.1:8000/api/converter/supported/')
  const data = await res.json()
  formatList.value = data.data
})

// 用户选文件的时候触发
const onFileChange = (e) => {
  selectedFile.value = e.target.files[0]
}

// 点开始转换按钮
const handleConvert = async () => {
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('target_format', targetFormat.value)

  const res = await fetch('http://127.0.0.1:8000/api/converter/convert/', {
    method: 'POST',
    body: formData
  })
  const result = await res.json()
  if (result.code === 200) {
    downloadUrl.value = 'http://127.0.0.1:8000' + result.data.download_url
  } else {
    alert(result.message)
  }
}
</script>

<style scoped>
.page-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 60px 20px;
}

.convert-card {
  background: white;
  border-radius: 20px;
  padding: 40px 32px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
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
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-upload:hover {
  border-color: #42b983;
  background: #f8fdfb;
}

.file-upload.has-file {
  border-style: solid;
  border-color: #42b983;
  background: #f8fdfb;
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

.format-select:focus {
  border-color: #42b983;
}

/* 按钮美化 */
.convert-btn {
  padding: 14px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.convert-btn:hover:not(:disabled) {
  background: #35a072;
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
  background: #f0f9eb;
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
  color: #42b983;
  font-size: 15px;
  text-decoration: none;
  font-weight: 500;
}

.download-link:hover {
  text-decoration: underline;
}
</style>
