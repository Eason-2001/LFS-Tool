<template>
  <div class="game-container">
    <div class="game-layout">
      <section class="panel board-panel">
        <div class="topbar">
          <div class="slots">
            <div v-for="n in 8" :key="n" class="slot" :class="{ filled: n <= foundation }">
            <template v-if="completed[n - 1]">
              <span
                v-for="k in 3"
                :key="k"
                class="slot-back"
                :style="{ transform: `translate(${(k - 1) * 2}px, ${(k - 1) * 1.5}px)` }"
              ></span>
              <img :src="cardUrl(completed[n - 1][0])" class="slot-face" draggable="false" alt="" />
            </template>
          </div>
          </div>

          <div class="hud">
            <div class="hud-item">⏱ {{ time }}s</div>
            <button class="ctrl-btn" @click="newGame">🔄 重开</button>
          </div>
        </div>

        <div class="table-wrap">
        <div class="table">
          <div
            v-for="(pile, col) in columns"
            :key="col"
            class="col"
            :style="{ '--pile-step': pileStep(pile) }"
            :ref="(el) => (colEls[col] = el)"
            @click="onColClick(col)"
          >
            <div v-if="pile.length === 0" class="col-slot"></div>
            <div
              v-for="(card, idx) in pile"
              :key="card.id"
              class="card"
              :class="{ back: !card.faceUp, selected: isSelected(col, idx), 'deal-in': dealing, 'fly-in': card.fly, 'home-fly': card.home, 'is-drag-src': isDragSource(col, idx) }"
              :style="dealStyle(col, idx, card, pile)"
              @pointerdown="onCardDown($event, col, idx)"
            >
              <img v-if="card.faceUp" :src="cardUrl(card)" class="card-img" draggable="false" alt="" />
            </div>
          </div>
        </div>

        <div class="table-footer">
          <div class="stock-pile" :class="{ disabled: stock.length < 10 }" @click="dealStock">
            <div class="pile-layers">
              <div
                v-for="n in remainingDeals"
                :key="n"
                class="card back pile-back"
                :style="{ transform: `translate(-${(n - 1) * 2}px, ${(n - 1) * 1.5}px)` }"
              ></div>
            </div>
            <span class="stock-label">剩 {{ Math.floor(stock.length / 10) }} 次</span>
          </div>
        </div>
        </div>

        <div v-if="status === 'win'" class="result win">
          <span>🎉 恭喜完成蜘蛛纸牌！</span>
          <em>用时 {{ time }} 秒</em>
        </div>

      </section>

      <section class="panel rank-panel">
        <h2 class="rank-title">🏆 排行榜</h2>
        <div v-if="me" class="me-row">
          <img
            class="rank-avatar"
            :src="authState.user?.avatar || DEFAULT_AVATAR"
            alt="我的头像"
            @error="onAvatarError"
          />
          <span>我的名次 <b>#{{ me.rank }}</b> · 最佳 <b>{{ me.best }}s</b> · 共对局 {{ me.plays }} 次</span>
        </div>
        <ol v-if="leaderboard.length" class="rank-list">
          <li
            v-for="(item, i) in leaderboard"
            :key="item.username"
            :class="{ mine: item.username === authState.user?.username }"
          >
            <span class="rank-no">{{ i + 1 }}</span>
            <img
              class="rank-avatar"
              :src="item.avatar || DEFAULT_AVATAR"
              alt="头像"
              @error="onAvatarError"
            />
            <span class="rank-name">{{ item.nickname || item.username }}</span>
            <span class="rank-score">{{ item.best_score }}s</span>
          </li>
        </ol>
        <p v-else class="rank-empty">暂无成绩，快来拿下首名</p>
      </section>
    </div>

    <router-link to="/game" class="back-btn">🎮 返回游戏大厅</router-link>

    <!-- 拖拽浮层：跟随指针的牌组 -->
    <div v-if="drag" class="drag-layer" :style="{ left: drag.x + 'px', top: drag.y + 'px' }">
      <div
        v-for="(card, i) in drag.cards"
        :key="card.id"
        class="card drag-card"
        :style="{ '--top': i * STEP_FACE + 'px' }"
      >
        <img :src="cardUrl(card)" class="card-img" draggable="false" alt="" />
      </div>
    </div>

    <!-- 胜利礼花层 -->
    <canvas v-if="celebrating" ref="fxCanvas" class="fx-layer"></canvas>

    <!-- 规则轻提示 -->
    <div v-if="hint" class="toast">{{ hint }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { request } from '../api/request'
import { useAuth } from '../composables/useAuth'

const { state: authState } = useAuth()

const DEFAULT_AVATAR = '/default-avatar.svg'
const GAME_KEY = 'spider'

function onAvatarError(e) {
  e.target.src = DEFAULT_AVATAR
}

// 花色：符号 + 素材文件名 + 是否红色
const SUITS = [
  { sym: '♠', file: 'spades', red: false },
  { sym: '♥', file: 'hearts', red: true },
  { sym: '♦', file: 'diamonds', red: true },
  { sym: '♣', file: 'clubs', red: false }
]
const RANK_FILE = {
  1: 'ace', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6',
  7: '7', 8: '8', 9: '9', 10: '10', 11: 'jack', 12: 'queen', 13: 'king'
}
const COLS = 10

function cardUrl(card) {
  return `/cards/${RANK_FILE[card.rank]}_of_${card.suitFile}.png`
}

// 飞牌起点：牌堆在右下角，按目标列算从右下飞入的反方向偏移
// 背面（未翻开）只露窄边；正面（翻开）露出大半截便于看点数花色
const STEP_BACK = 10
const STEP_FACE = 30

// 一列除首张外的累计纵向步进，用于把列容器高度撑到与牌堆一致
function pileStep(pile) {
  let s = 0
  for (let k = 1; k < pile.length; k++) s += pile[k - 1].faceUp ? STEP_FACE : STEP_BACK
  return s + 'px'
}

function dealStyle(col, idx, card, pile) {
  let delay
  if (card.home) delay = card.homeDelay || 0
  else if (card.fly) delay = col * 40
  else delay = (card.dealIndex || 0) * 45
  let top = 0
  for (let k = 0; k < idx; k++) {
    top += pile[k].faceUp ? STEP_FACE : STEP_BACK
  }
  const animating = dealing.value || card.fly || card.home
  return {
    animationDelay: delay + 'ms',
    '--top': top + 'px',
    // 动画中按发牌顺序递增层叠：后发出的牌压在上层，避免飞途中被已落位的牌挡住
    zIndex: animating ? 20 + (card.dealIndex || 0) : undefined,
    '--fx': card.fx || ((9 - col) * 22 + 30) + 'px',
    '--fy': card.fy || '110px',
    '--hx': card.hx || '0px',
    '--hy': card.hy || '0px'
  }
}

const columns = ref([])
const stock = ref([])
const remainingDeals = computed(() => Math.floor(stock.value.length / 10))
const foundation = ref(0)
const completed = ref([]) // 已收走的各组 K→A，用于顶部槽位缩略
const selected = ref(null)
const drag = ref(null)
const status = ref('ready') // ready | play | win
const time = ref(0)
const dealing = ref(false) // 开局发牌动画播放中
const fly = ref(false) // 补牌飞行动画播放中
const homeAnim = ref(false) // 收牌飞入槽位动画播放中
const celebrating = ref(false) // 胜利礼花播放中
const fxCanvas = ref(null)
const hint = ref('') // 顶部规则提示

const leaderboard = ref([])
const me = ref(null)
const colEls = ref([])

let timerId = null
let dealTimer = null
let dealSeq = 0
let cardId = 0

// 礼花粒子引擎
let fxRaf = null
let fxLaunchTimer = null
let fxStopTimer = null
let hintTimer = null
let fxRockets = []
let fxParticles = []
const FX_COLORS = ['#f5d76e', '#e8c987', '#ff9a5a', '#ff7eb6', '#7ee8c9', '#b79bff', '#ff6b6b']

const gameKey = computed(() => GAME_KEY)

// ---------- 排行榜接口 ----------
async function fetchLeaderboard() {
  const { data } = await request('/api/game/leaderboard/?game=' + gameKey.value)
  if (data?.code === 200) {
    leaderboard.value = data.data.top || []
    me.value = data.data.me
  }
}

async function submitScore() {
  if (time.value <= 0) return
  const { data } = await request('/api/game/score/', {
    method: 'POST',
    body: JSON.stringify({ game: gameKey.value, score: time.value })
  })
  if (data?.code === 200) {
    me.value = { rank: data.data.rank, best: data.data.best, plays: data.data.plays }
  }
  fetchLeaderboard()
}

// ---------- 发牌 ----------
function buildDeck() {
  const deck = []
  for (let copy = 0; copy < 2; copy++) {
    for (const suit of SUITS) {
      for (let rank = 1; rank <= 13; rank++) {
        deck.push({
          id: cardId++,
          suitFile: suit.file,
          sym: suit.sym,
          red: suit.red,
          rank,
          faceUp: false
        })
      }
    }
  }
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[deck[i], deck[j]] = [deck[j], deck[i]]
  }
  return deck
}

