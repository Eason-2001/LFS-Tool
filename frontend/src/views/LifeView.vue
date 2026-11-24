<template>
  <div class="life-container">
    <h1 class="page-title">🌤️ 天气</h1>
    <p class="page-subtitle">当前实况与未来三天预报</p>

    <!-- 天气卡片 -->
    <section class="panel weather-panel">
      <div v-if="loadingWeather && !weather" class="placeholder">天气加载中…</div>
      <div v-else-if="weather" class="weather-main">
        <div class="weather-left">
          <div class="weather-emoji">{{ weatherEmoji(weather.now.text) }}</div>
          <div class="weather-meta">
            <div class="weather-city">{{ weather.city }}</div>
            <div class="weather-text">{{ weather.now.text }}</div>
          </div>
        </div>
        <div class="weather-temp">{{ weather.now.temperature }}°</div>
        <div class="weather-extra">
          <span>体感 {{ weather.now.feels_like }}°</span>
          <span>湿度 {{ weather.now.humidity }}%</span>
          <span>{{ weather.now.wind_direction }}风</span>
        </div>
      </div>
      <div v-else class="placeholder">天气暂不可用</div>

      <div v-if="weather?.daily?.length" class="daily-row">
        <div v-for="(item, i) in weather.daily" :key="item.date" class="daily-item">
          <div class="daily-day">{{ dayLabel(item.date, i) }}</div>
          <div class="daily-emoji">{{ weatherEmoji(item.text_day) }}</div>
          <div class="daily-text">{{ item.text_day }}</div>
          <div class="daily-range">{{ item.low }}° ~ {{ item.high }}°</div>
        </div>
      </div>
      <p v-if="locationNote" class="location-note">📍 {{ locationNote }}</p>
    </section>

    <router-link to="/" class="back-btn">🏠 返回主页</router-link>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLife } from '../composables/useLife'
import { weatherEmoji, dayLabel } from '../utils/weather'

const { weather, loadingWeather, locationNote, loadWeather } = useLife()

onMounted(() => {
  loadWeather()
})
</script>

<style scoped>
.life-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 72px 24px 80px;
}
.page-title {
  font-size: 40px;
  letter-spacing: 2px;
  text-align: center;
  color: #fff;
  margin-bottom: 12px;
}
.page-subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.85);
  font-size: 16px;
  margin-bottom: 40px;
}
.panel {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 28px 24px;
  color: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}
.placeholder {
  color: #888;
  text-align: center;
  padding: 12px 0;
}

/* 天气主体 */
.weather-main {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}
.weather-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.weather-emoji {
  font-size: 44px;
}
.weather-city {
  font-size: 20px;
  font-weight: 600;
}
.weather-text {
  color: #666;
  font-size: 14px;
}
.weather-temp {
  font-size: 44px;
  font-weight: 700;
  margin-left: auto;
}
.weather-extra {
  display: flex;
  gap: 18px;
  width: 100%;
  color: #555;
  font-size: 14px;
}

/* 三天预报 */
.daily-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}
.daily-item {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.daily-day {
  font-weight: 600;
  font-size: 14px;
}
.daily-emoji {
  font-size: 28px;
}
.daily-text {
  color: #666;
  font-size: 13px;
}
.daily-range {
  color: #333;
  font-size: 13px;
}
.location-note {
  margin-top: 16px;
  color: #888;
  font-size: 13px;
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
