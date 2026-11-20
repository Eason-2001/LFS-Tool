<template>
  <div class="category-container">
    <h1 class="page-title">文件格式转换</h1>
    <p class="page-subtitle">选择你要转换的文件类型</p>

    <div class="card-grid">
      <!-- 图片转换卡片 -->
      <router-link to="/convert/image" class="tool-card">
        <div class="card-icon">🖼️</div>
        <h3>图片转换</h3>
        <p>PNG / JPG / WEBP 等图片格式互转</p>
      </router-link>

      <!-- 文档转换卡片 -->
      <router-link to="/convert/document" class="tool-card">
        <div class="card-icon">📄</div>
        <h3>文档转换</h3>
        <p>Markdown 转 HTML，后续支持更多文档格式</p>
      </router-link>

      <!-- 音频转换占位卡片 -->
      <div class="tool-card disabled">
        <div class="card-icon">🎵</div>
        <h3>音频转换</h3>
        <p>即将上线，敬请期待</p>
      </div>
    </div>

    <!-- 返回首页入口 -->
    <router-link to="/" class="back-btn">
      🏠 返回主页
    </router-link>

  </div>
</template>

<script setup>
// 分类页暂时不需要业务逻辑
</script>

<style scoped>
.category-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 80px 20px;
}

.page-title {
  font-size: 40px;
  text-align: center;
  color: #ffffff;
  margin-bottom: 12px;
}

.page-subtitle {
  text-align: center;
  color: #ffffff;
  font-size: 18px;
  margin-bottom: 60px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.tool-card {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 32px 24px;
  text-decoration: none;
  color: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.92);
}

.tool-card.disabled {
  opacity: 0.5;
}

.card-icon {
  font-size: 36px;
  margin-bottom: 16px;
}

.tool-card h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.tool-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
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