function newGame() {
  stopTimer()
  stopCelebration()
  if (dealTimer) { clearTimeout(dealTimer); dealTimer = null }
  const deck = buildDeck()
  columns.value = Array.from({ length: COLS }, () => [])
  const layers = Array.from({ length: COLS }, (_, c) => (c < 4 ? 6 : 5))
  dealSeq = 0
  // 逐轮扫过 10 列发牌（对齐参考站发牌顺序），列底牌朝上
  for (let level = 0; level < 6; level++) {
    for (let c = 0; c < COLS; c++) {
      if (level >= layers[c]) continue
      const card = deck.pop()
      card.faceUp = level === layers[c] - 1
      card.dealIndex = dealSeq++
      columns.value[c].push(card)
    }
  }
  stock.value = deck
  foundation.value = 0
  completed.value = []
  selected.value = null
  drag.value = null
  time.value = 0
  status.value = 'ready'
  homeAnim.value = false
  // 先铺好牌，等布局完成后测量牌堆到每张牌的真实偏移，再播飞牌动画
  fly.value = false
  dealing.value = false
  nextTick(() => {
    requestAnimationFrame(() => {
      measureOffsets(pileOriginRect())
      dealing.value = true
      dealTimer = setTimeout(() => { dealing.value = false }, dealSeq * 45 + 550)
    })
  })
}

