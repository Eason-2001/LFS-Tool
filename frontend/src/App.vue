<template>
  <div class="container">
    <h1>LFS 在线文件转换</h1>

    <!-- 上传表单 -->
    <div class="upload-box">
      <!-- 选择要转换的文件 -->
      <input type="file" @change="onFileChange" />

      <!-- 选择目标格式，选项从后端接口拿 -->
      <select v-model="targetFormat">
        <option value="">请选择转换格式</option>
        <option v-for="item in formatList" :value="item.target">
          {{ item.label }}
        </option>
      </select>

      <button @click="handleConvert" :disabled="!selectedFile || !targetFormat">
        开始转换
      </button>
    </div>

    <!-- 转换成功后的下载区 -->
    <div v-if="downloadUrl" class="result-box">
      <p>✅ 转换成功！</p>
      <a :href="downloadUrl" target="_blank">点击下载转换后的文件</a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 响应式变量
const formatList = ref([])  // 存支持的格式列表
const selectedFile = ref(null)  // 存用户选的文件
const targetFormat = ref('')  // 存用户选的目标格式
const downloadUrl = ref('')  // 存转换后的下载链接

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
  // 构造上传的表单数据
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('target_format', targetFormat.value)

  // 调后端上传接口
  const res = await fetch('http://127.0.0.1:8000/api/converter/convert/', {
    method: 'POST',
    body: formData
  })
  const result = await res.json()
  if (result.code === 200) {
    // 拼上后端地址，生成完整下载链接
    downloadUrl.value = 'http://127.0.0.1:8000' + result.data.download_url
  } else {
    alert(result.message)
  }
}
</script>

<style scoped>
.container { max-width: 600px; margin: 50px auto; text-align: center; }
.upload-box { margin: 30px 0; display: flex; flex-direction: column; gap: 15px; }
button { padding: 10px; background: #42b983; color: white; border: none; border-radius: 5px; cursor: pointer; }
.result-box { margin-top: 30px; padding: 20px; background: #f0f9eb; border-radius: 5px; }
</style>
