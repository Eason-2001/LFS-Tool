<template>
  <div class="div-container">
    <header class="hero">
      <h1>☯ 中式命理</h1>
      <p class="hero-sub">生辰八字排盘 · 今日运势</p>
    </header>

    <!-- 中式表单 -->
    <div class="card">
      <h3 class="card-title"><span class="title-bar"></span>填写出生信息</h3>
      <div class="form-grid">
        <div class="form-item">
          <label>出生年</label>
          <input v-model.number="bazi.year" type="number" placeholder="1995" min="1901" max="2099" step="1" inputmode="numeric" />
        </div>
        <div class="form-item">
          <label>出生月</label>
          <input v-model.number="bazi.month" type="number" placeholder="1" min="1" max="12" step="1" inputmode="numeric" />
        </div>
        <div class="form-item">
          <label>出生日</label>
          <input v-model.number="bazi.day" type="number" placeholder="1" min="1" max="31" step="1" inputmode="numeric" />
        </div>
        <div class="form-item">
          <label>出生时</label>
          <input v-model.number="bazi.hour" type="number" placeholder="如 8" min="0" max="23" step="1" inputmode="numeric" />
        </div>
        <div class="form-item">
          <label>出生分</label>
          <input v-model.number="bazi.minute" type="number" placeholder="如 30" min="0" max="59" step="1" inputmode="numeric" />
        </div>
        <div class="form-item">
          <label>性别</label>
          <div class="radio-row">
            <label class="radio" :class="{ on: bazi.gender === 'm' }">
              <input v-model="bazi.gender" type="radio" value="m" /> 男
            </label>
            <label class="radio" :class="{ on: bazi.gender === 'f' }">
              <input v-model="bazi.gender" type="radio" value="f" /> 女
            </label>
          </div>
        </div>
      </div>
      <button class="primary-btn" :disabled="loadingBazi" @click="submitBazi">
        {{ loadingBazi ? '推算中…' : '开始推算' }}
      </button>
      <p v-if="baziError" class="error-tip">{{ baziError }}</p>
    </div>

    <!-- 中式结果 -->
    <div v-if="baziResult" class="card result-card">
      <div v-if="baziResult.warnings?.length" class="warn-list">
        <p v-for="(w, i) in baziResult.warnings" :key="i">⚠️ {{ w }}</p>
      </div>

      <!-- 命盘 -->
      <div class="panel">
        <h4 class="panel-title">命盘 · {{ baziResult.pan?.sx || '' }}</h4>
        <div class="info-grid">
          <div class="info-item"><span>五行局</span><b>{{ baziResult.pan?.wx || '—' }}</b></div>
          <div class="info-item"><span>命宫</span><b>{{ baziResult.pan?.mg || '—' }}</b></div>
          <div class="info-item"><span>命主</span><b>{{ baziResult.pan?.mz || '—' }}</b></div>
          <div class="info-item"><span>身主</span><b>{{ baziResult.pan?.sz || '—' }}</b></div>
          <div class="info-item"><span>身宫</span><b>{{ baziResult.pan?.sg || '—' }}</b></div>
          <div class="info-item"><span>阴阳</span><b>{{ baziResult.pan?.yy || '—' }}</b></div>
          <div class="info-item"><span>命宫干支</span><b>{{ baziResult.pan?.branch || '—' }}</b></div>
          <div class="info-item"><span>命宫主星</span><b>{{ baziResult.pan?.ming_main || '—' }}</b></div>
        </div>
      </div>

      <!-- 今日运势 -->
      <div v-if="baziResult.fortune?.day" class="panel">
        <h4 class="panel-title">{{ baziResult.fortune.shenxiao || '生肖' }} · 今日运势</h4>
        <div class="star-row">
          <span>事业 <i class="stars">{{ star(baziResult.fortune.day.career_star) }}</i></span>
          <span>财运 <i class="stars">{{ star(baziResult.fortune.day.money_star) }}</i></span>
          <span>爱情 <i class="stars">{{ star(baziResult.fortune.day.love_star) }}</i></span>
        </div>
        <p class="fortune-txt">💼 {{ baziResult.fortune.day.career_txt || '—' }}</p>
        <p class="fortune-txt">💰 {{ baziResult.fortune.day.money_txt || '—' }}</p>
        <p class="fortune-txt">💗 {{ baziResult.fortune.day.love_txt || '—' }}</p>
        <div class="lucky-grid">
          <div class="lucky-item">幸运色：{{ baziResult.fortune.day.lucky_color || '—' }}</div>
          <div class="lucky-item">方位：{{ baziResult.fortune.day.lucky_direction || '—' }}</div>
          <div class="lucky-item">数字：{{ baziResult.fortune.day.lucky_num || '—' }}</div>
          <div class="lucky-item">饰物：{{ baziResult.fortune.day.lucky_jewelry || '—' }}</div>
          <div class="lucky-item">贵人：{{ baziResult.fortune.day.lucky_noble || '—' }}</div>
        </div>
      </div>

      <!-- 本月运势（接口未返回的分项隐藏） -->
      <div v-if="baziResult.fortune?.month" class="panel">
        <h4 class="panel-title">本月运势</h4>
        <p v-if="baziResult.fortune.month.total_txt" class="fortune-txt">🌙 整体：{{ baziResult.fortune.month.total_txt }}</p>
        <p v-if="baziResult.fortune.month.summary_txt" class="fortune-txt">📝 总运：{{ baziResult.fortune.month.summary_txt }}</p>
        <p v-if="baziResult.fortune.month.career_txt" class="fortune-txt">💼 事业：{{ baziResult.fortune.month.career_txt }}</p>
        <p v-if="baziResult.fortune.month.money_txt" class="fortune-txt">💰 财运：{{ baziResult.fortune.month.money_txt }}</p>
        <p v-if="baziResult.fortune.month.love_txt" class="fortune-txt">💗 感情：{{ baziResult.fortune.month.love_txt }}</p>
        <p v-if="baziResult.fortune.month.health_txt" class="fortune-txt">🩺 健康：{{ baziResult.fortune.month.health_txt }}</p>
        <p v-if="baziResult.fortune.month.advice_txt" class="fortune-txt">🧭 建议：{{ baziResult.fortune.month.advice_txt }}</p>
      </div>

      <!-- 今日黄历 -->
      <div v-if="baziResult.huangli" class="panel">
        <h4 class="panel-title">今日黄历</h4>
        <div class="info-grid">
          <div class="info-item"><span>农历</span><b>{{ baziResult.huangli.nongli || '—' }}</b></div>
          <div class="info-item"><span>干支</span><b>{{ baziResult.huangli.ganzhi || '—' }}</b></div>
          <div class="info-item"><span>值神</span><b>{{ baziResult.huangli.zhishen || '—' }}</b></div>
          <div class="info-item"><span>冲煞</span><b>{{ baziResult.huangli.chongsha || '—' }}</b></div>
        </div>
        <div class="yi-ji">
          <div class="yi"><span class="tag yi-tag">宜</span><span>{{ baziResult.huangli.yi || '—' }}</span></div>
          <div class="ji"><span class="tag ji-tag">忌</span><span>{{ baziResult.huangli.ji || '—' }}</span></div>
        </div>
      </div>
    </div>

    <router-link to="/divination" class="back-btn">← 返回选择</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { request } from '../api/request'

