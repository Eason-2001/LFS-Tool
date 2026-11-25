<template>
  <div class="tarot-container">
    <div class="tarot-window">
      <!-- 窗口头部 -->
      <div class="win-header">
        <span class="win-title">🔮 命运塔罗</span>
        <button class="win-reset" title="重置" @click="reset">↻</button>
      </div>

      <!-- 舞台：牌堆 deck 与横排结果区 cards-area 重叠 -->
      <div
        class="stage"
        ref="stageEl"
        @pointerdown="onPointerDown"
        @click="onStageClick"
      >
        <!-- 牌堆扇形 -->
        <div class="deck" :class="{ 'deck--hidden': stage === 'reveal' }" v-show="!deckGone">
          <button
            v-for="i in BACKS"
            :key="i"
            class="deck-card"
            :data-deck-index="i"
            :class="{ picked: selected.includes(i) }"
            v-show="!dealt || !selected.includes(i)"
            :style="layout(i)"
          >
            <span v-if="selected.includes(i)" class="pick-no">{{ selected.indexOf(i) + 1 }}</span>
            <span class="back-pattern"></span>
          </button>
        </div>

        <!-- 横排结果区 -->
        <div
          class="cards-area"
          :data-count="result ? result.cards.length : 0"
          :class="{ 'area--show': stage === 'reveal' }"
        >
          <div v-for="(card, i) in (result ? result.cards : [])" :key="card.id" class="slot" :data-slot="i">
            <div
              class="rcard"
              :class="{ flipped: slotDone[i], active: activeIdx === i, empty: !slotDone[i] }"
              @click="onSlotClick(i)"
            >
              <div class="rinner">
                <div class="rface rback"><span class="back-pattern"></span></div>
                <div class="rface rfront">
                  <div class="rfront-img">
                    <img
                      :src="cardImg(card.id)"
                      :alt="card.name"
                      :class="{ rotated: !card.upright }"
                      loading="lazy"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div class="slot-meta">
              <div class="rname">{{ card.name }}</div>
              <div class="r-dir" :class="card.upright ? 'upright' : 'reversed'">
                {{ card.upright ? '正位' : '逆位' }}
              </div>
            </div>
            <div class="slot-label">{{ card.position }}</div>
          </div>
        </div>

        <!-- 飞牌层：从牌堆抽到横排槽位 -->
        <div v-for="f in flies" :key="f.key" class="fly" :class="{ flipped: f.flipped }" :style="flyStyle(f)">
          <div class="rinner">
            <div class="rface rback"><span class="back-pattern"></span></div>
            <div class="rface rfront">
              <div class="rfront-img">
                <img
                  :src="cardImg(f.card.id)"
                  :class="{ rotated: !f.card.upright }"
                  loading="lazy"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 等待大模型解读：仪式感加载层 -->
        <div v-if="loading" class="loading-mask">
          <div class="loading-orbit">
            <span class="orbit-ring ring-outer"></span>
            <span class="orbit-ring ring-inner"></span>
            <span class="orbit-star">✦</span>
            <span class="orbit-plate">
              <span class="orbit-dot d1"></span>
              <span class="orbit-dot d2"></span>
              <span class="orbit-dot d3"></span>
            </span>
          </div>
          <p class="loading-text">星辰正在排列</p>
          <p class="loading-sub">牌面即将显现，请稍候勿离开</p>
        </div>
      </div>

      <!-- 综合解答：结合全部卡牌推算的全局结论（不属于单牌，独立展示） -->
      <div v-if="stage === 'reveal' && result" class="verdict-wrap">
        <div v-if="verdictStage === 'gathering'" class="verdict-gather">
          <span class="verdict-dot"></span>
          牌面正在汇聚启示…
        </div>
        <div v-else-if="verdictStage === 'revealed' && result.summary" class="verdict">
          <div class="verdict-ornament">✦</div>
          <h3 class="verdict-title">综合解答</h3>
          <p v-if="question" class="verdict-q">关于「{{ question }}」</p>
          <p class="verdict-text">{{ result.summary }}</p>
        </div>
      </div>

      <p class="win-tip">{{ tipText }}</p>

      <!-- 提问 -->
      <div class="win-question">
        <input
          v-model="question"
          class="question-input"
          type="text"
          maxlength="100"
          placeholder="请写下你想问的问题（必填）"
        />
      </div>

      <div class="win-action">
        <button
          v-show="stage !== 'reveal' && (canReveal || loading || dealing)"
          class="primary-btn"
          :disabled="!canReveal || !hasQuestion || loading || dealing"
          @click="reveal"
        >
          {{ btnText }}
        </button>
      </div>

      <p v-if="errorTip" class="error-tip">{{ errorTip }}</p>

      <!-- 底部牌阵切换 -->
      <div class="win-tabs">
        <button
          v-for="(cfg, key) in SPREADS"
          :key="key"
          class="tab-btn"
          :class="{ active: spread === key }"
          @click="changeSpread(key)"
        >
          {{ cfg.label }}
        </button>
      </div>

      <router-link to="/divination" class="win-back">← 返回选择</router-link>
    </div>

    <!-- 单牌详情弹框 -->
    <teleport to="body">
      <div v-if="detailCard" class="detail-mask" @click.self="closeDetail">
        <div class="detail-modal">
          <button class="detail-close" @click="closeDetail" aria-label="关闭">✕</button>
          <div class="dm-head">
            <img
              class="dm-img"
              :src="cardImg(detailCard.id)"
              :alt="detailCard.name"
              :class="{ rotated: !detailCard.upright }"
            />
            <div class="dm-meta">
              <h2>{{ detailCard.name }}</h2>
              <p class="dm-en">{{ detailCard.name_en }} · {{ suitLabel(detailCard.suit) }}</p>
              <span class="dm-dir" :class="detailCard.upright ? 'up' : 'down'">
                {{ detailCard.upright ? '正位' : '逆位' }}
              </span>
            </div>
          </div>

          <div class="dm-kw">
            <span v-for="k in keywordList(detailCard)" :key="k" class="dm-kw-tag">{{ k }}</span>
          </div>

          <!-- 本地静态牌意（始终展示） -->
          <section class="dm-block">
            <h3>{{ detailCard.upright ? '正位解读' : '逆位解读' }}</h3>
            <p class="dm-reading">{{ detailCard.reading }}</p>
          </section>

          <!-- AI 个性化解读（结合提问生成，有则展示） -->
          <section v-if="detailCard.ai_reading" class="dm-block dm-ai">
            <h3>个性化解读</h3>
            <p class="dm-reading">{{ detailCard.ai_reading }}</p>
          </section>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { request } from '../api/request'