// 取右下牌堆最顶层（最上面那一层）那张牌的屏幕位置
function pileOriginRect() {
  const pileEl = document.querySelector('.pile-layers') || document.querySelector('.stock-pile')
  if (!pileEl) return null
  const backs = pileEl.querySelectorAll('.pile-back')
  const topEl = backs[backs.length - 1] || pileEl
  return topEl.getBoundingClientRect()
}

// 以牌堆顶层为起点，算出每张落点牌应飞的横纵偏移（左上角对齐）
function measureOffsets(origin) {
  if (!origin) return
  columns.value.forEach((pile, c) => {
    const colEl = colEls.value[c]
    if (!colEl) return
    const cardEls = colEl.querySelectorAll('.card')
    pile.forEach((card, i) => {
      const el = cardEls[i]
      if (!el) return
      const r = el.getBoundingClientRect()
      card.fx = Math.round(origin.left - r.left) + 'px'
      card.fy = Math.round(origin.top - r.top) + 'px'
    })
  })
}

// ---------- 选中规则 ----------
function getSelection(col, idx) {
  const pile = columns.value[col]
  if (!pile[idx] || !pile[idx].faceUp) return null
  // 标准蜘蛛：只有从这张牌一路点数连续递减到列尾的整段才可拖；
  // 中途一旦断开，断点以上（含本张）都不可移动，不能把不到列尾的一段抽走
  for (let i = idx + 1; i < pile.length; i++) {
    const prev = pile[i - 1]
    const cur = pile[i]
    if (!cur.faceUp || cur.rank !== prev.rank - 1) return null
  }
  return { col, idx, count: pile.length - idx }
}

