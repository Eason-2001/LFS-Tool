<template>
  <div class="home-container">
    <h1 class="page-title">L F S 工 具 箱</h1>
    <p class="page-subtitle">实用小工具，一站搞定</p>

    <div class="card-grid">
      <!-- 格式转换卡片 -->
      <router-link to="/convert" class="tool-card">
        <div class="card-icon">🎨</div>
        <h3>文件格式转换</h3>
        <p>图片互转、Markdown转HTML，一键搞定</p>
      </router-link>

      <!-- 占位卡片，以后加新功能直接照着复制就行 -->
      <div class="tool-card">
        <div class="card-icon">📝</div>
        <h3>在线备忘录</h3>
        <p>即将上线，敬请期待</p>
      </div>

      <div class="tool-card">
        <div class="card-icon">⏱️</div>
        <h3>番茄专注钟</h3>
        <p>即将上线，敬请期待</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// 主页暂时不需要逻辑
</script>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 80px 20px;
}
.page-title {
  font-size: 80px;
  text-align: center;
  color: #ffffff;
  margin-bottom: 12px;
}
.page-subtitle {
  text-align: center;
  color: #ffffff;
  font-size: 25px;
  margin-bottom: 60px;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
.tool-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-decoration: none;
  color: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transition: all 0.2s ease;
}
/* 鼠标悬停的时候卡片抬升，就是那种高级感动效 */
.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
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
</style>