const SPREADS = {
  daily: { label: '每日一牌', count: 1, hint: '今日指引 · 选 1 张牌' },
  three: { label: '三牌占卜', count: 3, hint: '回顾过去 · 看清现在 · 走向未来' },
  love: { label: '爱情占卜', count: 3, hint: '现状 · 对方心态 · 关系走向' },
}

// 全套 78 张牌背
const BACKS = Array.from({ length: 78 }, (_, i) => i)

const SUIT_LABEL = {
  major: '大阿卡纳',
  wands: '权杖',
  cups: '圣杯',
  swords: '宝剑',
  pents: '星币',
}

// ---- 极坐标扇形常量（对齐参考站算法）----
const ANGLE_STEP = 4        // 相邻两张牌在圆心处的角度间隔（度）
const RADIUS_K = 1.1        // 半径 = RADIUS_K × 舞台宽
const MIN_M = 0
const MAX_M = 77

const spread = ref('daily')
const stage = ref('shuffle') // shuffle | pick | reveal
const selected = ref([])
const question = ref('')
const loading = ref(false)
const dealing = ref(false)
const result = ref(null)
const errorTip = ref('')
const slotDone = ref([])
const flies = ref([])
const activeIdx = ref(-1)
// 当前打开的详情弹框牌
const detailCard = ref(null)
// 综合解答浮现阶段：idle 未开始 | gathering 汇聚提示 | revealed 结论已浮现
const verdictStage = ref('idle')
// 已发牌：起点坐标读取完成后，被选中的牌从牌堆原位移除
const dealt = ref(false)
// 整堆牌离场：飞牌起点缓存完成后，整个牌堆层直接隐藏，底部只留背景
const deckGone = ref(false)

// 舞台尺寸
const stageEl = ref(null)
const stageW = ref(320)
const stageH = ref(380)
// 当前居中的牌索引（可随拖拽平移），78 张中点
const M = ref(38.5)

// 拖拽 / 惯性状态
let startX = 0
let lastX = 0
let lastT = 0
let O = 0
let vel = 0
let dragging = false
let moved = false
let rafDrag = null
let rafInertia = null

// 洗牌动画句柄
let shuffleRaf = null
let genId = 0
let shuffleTimers = []

const canReveal = computed(() => selected.value.length === SPREADS[spread.value].count)
const hasQuestion = computed(() => question.value.trim().length > 0)

const btnText = computed(() => {
  if (loading.value || dealing.value) return '正在抽牌…'
  const count = SPREADS[spread.value].count
  if (selected.value.length > 0) return `揭示牌意 (${selected.value.length}/${count})`
  return '揭示牌意'
})

const cardImg = (id) => `/divination/tarot/${id}.jpg`

// 相邻牌在弧上的水平弦长
const chord = computed(() => {
  const R = RADIUS_K * stageW.value
  return Math.max(6, 2 * R * Math.sin((ANGLE_STEP * Math.PI) / 180))
})