function isSelected(col, idx) {
  const s = selected.value
  return !!(s && s.col === col && idx >= s.idx && idx < s.idx + s.count)
}

// 正在被拖拽的原位牌组：拖拽期间在原位隐藏，避免和浮层重复
function isDragSource(col, idx) {
  const d = drag.value
  return !!(d && d.col === col && idx >= d.idx && idx < d.idx + d.count)
}

function canPlace(cards, tcol) {
  const dest = columns.value[tcol]
  const first = cards[0]
  // 空列：任意牌（或任意连续组）都可以放入
  if (dest.length === 0) return true
  const top = dest[dest.length - 1]
  return top.faceUp && top.rank === first.rank + 1
}

// ---------- 移动 ----------
function doMove(srcCol, idx, tcol, count) {
  const pile = columns.value[srcCol]
  const cards = pile.splice(idx, count)
  columns.value[tcol].push(...cards)
  const src = columns.value[srcCol]
  if (src.length && !src[src.length - 1].faceUp) src[src.length - 1].faceUp = true
  selected.value = null
  checkFoundation(tcol)
  checkFoundation(srcCol)
}

function checkFoundation(col) {
  const pile = columns.value[col]
  if (pile.length < 13) return
  const tail = pile.slice(-13)
  let ok = true
  for (let i = 0; i < 13; i++) {
    // 凑齐 K→A 点数连续递减即收走（不限花色）
    if (tail[i].rank !== 13 - i) { ok = false; break }
  }
  if (!ok) return
  sendHome(col, tail)
}

// 成组牌逐张排队飞入顶部槽位，全部落位后再从列中移除并记入已收组
const HOME_STAGGER = 55 // 相邻两张起飞间隔 ms
const HOME_DUR = 450 // 单张飞行时长 ms
function sendHome(col, group) {
  homeAnim.value = true
  const slotIdx = completed.value.length
  nextTick(() => {
    requestAnimationFrame(() => {
      const slotEl = document.querySelectorAll('.slot')[slotIdx]
      const colEl = colEls.value[col]
      const els = colEl ? colEl.querySelectorAll('.card') : []
      group.forEach((card, i) => {
        card.home = true
        card.homeDelay = (group.length - 1 - i) * HOME_STAGGER // A 先飞，最后 K
        const el = els[els.length - 13 + i]
        if (slotEl && el) {
          const s = slotEl.getBoundingClientRect()
          const r = el.getBoundingClientRect()
          card.hx = Math.round(s.left + s.width / 2 - (r.left + r.width / 2)) + 'px'
          card.hy = Math.round(s.top + s.height / 2 - (r.top + r.height / 2)) + 'px'
        }
      })
      const total = (group.length - 1) * HOME_STAGGER + HOME_DUR + 80
      setTimeout(() => {
        const pile = columns.value[col]
        pile.splice(pile.length - 13, 13)
        // 成组收走后，翻开新露出的那张压住的背面牌
        if (pile.length && !pile[pile.length - 1].faceUp) pile[pile.length - 1].faceUp = true
        completed.value.push(group)
        foundation.value++
        homeAnim.value = false
        if (foundation.value === 8 && status.value !== 'win') {
          status.value = 'win'
          stopTimer()
          submitScore()
          startCelebration()
        } else {
          checkFoundation(col)
        }
      }, total)
    })
  })
}

// ---------- 拖拽（Pointer Events，鼠标 + 触屏统一） ----------
function onCardDown(e, col, idx) {
  if (status.value === 'win' || dealing.value || fly.value || homeAnim.value) return
  const sel = getSelection(col, idx)
  if (!sel) return
  e.preventDefault()
  ensurePlaying()

  const cards = columns.value[col].slice(sel.idx, sel.idx + sel.count)
  const rect = e.currentTarget.getBoundingClientRect()
  drag.value = {
    col: sel.col,
    idx: sel.idx,
    count: sel.count,
    cards,
    dx: e.clientX - rect.left,
    dy: e.clientY - rect.top,
    x: rect.left,
    y: rect.top,
    moved: false
  }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', onDragUp, { once: true })
  window.addEventListener('pointercancel', onDragCancel, { once: true })
}

