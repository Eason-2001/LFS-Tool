<template>
  <div class="hub-container">
    <header class="hero">
      <div class="hero-title">
        <span class="hero-line"></span>
        <h1>🔮 命理测算</h1>
        <span class="hero-line"></span>
      </div>
      <p class="hero-sub">选择一种方式，看看今日与本月的运势</p>
    </header>

    <div class="entry-grid">
      <router-link
        v-for="e in entries"
        :key="e.path"
        :to="e.path"
        class="entry-card"
        :class="e.cls"
      >
        <div class="entry-img">
          <img v-if="!e.emoji" :src="e.img" :alt="e.title" />
          <div v-else class="entry-emoji">{{ e.emoji }}</div>
        </div>
        <div class="entry-body">
          <div class="entry-head">
            <span class="entry-tag">{{ e.tag }}</span>
          </div>
          <h3>{{ e.title }}</h3>
          <p>{{ e.desc }}</p>
          <span class="entry-cta">开始测算 <em>→</em></span>
        </div>
      </router-link>
    </div>

    <!-- 历史记录 -->
    <div v-if="history.length" class="card">
      <h3 class="card-title"><span class="title-bar"></span>测算历史</h3>
      <ul class="history-list">
        <li v-for="h in history" :key="h.id" class="history-item">
          <div class="history-head">
            <span class="kind-tag" :class="h.kind">{{ KIND_LABEL[h.kind] || '命理' }}</span>
            <span class="history-summary">{{ h.summary }}</span>
            <span class="history-time">{{ formatTime(h.created_at) }}</span>
          </div>
        </li>
      </ul>
    </div>

    <router-link to="/" class="back-btn">🏠 返回主页</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { request } from '../api/request'

const entries = [
  {
    path: '/divination/tarot',
    img: '/divination/tarot.png',
    title: '命运塔罗',
    desc: '三牌阵 · 直觉选牌 · 牌意解读',
    tag: '大阿卡纳 · 正逆位',
    cls: 'theme-tarot',
  },
  {
    path: '/divination/bazi',
    img: '/divination/bazi.webp',
    title: '中式命理',
    desc: '生辰八字排盘 · 今日运势',
    tag: '紫微斗数 · 生肖 · 黄历',
    cls: 'theme-cn',
  },
  {
    path: '/divination/horoscope',
    img: '/divination/horoscope.webp',
    title: '西式星座',
    desc: '阳历生日 · 本月运势',
    tag: '黄道十二宫 · 月度星运',
    cls: 'theme-west',
  },
]

const KIND_LABEL = { bazi: '中式', horoscope: '西式', tarot: '塔罗' }

const history = ref([])

async function loadHistory() {
  const { data } = await request('/api/divination/history/')
  if (data.code === 200) history.value = data.data || []
}

const formatTime = (iso) => (iso ? String(iso).slice(0, 16).replace('T', ' ') : '')

onMounted(loadHistory)
</script>

<style scoped>
.hub-container {
  max-width: 1080px;
  margin: 0 auto;
  padding: 64px 20px 80px;
}

/* ---- Hero ---- */
.hero {
  text-align: center;
  margin-bottom: 44px;
}

.hero-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
}

.hero-title h1 {
  font-size: 38px;
  letter-spacing: 3px;
  color: #fff;
  font-weight: 700;
  text-shadow: 0 2px 16px rgba(20, 24, 50, 0.35);
}

.hero-line {
  width: 56px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.7));
}

.hero-line:last-child {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.7), transparent);
}

.hero-sub {
  margin-top: 14px;
  color: rgba(255, 255, 255, 0.82);
  font-size: 15px;
  letter-spacing: 1px;
}

/* ---- 卡片 ---- */
.entry-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.entry-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 22px;
  overflow: hidden;
  text-decoration: none;
  color: #1a1a1a;
  box-shadow: 0 8px 28px rgba(18, 22, 45, 0.12);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.entry-card:hover {
  transform: translateY(-7px);
  box-shadow: 0 18px 40px rgba(18, 22, 45, 0.2);
}

.entry-img {
  position: relative;
  aspect-ratio: 9 / 16;
  overflow: hidden;
}

.entry-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}

.entry-card:hover .entry-img img {
  transform: scale(1.05);
}

.entry-body {
  padding: 20px 22px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.entry-head {
  display: flex;
}

.entry-tag {
  font-size: 12px;
  letter-spacing: 0.5px;
  padding: 4px 12px;
  border-radius: 999px;
}

.theme-cn .entry-tag {
  color: #b83a3a;
  background: rgba(184, 58, 58, 0.1);
}

.theme-west .entry-tag {
  color: #7a34e8;
  background: rgba(134, 59, 255, 0.1);
}

.theme-tarot .entry-tag {
  color: #2b6cb0;
  background: rgba(43, 108, 176, 0.1);
}

.entry-emoji {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  background: linear-gradient(155deg, #4b3a8f 0%, #2c2f5e 55%, #1d2340 100%);
}

.entry-body h3 {
  font-size: 20px;
  letter-spacing: 1px;
}

.entry-body p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.entry-cta {
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}

.theme-cn .entry-cta {
  color: #b83a3a;
}

.theme-west .entry-cta {
  color: #7a34e8;
}

.theme-tarot .entry-cta {
  color: #2b6cb0;
}

.entry-cta em {
  font-style: normal;
  transition: transform 0.2s ease;
}

.entry-card:hover .entry-cta em {
  transform: translateX(4px);
}

/* ---- 历史 ---- */
.card {
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 18px;
  padding: 26px 28px;
  box-shadow: 0 8px 24px rgba(18, 22, 45, 0.1);
  margin-top: 36px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  margin-bottom: 14px;
  color: #1a1a1a;
}

.title-bar {
  width: 4px;
  height: 16px;
  border-radius: 4px;
  background: linear-gradient(180deg, #863bff, #47bfff);
}

.history-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.history-item {
  padding: 14px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.07);
}

.history-item:last-child {
  border-bottom: none;
}

.history-head {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.kind-tag {
  flex: none;
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: #fff;
}

.kind-tag.bazi {
  background: #863bff;
}

.kind-tag.horoscope {
  background: #47bfff;
}

.kind-tag.tarot {
  background: #2b6cb0;
}

.history-summary {
  font-size: 15px;
  color: #1a1a1a;
}

.history-time {
  margin-left: auto;
  font-size: 13px;
  color: #999;
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

@media (max-width: 900px) {
  .entry-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .entry-grid {
    grid-template-columns: 1fr;
  }

  .hero-title h1 {
    font-size: 30px;
  }
}
</style>