const clampM = (v) => Math.min(MAX_M, Math.max(MIN_M, v))

// 极坐标布局：圆心在舞台中心，牌向上拱成扇形
function layout(i) {
  const rel = i - M.value
  const deg = ANGLE_STEP * rel
  const o = (deg * Math.PI) / 180
  const R = RADIUS_K * stageW.value
  const x = R * Math.sin(o)
  let y = R * (1 - Math.cos(o))
  // 选中牌向上抽出 0.2 个牌高（参考站 Et：y += -0.2*U，U=牌高=52% 舞台高）
  if (selected.value.includes(i)) y -= 0.2 * stageH.value * 0.52
  return {
    transform: `translate(calc(-50% + ${x.toFixed(1)}px), calc(-50% + ${y.toFixed(1)}px)) rotate(${deg.toFixed(1)}deg)`,
    zIndex: String(Math.round(10 * rel) + 1000),
  }
}

function measure() {
  if (stageEl.value) {
    stageW.value = stageEl.value.clientWidth
    stageH.value = stageEl.value.clientHeight
  }
}

const tipText = computed(() => {
  if (stage.value === 'shuffle') return '正在洗牌…'
  if (stage.value === 'reveal') return '点击牌面，查看解读'
  return `静心凝神 · 写下问题，横划牌阵选 ${SPREADS[spread.value].count} 张牌（已选 ${selected.value.length}/${SPREADS[spread.value].count}）`
})

function clearShuffleTimers() {
  shuffleTimers.forEach((t) => clearTimeout(t))
  shuffleTimers = []
}

// ---- 三段洗牌动画（复刻参考站 Dt：每 200ms 换一次随机目标，共三段，620ms 后回弹）----
function runShuffle() {
  stage.value = 'shuffle'
  genId++
  const gen = genId
  const W = stageW.value
  const H = stageH.value
  const cards = [...(stageEl.value?.querySelectorAll('.deck-card') || [])]
  const poses = cards.map(() => ({ x0: 0, y0: 0, rot0: 0, x1: 0, y1: 0, rot1: 0 }))

  const newTarget = (p) => {
    p.x0 = p.x1
    p.y0 = p.y1
    p.rot0 = p.rot1
    p.x1 = (Math.random() - 0.5) * W * 0.6
    p.y1 = -0.16 * H + Math.random() * H * 0.28
    p.rot1 = 44 * (Math.random() - 0.5)
  }

  cards.forEach((el, k) => {
    newTarget(poses[k])
    el.style.transition = 'none'
  })

  let start = 0
  let lastSeg = -1
  cancelAnimationFrame(shuffleRaf)

  shuffleRaf = requestAnimationFrame(function loop(now) {
    if (gen !== genId) return
    if (!start) start = now
    const d = now - start
    const seg = Math.floor(d / 200)
    if (seg !== lastSeg) {
      lastSeg = seg
      cards.forEach((el, k) => newTarget(poses[k]))
    }
    if (d >= 620) {
      // 段1：300ms ease-in 归心（参考站 Dt 尾段）
      cards.forEach((el) => {
        el.style.transition = 'transform 300ms ease-in, filter 300ms ease'
        el.style.transform = 'translate(-50%, -50%) rotate(0deg)'
        el.style.filter = 'brightness(1)'
      })
      // 段2：归心后切到选牌阶段，440ms 回弹贝塞尔落回扇形（参考站 yt(!0)）
      shuffleTimers.push(
        setTimeout(() => {
          if (gen !== genId) return
          cards.forEach((el, k) => {
            el.style.transition = 'transform 440ms cubic-bezier(0.175, 0.885, 0.32, 1.275)'
            el.style.transform = layout(k).transform
          })
          stage.value = 'pick'
        }, 300),
      )
      shuffleTimers.push(
        setTimeout(() => {
          if (gen !== genId) return
          cards.forEach((el) => { el.style.transition = ''; el.style.filter = '' })
        }, 300 + 440),
      )
      return
    }
    const u = Math.min(1, (d - 200 * seg) / 160)
    const v = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2
    cards.forEach((el, k) => {
      const p = poses[k]
      const x = p.x0 + (p.x1 - p.x0) * v
      const y = p.y0 + (p.y1 - p.y0) * v
      const rot = p.rot0 + (p.rot1 - p.rot0) * v
      el.style.transform = `translate(calc(-50% + ${x.toFixed(1)}px), calc(-50% + ${y.toFixed(1)}px)) rotate(${rot.toFixed(1)}deg)`
      el.style.filter = `brightness(${(0.7 + 0.3 * v).toFixed(2)})`
    })
    shuffleRaf = requestAnimationFrame(loop)
  })
}