// 拖拽被取消（移出窗口 / pointercancel）：清理浮层，牌回原位，不做移动
function onDragCancel() {
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', onDragUp)
  drag.value = null
}

function onDragMove(e) {
  if (!drag.value) return
  drag.value.x = e.clientX - drag.value.dx
  drag.value.y = e.clientY - drag.value.dy
  drag.value.moved = true
}

function columnAt(x, y) {
  const padX = 16 // 水平吸附范围：拖到列附近即可放下
  const padY = 12
  for (let c = 0; c < COLS; c++) {
    const el = colEls.value[c]
    if (!el) continue
    const r = el.getBoundingClientRect()
    // 纵向下界放宽：牌堆较长时指针落在列底附近仍能命中该列
    if (x >= r.left - padX && x <= r.right + padX && y >= r.top - padY && y <= r.bottom + 120) return c
  }
  return -1
}

function onDragUp(e) {
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointercancel', onDragCancel)
  const d = drag.value
  drag.value = null
  if (!d) return
  const c = columnAt(e.clientX, e.clientY)
  if (c >= 0 && c !== d.col && canPlace(d.cards, c)) {
    doMove(d.col, d.idx, c, d.count)
  } else if (!d.moved) {
    // 点按未拖动：转为点选，便于再点目标列放置
    selected.value = { col: d.col, idx: d.idx, count: d.count }
  }
}

// 点目标列：把已选中的牌组尝试放入（点选兜底，主交互为拖拽）
function onColClick(col) {
  if (!selected.value || status.value === 'win' || dealing.value || fly.value) return
  const sel = selected.value
  const cards = columns.value[sel.col].slice(sel.idx, sel.idx + sel.count)
  if (canPlace(cards, col)) doMove(sel.col, sel.idx, col, sel.count)
}

// ---------- 发牌堆 ----------
function dealStock() {
  if (status.value === 'win' || dealing.value || fly.value || homeAnim.value) return
  if (stock.value.length < 10) { showHint('牌堆已经发完了'); return }
  // 标准规则：只要还有空列，就不能从牌堆补牌
  if (columns.value.some((p) => p.length === 0)) {
    showHint('还有空列，先把空位填满才能发新一轮牌')
    return
  }
  ensurePlaying()
  // 先记录被抽走前牌堆顶层的位置，作为本次补牌的飞牌起点
  const origin = pileOriginRect()
  const sent = []
  for (let c = 0; c < COLS; c++) {
    const card = stock.value.pop()
    card.faceUp = true
    card.dealIndex = dealSeq++
    card.fly = true
    // 以列内现有顶牌推算落点，写好从牌堆顶到落点的偏移
    const colEl = colEls.value[c]
    if (colEl && origin) {
      const els = colEl.querySelectorAll('.card')
      const last = els[els.length - 1]
      const lr = last ? last.getBoundingClientRect() : colEl.getBoundingClientRect()
      const rTop = last ? lr.top + STEP_FACE : lr.top
      card.fx = Math.round(origin.left - lr.left) + 'px'
      card.fy = Math.round(origin.top - rTop) + 'px'
    }
    columns.value[c].push(card)
    sent.push(card)
  }
  fly.value = true
  setTimeout(() => {
    sent.forEach(k => { k.fly = false })
    fly.value = false
  }, COLS * 40 + 550)
  for (let c = 0; c < COLS; c++) checkFoundation(c)
}

// ---------- 计时 ----------
function ensurePlaying() {
  if (status.value === 'ready') {
    status.value = 'play'
    startTimer()
  }
}

function startTimer() {
  stopTimer()
  timerId = setInterval(() => { time.value++ }, 1000)
}

function stopTimer() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

// ---------- 胜利礼花 ----------
const fxRand = (min, max) => min + Math.random() * (max - min)