const bazi = ref({ year: '', month: '', day: '', hour: '', minute: '', gender: 'm' })
const loadingBazi = ref(false)
const baziResult = ref(null)
const baziError = ref('')

const star = (n) => {
  const v = Number(n) || 0
  return '★'.repeat(v) + '☆'.repeat(5 - v)
}

// 空值 / 非数字统一转成 NaN：number 框可能返回字符串或空串，避免两套判空逻辑误判
function toNum(v) {
  if (v === '' || v === null || v === undefined) return NaN
  const n = Number(v)
  return Number.isFinite(n) ? n : NaN
}

const inRange = (n, lo, hi) => Number.isFinite(n) && n >= lo && n <= hi

async function submitBazi() {
  const f = bazi.value
  const year = toNum(f.year)
  const month = toNum(f.month)
  const day = toNum(f.day)
  const hour = toNum(f.hour)
  const minute = toNum(f.minute)

  if ([year, month, day, hour, minute].some(Number.isNaN)) {
    baziError.value = '请完整填写出生年月日时分'
    return
  }
  if (!inRange(year, 1901, 2099)) {
    baziError.value = '出生年须在 1901–2099 之间'
    return
  }
  if (!inRange(month, 1, 12)) {
    baziError.value = '出生月须在 1–12 之间'
    return
  }
  if (!inRange(day, 1, 31)) {
    baziError.value = '出生日须在 1–31 之间'
    return
  }
  const maxDay = new Date(year, month, 0).getDate()
  if (day > maxDay) {
    baziError.value = `${month} 月没有 ${day} 日，请核对日期`
    return
  }
  if (!inRange(hour, 0, 23)) {
    baziError.value = '出生时须在 0–23 之间'
    return
  }
  if (!inRange(minute, 0, 59)) {
    baziError.value = '出生分须在 0–59 之间'
    return
  }

  loadingBazi.value = true
  baziError.value = ''
  const { data } = await request('/api/divination/bazi/', {
    method: 'POST',
    body: JSON.stringify({ year, month, day, hour, minute, gender: f.gender }),
  })
  loadingBazi.value = false
  if (data.code === 200) {
    baziResult.value = data.data
  } else {
    baziError.value = data.message || '推算失败'
  }
}
</script>