// ---- 拖拽 / 惯性 ----
function onPointerDown(e) {
  if (stage.value !== 'pick') return
  dragging = true
  moved = false
  O = 0
  vel = 0
  startX = lastX = e.clientX
  lastT = performance.now()
  cancelAnimationFrame(rafInertia)
}

function onPointerMove(e) {
  if (!dragging) return
  const now = performance.now()
  const dt = now - lastT
  const dx = e.clientX - lastX
  if (Math.abs(e.clientX - startX) > 6) moved = true
  if (moved) {
    O += dx
    if (dt > 0) vel = dx / dt
    lastX = e.clientX
    lastT = now
    if (!rafDrag) rafDrag = requestAnimationFrame(applyDrag)
  }
}

function applyDrag() {
  rafDrag = null
  if (O) {
    M.value = clampM(M.value - O / chord.value)
    O = 0
  }
}

function onPointerUp() {
  if (!dragging) return
  dragging = false
  cancelAnimationFrame(rafDrag)
  rafDrag = null
  if (moved && Math.abs(vel) > 0.02) startInertia()
}

function startInertia() {
  const tick = () => {
    M.value = clampM(M.value - (16 * vel) / chord.value)
    vel *= 0.94
    if (Math.abs(vel) >= 0.02) rafInertia = requestAnimationFrame(tick)
  }
  rafInertia = requestAnimationFrame(tick)
}

// 容器级 click 委托：从事件目标向上定位到牌
function onStageClick(e) {
  if (moved) {
    moved = false
    return
  }
  const card = e.target && e.target.closest ? e.target.closest('.deck-card') : null
  if (!card) return
  const i = Number(card.dataset.deckIndex)
  if (!Number.isNaN(i)) toggleBack(i)
}

function changeSpread(key) {
  // 重复点击当前已选中的牌阵类型：不刷新牌组
  if (key === spread.value) return
  // 正在抽牌/发牌过程中不切换，避免打断动画
  if (loading.value || dealing.value) return
  spread.value = key
  reset()
}

function toggleBack(i) {
  if (stage.value !== 'pick') return
  const idx = selected.value.indexOf(i)
  if (idx >= 0) {
    selected.value.splice(idx, 1)
  } else if (selected.value.length < SPREADS[spread.value].count) {
    selected.value.push(i)
  }
}

async function reveal() {
  if (!canReveal.value || loading.value || dealing.value) return
  if (!hasQuestion.value) {
    errorTip.value = '请先写下你想问的问题'
    return
  }
  loading.value = true
  dealing.value = true
  errorTip.value = ''
  try {
    const { data } = await request('/api/divination/tarot/', {
      method: 'POST',
      body: JSON.stringify({ spread: spread.value, question: question.value }),
    })
    if (data && data.code === 200) {
      result.value = data.data
      slotDone.value = result.value.cards.map(() => false)
      verdictStage.value = 'idle'
      stage.value = 'reveal'
      await nextTick()
      dealFlies()
    } else {
      errorTip.value = (data && data.message) || '抽牌失败，请再试一次'
    }
  } catch (err) {
    errorTip.value = '网络异常，抽牌失败，请稍后重试'
  } finally {
    loading.value = false
    dealing.value = false
  }
}

// ---- 飞牌：从牌堆抽到横排槽位，连贯翻牌 ----
async function dealFlies() {
  await nextTick()
  const box = stageEl.value?.getBoundingClientRect()
  if (!box) return
  const slotEls = [...stageEl.value.querySelectorAll('.slot')]
  const deckEls = selected.value.map((idx) =>
    stageEl.value.querySelector(`[data-deck-index="${idx}"]`),
  )
  const list = result.value.cards.map((card, i) => {
    const slot = slotEls[i]
    // 落位目标取卡片本体（.rcard）的宽高位置，避免把下方位置标签的高度算进去导致交接缩小
    const cardEl = slot ? slot.querySelector('.rcard') : null
    const refEl = cardEl || slot
    const s = refEl
      ? refEl.getBoundingClientRect()
      : { left: box.left, top: box.top, width: 80, height: 120 }
    const dRect = deckEls[i]?.getBoundingClientRect()
    const sw = s.width
    const sh = s.height
    // 起点沿用选中牌在扇形上的角度，落位时回正（参考站：fly 初始 rotate(rot)→0）
    const rot = ANGLE_STEP * ((selected.value[i] ?? 0) - M.value)
    let fromL
    let fromT
    let fromW
    let fromH
    let fromRot
    if (dRect && dRect.width) {
      fromW = dRect.width
      fromH = dRect.height
      fromL = dRect.left + dRect.width / 2 - fromW / 2 - box.left
      fromT = dRect.top + dRect.height / 2 - fromH / 2 - box.top
      fromRot = rot
    } else {
      fromW = sw
      fromH = sh
      fromL = box.width / 2 - fromW / 2
      fromT = 0.4 * box.height - fromH / 2
      fromRot = 0
    }
    return {
      key: i,
      card,
      reversed: !card.upright,
      started: false,
      flipped: false,
      slot: i,
      from: { left: fromL, top: fromT, w: fromW, h: fromH, rot: fromRot },
      to: { left: s.left - box.left, top: s.top - box.top, w: sw, h: sh, rot: 0 },
    }
  })
  flies.value = list
  // 起点坐标已缓存进飞牌对象，此时再把被抽走的牌从牌堆原位移除，避免底部残留残影
  dealt.value = true
  // 整堆牌直接离场，底部只留背景
  deckGone.value = true
  // 兜底：逐张内联隐藏牌堆牌，避免父级透明度过渡在个别浏览器上不生效
  stageEl.value?.querySelectorAll('.deck-card').forEach((el) => {
    el.style.display = 'none'
  })
  list.forEach((f, i) => shuffleTimers.push(setTimeout(() => startFly(f), 110 * i)))
}