function explodeFx(x, y, color) {
  const n = 46
  for (let i = 0; i < n; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = fxRand(1.2, 4.6)
    const life = fxRand(50, 80)
    fxParticles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life, max: life,
      color: Math.random() > 0.75 ? FX_COLORS[(Math.random() * FX_COLORS.length) | 0] : color,
      size: fxRand(1.6, 3)
    })
  }
}

function launchRocket(canvas) {
  const W = canvas.width, H = canvas.height
  fxRockets.push({
    x: fxRand(W * 0.15, W * 0.85),
    y: H + 10,
    vy: -fxRand(9, 12),
    targetY: fxRand(H * 0.18, H * 0.42),
    color: FX_COLORS[(Math.random() * FX_COLORS.length) | 0]
  })
}

function fxLoop(canvas) {
  const ctx = canvas.getContext('2d')
  const W = canvas.width, H = canvas.height
  ctx.clearRect(0, 0, W, H)

  fxRockets = fxRockets.filter((r) => {
    r.y += r.vy
    r.vy += 0.05
    ctx.globalAlpha = 1
    ctx.fillStyle = r.color
    ctx.beginPath()
    ctx.arc(r.x, r.y, 2.4, 0, Math.PI * 2)
    ctx.fill()
    if (r.y <= r.targetY || r.vy >= -1) {
      explodeFx(r.x, r.y, r.color)
      return false
    }
    return true
  })

  fxParticles = fxParticles.filter((p) => {
    p.vx *= 0.985
    p.vy *= 0.985
    p.vy += 0.045
    p.x += p.vx
    p.y += p.vy
    p.life--
    const a = Math.max(p.life / p.max, 0)
    ctx.globalAlpha = a * (Math.random() > 0.25 ? 1 : 0.4)
    ctx.fillStyle = p.color
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
    ctx.fill()
    return p.life > 0
  })
  ctx.globalAlpha = 1

  if (fxRockets.length || fxParticles.length) {
    fxRaf = requestAnimationFrame(() => fxLoop(canvas))
  } else {
    stopCelebration()
  }
}

function startCelebration() {
  celebrating.value = true
  nextTick(() => {
    const canvas = fxCanvas.value
    if (!canvas) return
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    fxRockets = []
    fxParticles = []
    launchRocket(canvas)
    launchRocket(canvas)
    fxLaunchTimer = setInterval(() => launchRocket(canvas), 380)
    fxStopTimer = setTimeout(() => {
      if (fxLaunchTimer) { clearInterval(fxLaunchTimer); fxLaunchTimer = null }
    }, 4600)
    fxLoop(canvas)
  })
}

function stopCelebration() {
  if (fxRaf) { cancelAnimationFrame(fxRaf); fxRaf = null }
  if (fxLaunchTimer) { clearInterval(fxLaunchTimer); fxLaunchTimer = null }
  if (fxStopTimer) { clearTimeout(fxStopTimer); fxStopTimer = null }
  fxRockets = []
  fxParticles = []
  celebrating.value = false
}

// 顶部轻提示，若干秒后自动消失
function showHint(msg) {
  hint.value = msg
  if (hintTimer) clearTimeout(hintTimer)
  hintTimer = setTimeout(() => { hint.value = ''; hintTimer = null }, 2200)
}

newGame()
onMounted(fetchLeaderboard)
onBeforeUnmount(() => {
  stopTimer()
  stopCelebration()
  if (dealTimer) clearTimeout(dealTimer)
  if (hintTimer) clearTimeout(hintTimer)
  window.removeEventListener('pointermove', onDragMove)
})
</script>

<style scoped>
.game-container {
  max-width: 1560px;
  margin: 0 auto;
  padding: 72px 24px 80px;
}

.game-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  max-width: 1440px;
  margin: 0 auto;
  align-items: start;
}

.panel {
  background: rgba(18, 20, 26, 0.86);
  border: 1px solid rgba(201, 168, 106, 0.18);
  border-radius: 16px;
  padding: 24px;
  color: #f2ead8;
}

