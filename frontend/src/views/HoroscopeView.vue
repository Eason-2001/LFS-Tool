<template>
  <div class="div-container">
    <header class="hero">
      <h1>✨ 西式星座</h1>
      <p class="hero-sub">阳历生日 · 本月星座运势</p>
    </header>

    <!-- 西式表单 -->
    <div class="card">
      <h3 class="card-title"><span class="title-bar"></span>填写阳历生日</h3>
      <div class="form-grid two">
        <div class="form-item">
          <label>出生月</label>
          <input v-model.number="horo.month" type="number" placeholder="1" min="1" max="12" step="1" inputmode="numeric" />
        </div>
        <div class="form-item">
          <label>出生日</label>
          <input v-model.number="horo.day" type="number" placeholder="1" min="1" max="31" step="1" inputmode="numeric" />
        </div>
      </div>
      <button class="primary-btn" :disabled="loadingHoro" @click="submitHoroscope">
        {{ loadingHoro ? '推算中…' : '查看本月运势' }}
      </button>
      <p v-if="horoError" class="error-tip">{{ horoError }}</p>
    </div>

    <!-- 西式结果 -->
    <div v-if="horoResult" class="card result-card">
      <div class="panel">
        <h4 class="panel-title">{{ horoResult.sign_cn }} <span class="sign-en">{{ horoResult.sign_en }}</span></h4>
        <p class="horo-date">{{ horoResult.date || '' }} · {{ horoResult.period || 'monthly' }}</p>
        <p class="horo-text">{{ horoResult.horoscope }}</p>
      </div>
    </div>

    <router-link to="/divination" class="back-btn">← 返回选择</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { request } from '../api/request'

const horo = ref({ month: '', day: '' })
const loadingHoro = ref(false)
const horoResult = ref(null)
const horoError = ref('')

function toNum(v) {
  if (v === '' || v === null || v === undefined) return NaN
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

const inRange = (n, lo, hi) => Number.isFinite(n) && n >= lo && n <= hi

async function submitHoroscope() {
  const f = horo.value
  const month = toNum(f.month)
  const day = toNum(f.day)

  if ([month, day].some(Number.isNaN)) {
    horoError.value = '请填写出生月日'
    return
  }
  if (!inRange(month, 1, 12)) {
    horoError.value = '出生月须在 1–12 之间'
    return
  }
  if (!inRange(day, 1, 31)) {
    horoError.value = '出生日须在 1–31 之间'
    return
  }

  loadingHoro.value = true
  horoError.value = ''
  const { data } = await request('/api/divination/horoscope/', {
    method: 'POST',
    body: JSON.stringify({ month, day }),
  })
  loadingHoro.value = false
  if (data.code === 200) {
    horoResult.value = data.data
  } else {
    horoError.value = data.message || '推算失败'
  }
}
</script>

<style scoped>
.div-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 56px 20px 80px;
}

.hero {
  text-align: center;
  margin-bottom: 30px;
}

.hero h1 {
  font-size: 32px;
  letter-spacing: 2px;
  color: #fff;
  font-weight: 700;
  text-shadow: 0 2px 16px rgba(20, 24, 50, 0.35);
}

.hero-sub {
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  letter-spacing: 1px;
}

.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 8px 28px rgba(18, 22, 45, 0.12);
  margin-bottom: 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  margin-bottom: 22px;
  color: #1a1a1a;
}

.title-bar {
  width: 4px;
  height: 16px;
  border-radius: 4px;
  background: linear-gradient(180deg, #863bff, #47bfff);
}

.form-grid.two {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  max-width: 360px;
  gap: 14px;
  margin-bottom: 24px;
}

.form-item label {
  display: block;
  font-size: 13px;
  color: #555;
  margin-bottom: 7px;
}

.form-item input {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid #e2e5ec;
  border-radius: 12px;
  font-size: 15px;
  background: #fff;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-item input:focus {
  border-color: #863bff;
  box-shadow: 0 0 0 3px rgba(134, 59, 255, 0.12);
}

.primary-btn {
  padding: 13px 36px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(135deg, #863bff, #6a2fd6);
  box-shadow: 0 8px 20px rgba(134, 59, 255, 0.28);
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
  filter: brightness(1.06);
  box-shadow: 0 10px 24px rgba(134, 59, 255, 0.36);
}

.primary-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-tip {
  margin-top: 14px;
  color: #e05252;
  font-size: 14px;
}

.result-card {
  padding-top: 24px;
}

.panel {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 16px;
  padding: 22px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.panel-title::before {
  content: '';
  width: 4px;
  height: 16px;
  border-radius: 4px;
  background: linear-gradient(180deg, #863bff, #47bfff);
}

.sign-en {
  font-size: 13px;
  color: #999;
  font-weight: normal;
  letter-spacing: 1px;
}

.horo-date {
  color: #999;
  font-size: 13px;
  margin-bottom: 14px;
}

.horo-text {
  color: #333;
  font-size: 15px;
  line-height: 1.9;
  white-space: pre-line;
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

@media (max-width: 720px) {
  .form-grid.two {
    max-width: none;
  }
}
</style>