function patchFly(key, patch) {
  flies.value = flies.value.map((x) => (x.key === key ? { ...x, ...patch } : x))
}

function startFly(f) {
  requestAnimationFrame(() => patchFly(f.key, { started: true }))
  shuffleTimers.push(setTimeout(() => patchFly(f.key, { flipped: true }), 312))
  shuffleTimers.push(
    setTimeout(() => {
      slotDone.value[f.slot] = true
      flies.value = flies.value.filter((x) => x.key !== f.key)
      // 全部牌翻完后，进入综合解答的汇聚 → 浮现流程
      if (slotDone.value.every(Boolean)) scheduleVerdict()
    }, 312 + 600 + 20),
  )
}

// 综合解答：先显示汇聚提示，停顿后浮现全局结论
function scheduleVerdict() {
  verdictStage.value = 'gathering'
  shuffleTimers.push(
    setTimeout(() => {
      verdictStage.value = 'revealed'
    }, 900),
  )
}

function onSlotClick(i) {
  if (stage.value !== 'reveal' || !slotDone.value[i]) return
  const card = result.value.cards[i]
  if (!card) return
  detailCard.value = card
}

function closeDetail() {
  detailCard.value = null
}

function suitLabel(suit) {
  return SUIT_LABEL[suit] || ''
}

function keywordList(card) {
  return String(card?.keywords || '')
    .split('·')
    .map((k) => k.trim())
    .filter(Boolean)
}

function flyStyle(f) {
  const p = f.started ? f.to : f.from
  return {
    left: `${p.left}px`,
    top: `${p.top}px`,
    width: `${p.w}px`,
    height: `${p.h}px`,
    transform: `rotate(${p.rot.toFixed(1)}deg)`,
  }
}

function reset() {
  stage.value = 'shuffle'
  selected.value = []
  result.value = null
  errorTip.value = ''
  loading.value = false
  dealing.value = false
  slotDone.value = []
  flies.value = []
  activeIdx.value = -1
  detailCard.value = null
  verdictStage.value = 'idle'
  dealt.value = false
  deckGone.value = false
  M.value = 38.5
  clearShuffleTimers()
  stageEl.value?.querySelectorAll('.deck-card').forEach((el) => {
    el.style.transition = ''
    el.style.transform = ''
    el.style.filter = ''
    el.style.display = ''
  })
  runShuffle()
}

onMounted(() => {
  measure()
  window.addEventListener('resize', measure)
  window.addEventListener('pointermove', onPointerMove)
  window.addEventListener('pointerup', onPointerUp)
  window.addEventListener('pointercancel', onPointerUp)
  runShuffle()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafDrag)
  cancelAnimationFrame(rafInertia)
  cancelAnimationFrame(shuffleRaf)
  clearShuffleTimers()
  window.removeEventListener('resize', measure)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup', onPointerUp)
  window.removeEventListener('pointercancel', onPointerUp)
})
</script>

<style scoped>
/* 外层：继承全站磨砂背景，窗口居中 */
.tarot-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 40px 16px 60px;
}

.tarot-window {
  width: 100%;
  max-width: 430px;
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  background: radial-gradient(130% 70% at 50% 112%, #8652d680, #0000 62%),
    radial-gradient(95% 62% at 50% 42%, #4824848c, #0000 72%), linear-gradient(#0a0514 0%, #150a2c 52%, #1e1040 100%);
  border: 1px solid rgba(134, 59, 255, 0.28);
  border-radius: 24px;
  box-shadow: 0 18px 50px rgba(5, 3, 16, 0.5);
  overflow: hidden;
}

/* ---- 头部 ---- */
.win-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 12px;
}

.win-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #f1ecff;
}