.board-panel {
  min-width: 0;
  min-height: 880px;
  padding: 32px 24px 40px;
  overflow: visible;
  /* 近黑墨绿绒布桌面 + 细绒纹理 + 暗角 */
  background:
    repeating-linear-gradient(45deg, rgba(255, 255, 255, 0.016) 0 1px, transparent 1px 5px),
    radial-gradient(ellipse at 50% -10%, #263b32 0%, #15231d 48%, #0a110e 100%);
  border-color: rgba(201, 168, 106, 0.22);
  box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.55), 0 18px 40px rgba(0, 0, 0, 0.4);
}

/* ---------- 顶部栏 ---------- */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

/* ---------- 右下角待发牌堆 ---------- */
.table-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 200px;
  min-height: clamp(64px, 8vw, 80px);
}

.stock-pile {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.stock-pile.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pile-layers {
  position: relative;
  width: clamp(60px, 7.4vw, 86px);
  aspect-ratio: 5 / 7;
}

.pile-back {
  position: absolute;
  inset: 0;
}

.stock-label {
  font-size: 14px;
  color: #e6d9bd;
}

.slots {
  display: flex;
  gap: 8px;
}

.slot {
  position: relative;
  width: clamp(46px, 5.4vw, 62px);
  aspect-ratio: 5 / 7;
  border: 1.5px dashed rgba(201, 168, 106, 0.32);
  border-radius: 8px;
}

.slot.filled {
  border: 1.5px solid rgba(232, 201, 135, 0.75);
  background: rgba(201, 168, 106, 0.18);
  box-shadow: inset 0 0 10px rgba(201, 168, 106, 0.15);
}

/* 槽位里已收组的薄牌堆：几层错位牌背 + 最上一张 K 牌面 */
.slot-back {
  position: absolute;
  inset: 0;
  border-radius: 8px;
  background: linear-gradient(135deg, #2b2b31 0%, #101013 100%);
  border: 1px solid rgba(201, 168, 106, 0.5);
}

.slot-face {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: fill;
  border-radius: 8px;
}

.hud {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hud-item {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(201, 168, 106, 0.28);
  border-radius: 10px;
  padding: 8px 16px;
  font-size: 16px;
  font-weight: 600;
  color: #e8c987;
}

.ctrl-btn {
  border: 1px solid rgba(201, 168, 106, 0.45);
  background: rgba(201, 168, 106, 0.12);
  color: #e8c987;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.ctrl-btn:hover { background: rgba(201, 168, 106, 0.26); }

/* ---------- 牌桌 ---------- */
.table-wrap {
  width: max-content;
  max-width: 100%;
  margin: 0 auto;
}

.table {
  display: flex;
  gap: 10px;
  min-width: max-content;
  padding-bottom: 10px;
}

.col {
  position: relative;
  width: clamp(60px, 7.4vw, 86px);
  height: calc(140% + var(--pile-step, 0px));
  min-height: 340px;
}

.col-slot {
  width: 100%;
  aspect-ratio: 5 / 7;
  border: 1.5px dashed rgba(201, 168, 106, 0.22);
  border-radius: 8px;
}

.card {
  position: absolute;
  left: 0;
  top: var(--top, 0);
  width: 100%;
  aspect-ratio: 5 / 7;
  border-radius: 8px;
  background: #f7f3ea;
  border: 1px solid rgba(201, 168, 106, 0.45);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.5);
  cursor: grab;
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: fill;
  border-radius: inherit;
  display: block;
  pointer-events: none;
}

/* 牌背：黑金花纹 + 内金框 */
.card.back {
  background:
    repeating-linear-gradient(45deg, rgba(201, 168, 106, 0.07) 0 1px, transparent 1px 6px),
    linear-gradient(135deg, #2b2b31 0%, #101013 100%);
  border: 1px solid rgba(201, 168, 106, 0.5);
}

.card.back::before {
  content: '';
  position: absolute;
  inset: 5px;
  border: 1px solid rgba(201, 168, 106, 0.35);
  border-radius: 6px;
}

.card.back::after {
  content: '♠';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(201, 168, 106, 0.32);
  font-size: 22px;
}

.card.selected {
  outline: 2px solid #e8c987;
  outline-offset: 1px;
  transform: translateY(-6px);
  z-index: 5;
}

/* 拖拽期间原位牌组隐藏，由跟随指针的浮层代替 */
.card.is-drag-src { visibility: hidden; }

/* 开局发牌动画：从右下牌堆直线飞入各列，干脆有力 */
@keyframes dealIn {
  0% { opacity: 0; transform: translate(var(--fx), var(--fy)) scale(0.96); }
  22% { opacity: 1; }
  100% { opacity: 1; transform: translate(0, 0) scale(1); }
}

/* 飞牌浮在牌堆之上，避免被摞在后面的牌堆盖住，看起来像从摞顶抽出 */
.card.deal-in,
.card.fly-in { z-index: 30; }
.card.deal-in { animation: dealIn 0.45s cubic-bezier(0.3, 0.7, 0.3, 1) both; }
.card.fly-in { animation: dealIn 0.4s cubic-bezier(0.3, 0.7, 0.3, 1) both; }

/* 凑齐 K→A 后逐张向上飞入顶部槽位，落槽时收拢缩小 */
@keyframes homeFly {
  0% { opacity: 1; transform: translate(0, 0) scale(1); }
  55% { opacity: 1; }
  100% { opacity: 0.9; transform: translate(var(--hx), var(--hy)) scale(0.5); }
}
.card.home-fly { z-index: 40; animation: homeFly 0.45s cubic-bezier(0.3, 0.7, 0.3, 1) both; }

/* 拖拽浮层 */
.drag-layer {
  position: fixed;
  z-index: 100;
  pointer-events: none;
  width: clamp(60px, 7.4vw, 86px);
}

/* 胜利礼花：全屏置顶、不挡点击 */
.fx-layer {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 200;
  pointer-events: none;
}

/* 顶部规则轻提示 */
.toast {
  position: fixed;
  top: 84px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 180;
  max-width: 80vw;
  padding: 10px 20px;
  border-radius: 12px;
  background: rgba(20, 22, 28, 0.92);
  border: 1px solid rgba(201, 168, 106, 0.45);
  color: #e8c987;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.3px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.5);
  animation: toastIn 0.25s ease both;
  pointer-events: none;
}

@keyframes toastIn {
  from { opacity: 0; transform: translate(-50%, -8px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

.drag-card {
  cursor: grabbing;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45);
}

.result {
  margin-top: 18px;
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result.win { color: #e8c987; }
.result em { font-style: normal; font-size: 14px; color: #d8cdb2; }

/* ---------- 排行榜 ---------- */
.rank-title { font-size: 18px; margin-bottom: 14px; }

.me-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(201, 168, 106, 0.14);
  border: 1px solid rgba(201, 168, 106, 0.3);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 14px;
  font-size: 14px;
  color: #ece0c2;
}

.rank-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(201, 168, 106, 0.25);
  flex-shrink: 0;
  background: #fff;
}

.me-row b { color: #fff; }

.rank-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }

.rank-list li {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(201, 168, 106, 0.12);
}

.rank-list li.mine {
  background: rgba(201, 168, 106, 0.18);
  border: 1px solid rgba(201, 168, 106, 0.34);
}

.rank-no { width: 28px; font-weight: 700; color: #d8c28a; }
.rank-name { flex: 1; font-size: 15px; color: #fff; }
.rank-score { font-weight: 600; color: #fff; }
.rank-empty { text-align: center; color: #9aa69a; font-size: 14px; padding: 16px 0; }

.back-btn {
  display: block;
  width: fit-content;
  margin: 28px auto 0;
  padding: 10px 22px;
  border-radius: 999px;
  background: rgba(201, 168, 106, 0.12);
  border: 1px solid rgba(201, 168, 106, 0.4);
  color: #e8c987;
  text-decoration: none;
  font-size: 14px;
}

.back-btn:hover { background: rgba(201, 168, 106, 0.24); }

@media (max-width: 900px) {
  .game-layout { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .game-container { padding: 24px 12px 48px; }
  .panel { padding: 12px; }
}
</style>