<style scoped>
.div-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 56px 20px 80px;
}

/* ---- Hero ---- */
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

/* ---- 卡片 ---- */
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}

.form-item > label {
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

.radio-row {
  display: flex;
  gap: 10px;
  padding-top: 2px;
}

.radio {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 11px 0;
  border: 1px solid #e2e5ec;
  border-radius: 12px;
  font-size: 15px;
  color: #555;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s ease;
}

.radio input {
  display: none;
}

.radio.on {
  border-color: #863bff;
  background: rgba(134, 59, 255, 0.08);
  color: #7a34e8;
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
  padding: 20px;
  margin-bottom: 18px;
}

.panel:last-child {
  margin-bottom: 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 16px;
}

.panel-title::before {
  content: '';
  width: 4px;
  height: 15px;
  border-radius: 4px;
  background: linear-gradient(180deg, #863bff, #47bfff);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 12px;
}

.info-item span {
  font-size: 12px;
  color: #888;
}

.info-item b {
  font-size: 15px;
  color: #1a1a1a;
}

.star-row {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
  color: #555;
  font-size: 14px;
  margin-bottom: 14px;
}

.stars {
  font-style: normal;
  color: #863bff;
  letter-spacing: 1px;
}

.fortune-txt {
  color: #333;
  font-size: 14px;
  line-height: 1.75;
  margin: 7px 0;
}

.lucky-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.lucky-item {
  padding: 7px 13px;
  border-radius: 999px;
  background: rgba(134, 59, 255, 0.08);
  color: #6a4fa8;
  font-size: 13px;
}

.yi-ji {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.yi-ji > div {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  font-size: 14px;
  color: #333;
  line-height: 1.7;
}

.tag {
  flex: none;
  width: 36px;
  text-align: center;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  padding: 3px 0;
}

.yi-tag {
  background: #3aa76d;
}

.ji-tag {
  background: #e05252;
}

.warn-list {
  margin-bottom: 16px;
}

.warn-list p {
  color: #b8860b;
  font-size: 13px;
  margin: 4px 0;
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
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