.win-reset {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(185, 140, 255, 0.35);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(226, 218, 255, 0.85);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.win-reset:hover {
  background: rgba(134, 59, 255, 0.25);
}

/* ---- 舞台 ---- */
.stage {
  position: relative;
  height: 380px;
  overflow: hidden;
  touch-action: pan-y;
  cursor: grab;
}

.stage:active {
  cursor: grabbing;
}

/* 牌堆层 */
.deck {
  position: absolute;
  inset: 0;
  transition: opacity 0.2s ease, filter 0.2s ease;
}

.deck--hidden {
  opacity: 0;
  filter: blur(8px);
  pointer-events: none;
}

/* 横排结果区 */
.cards-area {
  position: absolute;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 12px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.45s ease, filter 0.45s ease;
}

.cards-area.area--show {
  opacity: 1;
  pointer-events: auto;
}

.cards-area[data-count='1'] .slot { width: 48%; }
.cards-area[data-count='3'] .slot { width: 30%; }

.slot {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  min-width: 0;
  height: 100%;
  padding-top: 12px;
  display: flex;
}

.rcard {
  aspect-ratio: 2 / 3;
  perspective: 600px;
  flex: auto;
  width: auto;
  max-width: 100%;
  min-height: 0;
}

.rinner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
}

/* 翻牌过渡只发生在飞牌层；槽位落位瞬间切正面，不重播第二次翻牌 */
.fly .rinner {
  transition: transform 0.6s;
}

.rcard.flipped .rinner,
.fly.flipped .rinner {
  transform: rotateY(180deg);
}

.rface {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px #e8c66a29, 0 6px 18px rgba(5, 3, 16, 0.4);
}

.rback {
  background: linear-gradient(155deg, #3a1f6b 0%, #241547 55%, #160d30 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 飞牌未落位前：槽位显示为虚线空牌，不露实心牌背 */
.rcard.empty .rback {
  background: rgba(255, 255, 255, 0.04);
  border: 1px dashed rgba(232, 198, 106, 0.2);
  box-shadow: none;
}

.rcard.empty .back-pattern {
  display: none;
}

.rfront {
  transform: rotateY(180deg);
  background: linear-gradient(#2a1450 0%, #180b32 100%);
  border: 1px solid rgba(232, 198, 106, 0.35);
}

.rfront-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  border-radius: 4px;
  background: linear-gradient(#e8c66a1f 0%, #a970ff1f 100%);
  border: 0.5px solid #e8c66a47;
}

.rfront-img img {
  object-fit: cover;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  display: block;
}

.rfront-img img.rotated {
  transform: rotate(180deg);
}

/* 框外信息块：牌名 + 正逆位，位于卡片下方 */
.slot-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  margin-top: 6px;
}

.rname {
  color: #f4e6b8;
  text-align: center;
  letter-spacing: 1px;
  font-size: max(10px, min(2.2vw, 13px));
  font-weight: 500;
  line-height: 1.3;
}

.r-dir {
  border-radius: 8px;
  margin-top: 3px;
  padding: 1px 6px;
  font-size: max(9px, min(1.8vw, 11px));
  line-height: 1.4;
  display: inline-block;
}

.r-dir.upright {
  color: #e8c66a;
  background: #e8c66a29;
  border: 0.5px solid #e8c66a66;
}

.r-dir.reversed {
  color: #c9a6ff;
  background: #a970ff2e;
  border: 0.5px solid #a970ff73;
}

.slot-label {
  color: #a08fc6;
  font-size: 12px;
  letter-spacing: 1px;
  text-align: center;
}

/* 飞牌层 */
.fly {
  position: absolute;
  z-index: 1300;
  perspective: 600px;
  pointer-events: none;
  will-change: left, top, width, height, transform;
  transition: left 0.52s cubic-bezier(0.22, 0.61, 0.36, 1),
    top 0.52s cubic-bezier(0.22, 0.61, 0.36, 1),
    width 0.52s cubic-bezier(0.22, 0.61, 0.36, 1),
    height 0.52s cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 0.52s cubic-bezier(0.22, 0.61, 0.36, 1);
}

/* ---- 牌背（极坐标定位在舞台中心为圆心）---- */
.deck-card {
  position: absolute;
  top: 50%;
  left: 50%;
  height: 52%;
  aspect-ratio: 2 / 3;
  border-radius: 8px;
  border: 1px solid rgba(232, 198, 106, 0.32);
  background: linear-gradient(155deg, #3a1f6b 0%, #241547 55%, #160d30 100%);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05), 0 6px 16px rgba(5, 3, 16, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  will-change: transform, filter;
  -webkit-tap-highlight-color: transparent;
}

.deck-card:hover {
  filter: brightness(1.15);
}

.deck-card.picked {
  outline: 2px solid #e8c66a;
  box-shadow: 0 0 22px rgba(232, 198, 106, 0.45);
}

/* 金色圆环牌背纹 */
.back-pattern {
  aspect-ratio: 1;
  width: 74%;
  border: 1px solid rgba(232, 198, 106, 0.32);
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-pattern::before {
  content: '';
  position: absolute;
  inset: 11%;
  border-radius: 50%;
  background: repeating-conic-gradient(rgba(232, 198, 106, 0.85) 0deg 2deg, transparent 2deg 12deg);
  -webkit-mask: radial-gradient(circle, #0000 33%, #000 35%);
  mask: radial-gradient(circle, #0000 33%, #000 35%);
}

.back-pattern::after {
  content: '';
  width: 26%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, #f2dc9a 0%, #b8963f 70%, #7a5f22 100%);
  box-shadow: 0 0 10px rgba(242, 220, 155, 0.75);
}

.pick-no {
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translate(-50%);
  min-width: 16px;
  height: 16px;
  padding: 0 5px;
  border-radius: 999px;
  background: #e8c66a;
  color: #241141;
  font-size: 10px;
  font-weight: 600;
  line-height: 16px;
  text-align: center;
  z-index: 2;
}

.win-tip {
  text-align: center;
  color: rgba(226, 218, 255, 0.75);
  font-size: 13px;
  padding: 4px 20px 14px;
}

/* ---- 提问 ---- */
.win-question {
  padding: 0 20px 14px;
}

.question-input {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid rgba(134, 59, 255, 0.25);
  border-radius: 12px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.07);
  color: #f1ecff;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.question-input::placeholder {
  color: rgba(226, 218, 255, 0.4);
}

.question-input:focus {
  border-color: #863bff;
  box-shadow: 0 0 0 3px rgba(134, 59, 255, 0.18);
}

.win-action {
  display: flex;
  justify-content: center;
  padding: 0 20px 16px;
}

.primary-btn {
  padding: 12px 34px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(135deg, #863bff, #6a2fd6);
  box-shadow: 0 8px 20px rgba(134, 59, 255, 0.35);
  transition: filter 0.2s ease, opacity 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
  filter: brightness(1.08);
}

.primary-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.error-tip {
  margin: 0 20px 14px;
  color: #ff8a8a;
  font-size: 13px;
  text-align: center;
}

/* ---- 结果解读 ---- */
/* ---- 单牌详情弹框 ---- */
.detail-mask {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(5, 3, 16, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.detail-modal {
  position: relative;
  width: 100%;
  max-width: 380px;
  background: radial-gradient(130% 70% at 50% 112%, #8652d680, #0000 62%),
    radial-gradient(95% 62% at 50% 42%, #4824848c, #0000 72%), linear-gradient(#0a0514 0%, #150a2c 52%, #1e1040 100%);
  border: 1px solid rgba(134, 59, 255, 0.3);
  border-radius: 22px;
  box-shadow: 0 24px 60px rgba(3, 2, 12, 0.6);
  padding: 22px 22px 24px;
}

.detail-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
  color: rgba(226, 218, 255, 0.85);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}

.detail-close:hover {
  background: rgba(134, 59, 255, 0.25);
}

.dm-head {
  display: flex;
  gap: 16px;
  align-items: center;
}

.dm-img {
  width: 84px;
  aspect-ratio: 2 / 3;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid rgba(232, 198, 106, 0.35);
  flex: none;
}

.dm-img.rotated {
  transform: rotate(180deg);
}

.dm-meta h2 {
  color: #f1ecff;
  font-size: 22px;
  letter-spacing: 1px;
}

.dm-en {
  color: #a08fc6;
  font-size: 13px;
  margin: 6px 0 10px;
}

.dm-dir {
  display: inline-block;
  border-radius: 8px;
  padding: 2px 10px;
  font-size: 12px;
}

.dm-dir.up {
  color: #e8c66a;
  background: #e8c66a29;
  border: 0.5px solid #e8c66a66;
}

.dm-dir.down {
  color: #c9a6ff;
  background: #a970ff2e;
  border: 0.5px solid #a970ff73;
}

.dm-kw {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 18px 0;
}

.dm-kw-tag {
  font-size: 12px;
  color: #f4e6b8;
  background: rgba(232, 198, 106, 0.12);
  border: 0.5px solid rgba(232, 198, 106, 0.3);
  border-radius: 999px;
  padding: 4px 12px;
}

.dm-block h3 {
  color: #f1ecff;
  font-size: 16px;
  margin-bottom: 10px;
}

.dm-reading {
  color: #d8cfea;
  font-size: 14px;
  line-height: 1.8;
}

.dm-ai {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid rgba(134, 59, 255, 0.22);
}

.dm-ai .dm-reading {
  color: #e6dcff;
}

/* ---- 综合解答卡（结合全部卡牌的全局结论） ---- */
.verdict-wrap {
  margin: 2px 20px 0;
  min-height: 24px;
}

.verdict-gather {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(226, 218, 255, 0.6);
  font-size: 13px;
  letter-spacing: 1px;
  padding: 14px 0;
}

.verdict-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #e8c66a;
  box-shadow: 0 0 10px rgba(232, 198, 106, 0.8);
  animation: verdictPulse 1.2s ease-in-out infinite;
}

@keyframes verdictPulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.15); }
}

.verdict {
  position: relative;
  padding: 18px 18px 16px;
  border-radius: 18px;
  text-align: center;
  background: linear-gradient(160deg, rgba(134, 59, 255, 0.18), rgba(18, 9, 38, 0.45));
  border: 1px solid rgba(232, 198, 106, 0.3);
  box-shadow: 0 12px 30px rgba(5, 3, 16, 0.35), inset 0 0 26px rgba(232, 198, 106, 0.07);
  animation: verdictIn 0.85s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
}

@keyframes verdictIn {
  from { opacity: 0; transform: translateY(18px); filter: blur(5px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}

.verdict-ornament {
  color: #e8c66a;
  font-size: 14px;
  letter-spacing: 8px;
  text-indent: 8px;
}

.verdict-title {
  color: #f4e6b8;
  font-size: 15px;
  letter-spacing: 4px;
  text-indent: 4px;
  margin: 8px 0 10px;
}

.verdict-q {
  color: #a08fc6;
  font-size: 12px;
  margin-bottom: 8px;
}

.verdict-text {
  color: #e6dcff;
  font-size: 14px;
  line-height: 1.85;
}

/* ---- 等待解读加载层（仪式感） ---- */
.loading-mask {
  position: absolute;
  inset: 0;
  z-index: 1200;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: rgba(8, 4, 20, 0.55);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}

.loading-orbit {
  position: relative;
  width: 92px;
  height: 92px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orbit-ring {
  position: absolute;
  border-radius: 50%;
}

.ring-outer {
  inset: 0;
  border: 1px solid rgba(232, 198, 106, 0.3);
  border-top-color: #e8c66a;
  animation: orbitSpin 1.6s linear infinite;
}

.ring-inner {
  inset: 16px;
  border: 1px dashed rgba(169, 112, 255, 0.35);
  border-bottom-color: #a970ff;
  animation: orbitSpinRev 2.2s linear infinite;
}

.orbit-star {
  color: #f2dc9a;
  font-size: 22px;
  text-shadow: 0 0 12px rgba(242, 220, 155, 0.8);
  animation: starPulse 1.6s ease-in-out infinite;
}

.orbit-plate {
  position: absolute;
  inset: 0;
  animation: orbitSpin 3s linear infinite;
}

.orbit-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  margin: -3px 0 0 -3px;
  border-radius: 50%;
  background: #e8c66a;
  box-shadow: 0 0 8px rgba(232, 198, 106, 0.9);
}

.orbit-dot.d1 { transform: rotate(0deg) translate(46px) rotate(0deg); }
.orbit-dot.d2 { transform: rotate(120deg) translate(46px) rotate(-120deg); }
.orbit-dot.d3 { transform: rotate(240deg) translate(46px) rotate(-240deg); }

.loading-text {
  color: #f4e6b8;
  font-size: 15px;
  letter-spacing: 3px;
  text-indent: 3px;
}

.loading-sub {
  color: rgba(226, 218, 255, 0.55);
  font-size: 12px;
  letter-spacing: 1px;
}

@keyframes orbitSpin {
  to { transform: rotate(360deg); }
}

@keyframes orbitSpinRev {
  to { transform: rotate(-360deg); }
}

@keyframes starPulse {
  0%, 100% { opacity: 0.65; transform: scale(0.85); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* ---- 底部 Tab ---- */
.win-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 16px 16px;
  border-top: 1px solid rgba(134, 59, 255, 0.18);
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: 10px;
  border: 1px solid transparent;
  background: transparent;
  color: rgba(226, 218, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: linear-gradient(135deg, #863bff, #6a2fd6);
  color: #fff;
  box-shadow: 0 6px 16px rgba(134, 59, 255, 0.3);
}

.win-back {
  display: block;
  width: fit-content;
  margin: 4px auto 18px;
  padding: 9px 20px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(134, 59, 255, 0.3);
  color: rgba(226, 218, 255, 0.85);
  text-decoration: none;
  font-size: 13px;
}

.win-back:hover {
  background: rgba(134, 59, 255, 0.2);
}

@media (max-width: 480px) {
  .tarot-container {
    padding: 16px 12px 40px;
  }
}
</style>
