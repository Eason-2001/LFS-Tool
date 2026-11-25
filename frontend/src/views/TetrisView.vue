<template>
  <div class="game-container">
    <div class="game-layout">
      <section class="panel game-panel">
        <div class="hud">
          <div class="hud-item">得分 <b>{{ state.score }}</b></div>
          <div class="hud-item">最高 <b>{{ state.best }}</b></div>
          <div class="hud-item">等级 <b>{{ state.level }}</b></div>
          <div class="hud-item">行数 <b>{{ state.lines }}</b></div>
          <div class="hud-item" :class="{ combo: state.combo > 0 }">
            {{ state.combo > 0 ? `连击 x${state.combo}` : '连击 --' }}
          </div>
        </div>

        <div class="preview-row">
          <div class="next-box">
            <span>暂存</span>
            <canvas ref="holdRef" class="next-canvas"></canvas>
          </div>
          <div class="next-box">
            <span>下一块</span>
            <canvas ref="nextRef" class="next-canvas"></canvas>
          </div>
        </div>

        <canvas ref="canvasRef" class="game-canvas"></canvas>

        <div v-if="state.status === 'play' || state.status === 'pause' || state.status === 'clearing'" class="touch-controls">
          <button class="ctrl-btn" @click="holdPiece">⇄</button>
          <button class="ctrl-btn" @click="moveLeft">←</button>
          <button class="ctrl-btn" @click="rotatePiece">⟳</button>
          <button class="ctrl-btn" @click="moveRight">→</button>
          <button class="ctrl-btn" @click="softDrop">↓</button>
          <button class="ctrl-btn ctrl-drop" @click="hardDrop">⤓</button>
        </div>

        <button
          v-if="state.status === 'play' || state.status === 'pause'"
          class="touch-btn"
          @click="togglePause"
        >
          {{ state.status === 'pause' ? '▶ 继续' : '⏸ 暂停' }}
        </button>
        <p class="tips">{{ isTouch ? '⇄ 暂存 · ← → 移动 · ⟳ 旋转 · ↓ 软降 · ⤓ 硬降' : '← → 移动 · ↑ 旋转 · ↓ 软降 · 空格 硬降 · C 暂存 · P 暂停 · 回车 开始' }}</p>
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
          <span>我的名次 <b>#{{ me.rank }}</b> · 最佳 <b>{{ me.best }}</b> 分 · 共对局 {{ me.plays }} 次</span>
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
            <span class="rank-score">{{ item.best_score }} 分</span>
          </li>
        </ol>
        <p v-else class="rank-empty">暂无成绩，快来拿下首名</p>
      </section>
    </div>

    <router-link to="/game" class="back-btn">🎮 返回游戏大厅</router-link>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { request } from '../api/request'
import { useAuth } from '../composables/useAuth'

const { state: authState } = useAuth()

const DEFAULT_AVATAR = '/default-avatar.svg'
const GAME_KEY = 'tetris'
const BEST_KEY = 'lfs-tetris-best'

function onAvatarError(e) {
  e.target.src = DEFAULT_AVATAR
}

// ---------- 棋盘常量 ----------
const COLS = 10
const ROWS = 20
const CELL = 30
const BOARD_W = COLS * CELL
const BOARD_H = ROWS * CELL
const CLEAR_MS = 240 // 消行闪光时长

// 7 种四格骨牌：矩阵 + 色相（注意不要用 0，0 作为空值标记）
const PIECES = [
  { name: 'I', hue: 190, m: [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]] },
  { name: 'O', hue: 45, m: [[1, 1], [1, 1]] },
  { name: 'T', hue: 275, m: [[0, 1, 0], [1, 1, 1], [0, 0, 0]] },
  { name: 'S', hue: 145, m: [[0, 1, 1], [1, 1, 0], [0, 0, 0]] },
  { name: 'Z', hue: 350, m: [[1, 1, 0], [0, 1, 1], [0, 0, 0]] },
  { name: 'J', hue: 220, m: [[1, 0, 0], [1, 1, 1], [0, 0, 0]] },
  { name: 'L', hue: 30, m: [[0, 0, 1], [1, 1, 1], [0, 0, 0]] }
]

const LINE_SCORE = [0, 100, 300, 500, 800]

const canvasRef = ref(null)
const nextRef = ref(null)
const holdRef = ref(null)
const isTouch = ref(false)

const state = reactive({
  score: 0,
  best: 0,
  level: 1,
  lines: 0,
  combo: -1, // -1 表示当前无连击
  status: 'menu' // menu | play | clearing | pause | over
})

const leaderboard = ref([])
const me = ref(null)

// 运行时变量
let ctx = null
let nextCtx = null
let holdCtx = null
let dpr = 1
let rafId = null
let last = performance.now()
let dropTimer = 0
let board = []
let cur = null
let next = null
let hold = null
let holdUsed = false
let bag = []
let clearingRows = []
let clearTimer = 0
let audio = null

// ---------- 接口 ----------
async function fetchLeaderboard() {
  const { data } = await request('/api/game/leaderboard/?game=' + GAME_KEY)
  if (data?.code === 200) {
    leaderboard.value = data.data.top || []
    me.value = data.data.me
  }
}

async function submitScore() {
  if (state.score <= 0) return
  const { data } = await request('/api/game/score/', {
    method: 'POST',
    body: JSON.stringify({ game: GAME_KEY, score: state.score })
  })
  if (data?.code === 200) {
    me.value = { rank: data.data.rank, best: data.data.best, plays: data.data.plays }
  }
  fetchLeaderboard()
}

// ---------- 音效（WebAudio 合成，无外部文件） ----------
function ensureAudio() {
  if (!audio) {
    try { audio = new (window.AudioContext || window.webkitAudioContext)() } catch (e) { audio = null }
  }
  if (audio && audio.state === 'suspended') audio.resume()
}

function beep(freq, dur = 0.08, type = 'square', vol = 0.12, slide = 0) {
  if (!audio) return
  const t = audio.currentTime
  const o = audio.createOscillator()
  const g = audio.createGain()
  o.type = type
  o.frequency.setValueAtTime(freq, t)
  if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(30, freq + slide), t + dur)
  g.gain.setValueAtTime(vol, t)
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur)
  o.connect(g)
  g.connect(audio.destination)
  o.start(t)
  o.stop(t + dur + 0.02)
}

// ---------- 方块逻辑 ----------
// 7-Bag：一袋 7 种块洗牌依次发，保证分布均匀，不会长期缺某一种
function drawFromBag() {
  if (!bag.length) {
    bag = [0, 1, 2, 3, 4, 5, 6].sort(() => Math.random() - 0.5)
  }
  const i = bag.pop()
  const p = PIECES[i]
  return { name: p.name, hue: p.hue, m: p.m.map(row => row.slice()) }
}

function emptyBoard() {
  return Array.from({ length: ROWS }, () => Array(COLS).fill(null))
}

function collide(m, px, py) {
  for (let r = 0; r < m.length; r++) {
    for (let c = 0; c < m[r].length; c++) {
      if (!m[r][c]) continue
      const x = px + c
      const y = py + r
      if (x < 0 || x >= COLS || y >= ROWS) return true
      if (y >= 0 && board[y][x] !== null) return true
    }
  }
  return false
}

// 顺时针旋转矩阵
function rotateMatrix(m) {
  const n = m.length
  const res = Array.from({ length: n }, () => Array(n).fill(0))
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      res[c][n - 1 - r] = m[r][c]
    }
  }
  return res
}

function resetPosition(p) {
  p.x = Math.floor((COLS - p.m[0].length) / 2)
  p.y = 0
}

function spawn() {
  cur = next || drawFromBag()
  next = drawFromBag()
  resetPosition(cur)
  if (collide(cur.m, cur.x, cur.y)) {
    gameOver()
  } else {
    drawNext()
  }
}

function lockPiece() {
  for (let r = 0; r < cur.m.length; r++) {
    for (let c = 0; c < cur.m[r].length; c++) {
      if (!cur.m[r][c]) continue
      const y = cur.y + r
      const x = cur.x + c
      if (y >= 0) board[y][x] = cur.hue
    }
  }

  const full = []
  for (let r = 0; r < ROWS; r++) {
    if (board[r].every(v => v !== null)) full.push(r)
  }

  if (full.length) {
    // 进入消行动画状态，闪光结束后再真正移除
    clearingRows = full
    clearTimer = 0
    state.status = 'clearing'
    applyClearScore(full.length)
  } else {
    // 本次没消行，连击中断
    state.combo = -1
    spawn()
  }
  holdUsed = false
}

function applyClearScore(cleared) {
  state.combo += 1
  const base = LINE_SCORE[cleared] * state.level
  const comboBonus = state.combo > 0 ? 50 * state.combo * state.level : 0
  state.score += base + comboBonus
  state.lines += cleared
  state.level = Math.floor(state.lines / 10) + 1
  if (cleared === 4) {
    beep(660, 0.18, 'triangle', 0.16, 320)
  } else {
    beep(520 + cleared * 120, 0.12, 'triangle', 0.14, 200)
  }
}

function finishClear() {
  // 从下往上移除闪光行，顶部补空行
  for (const r of clearingRows.slice().sort((a, b) => b - a)) {
    board.splice(r, 1)
    board.unshift(Array(COLS).fill(null))
  }
  clearingRows = []
  state.status = 'play'
  spawn()
}

function moveLeft() {
  if (state.status !== 'play') return
  if (!collide(cur.m, cur.x - 1, cur.y)) cur.x--
}

function moveRight() {
  if (state.status !== 'play') return
  if (!collide(cur.m, cur.x + 1, cur.y)) cur.x++
}

function softDrop() {
  if (state.status !== 'play') return
  if (!collide(cur.m, cur.x, cur.y + 1)) {
    cur.y++
    state.score += 1
  } else {
    lockPiece()
  }
}

function hardDrop() {
  if (state.status !== 'play') return
  let dist = 0
  while (!collide(cur.m, cur.x, cur.y + 1)) {
    cur.y++
    dist++
  }
  state.score += dist * 2
  lockPiece()
}

function rotatePiece() {
  if (state.status !== 'play') return
  const rm = rotateMatrix(cur.m)
  // 简单墙踢：原位撞了就左右挪一列试
  for (const kick of [0, -1, 1, -2, 2]) {
    if (!collide(rm, cur.x + kick, cur.y)) {
      cur.m = rm
      cur.x += kick
      beep(360, 0.05, 'square', 0.08)
      return
    }
  }
}

function holdPiece() {
  if (state.status !== 'play' || holdUsed) return
  ensureAudio()
  const current = cur
  if (hold) {
    cur = hold
    hold = current
    resetPosition(cur)
    if (collide(cur.m, cur.x, cur.y)) {
      gameOver()
      return
    }
  } else {
    hold = current
    cur = next
    next = drawFromBag()
    resetPosition(cur)
  }
  holdUsed = true
  beep(440, 0.06, 'triangle', 0.1)
  drawNext()
  drawHold()
}

function dropInterval() {
  return Math.max(90, 750 - (state.level - 1) * 60)
}

function tick() {
  if (collide(cur.m, cur.x, cur.y + 1)) lockPiece()
  else cur.y++
}

function resetGame() {
  board = emptyBoard()
  state.score = 0
  state.level = 1
  state.lines = 0
  state.combo = -1
  dropTimer = 0
  bag = []
  hold = null
  holdUsed = false
  clearingRows = []
  next = drawFromBag()
  spawn()
  state.status = 'play'
}

function gameOver() {
  state.status = 'over'
  if (state.score > state.best) {
    state.best = state.score
    try { localStorage.setItem(BEST_KEY, String(state.best)) } catch (e) {}
  }
  beep(160, 0.4, 'sawtooth', 0.16, -120)
  submitScore()
}

function togglePause() {
  ensureAudio()
  if (state.status === 'play') state.status = 'pause'
  else if (state.status === 'pause') state.status = 'play'
}

// ---------- 绘制 ----------
function roundRect(x, y, w, h, r) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

function drawCell(x, y, hue, size = CELL, alpha = 1) {
  ctx.save()
  ctx.globalAlpha = alpha
  ctx.shadowColor = `hsl(${hue} 90% 60%)`
  ctx.shadowBlur = 6
  ctx.fillStyle = `hsl(${hue} 85% 55%)`
  roundRect(x + 2, y + 2, size - 4, size - 4, 5)
  ctx.fill()
  ctx.restore()
}

// 落点影子：沿当前位置向下找到最远可落行
function ghostY() {
  let y = cur.y
  while (!collide(cur.m, cur.x, y + 1)) y++
  return y
}

function draw() {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.fillStyle = '#070b16'
  ctx.fillRect(0, 0, BOARD_W, BOARD_H)

  // 网格
  ctx.strokeStyle = 'rgba(255,255,255,0.06)'
  ctx.lineWidth = 1
  for (let c = 1; c < COLS; c++) {
    ctx.beginPath()
    ctx.moveTo(c * CELL, 0)
    ctx.lineTo(c * CELL, BOARD_H)
    ctx.stroke()
  }
  for (let r = 1; r < ROWS; r++) {
    ctx.beginPath()
    ctx.moveTo(0, r * CELL)
    ctx.lineTo(BOARD_W, r * CELL)
    ctx.stroke()
  }

  // 已落块（消行中的行做白闪）
  const flashing = state.status === 'clearing'
  const flashAlpha = flashing ? 0.4 + 0.6 * Math.abs(Math.sin(clearTimer / 40)) : 1
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const v = board[r][c]
      if (v === null) continue
      if (flashing && clearingRows.includes(r)) {
        ctx.save()
        ctx.globalAlpha = flashAlpha
        ctx.fillStyle = '#ffffff'
        roundRect(c * CELL + 2, r * CELL + 2, CELL - 4, CELL - 4, 5)
        ctx.fill()
        ctx.restore()
      } else {
        drawCell(c * CELL, r * CELL, v)
      }
    }
  }

  // 影子 + 当前块
  if (cur && (state.status === 'play' || state.status === 'pause')) {
    const gy = ghostY()
    if (gy !== cur.y) {
      for (let r = 0; r < cur.m.length; r++) {
        for (let c = 0; c < cur.m[r].length; c++) {
          if (!cur.m[r][c]) continue
          const y = gy + r
          const x = cur.x + c
          if (y >= 0) drawCell(x * CELL, y * CELL, cur.hue, CELL, 0.22)
        }
      }
    }
    for (let r = 0; r < cur.m.length; r++) {
      for (let c = 0; c < cur.m[r].length; c++) {
        if (!cur.m[r][c]) continue
        const y = cur.y + r
        const x = cur.x + c
        if (y >= 0) drawCell(x * CELL, y * CELL, cur.hue)
      }
    }
  }

  // 覆盖层
  if (state.status === 'menu') {
    ctx.fillStyle = 'rgba(4,7,15,0.72)'
    ctx.fillRect(0, 0, BOARD_W, BOARD_H)
    centerText('俄 罗 斯 方 块', BOARD_H / 2 - 60, 28, '#e6fbff', 20)
    centerText('堆叠消行 · 连击加成 · 暂存换块', BOARD_H / 2 - 16, 14, '#9fd8ff', 6)
    centerText(isTouch.value ? '点按下方按钮开始' : '按 回车 开始', BOARD_H / 2 + 40, 18, '#00e5ff', 10)
  } else if (state.status === 'pause') {
    ctx.fillStyle = 'rgba(4,7,15,0.6)'
    ctx.fillRect(0, 0, BOARD_W, BOARD_H)
    centerText('已 暂 停', BOARD_H / 2 - 10, 32, '#cfe3ff', 14)
    centerText(isTouch.value ? '点按继续' : '按 P 继续', BOARD_H / 2 + 34, 15, '#5f7ba6')
  } else if (state.status === 'over') {
    ctx.fillStyle = 'rgba(4,7,15,0.78)'
    ctx.fillRect(0, 0, BOARD_W, BOARD_H)
    centerText('游 戏 结 束', BOARD_H / 2 - 56, 32, '#ff5d8f', 18)
    centerText('本局得分 ' + state.score, BOARD_H / 2 - 6, 22, '#e6fbff', 8)
    centerText(isTouch.value ? '点按再来一局' : '按 回车 再来一局', BOARD_H / 2 + 44, 16, '#00e5ff', 8)
  }
}

function centerText(txt, y, size, fill, blur = 0) {
  ctx.save()
  ctx.font = `700 ${size}px "Segoe UI","Microsoft YaHei",sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  if (blur) { ctx.shadowColor = fill; ctx.shadowBlur = blur }
  ctx.fillStyle = fill
  ctx.fillText(txt, BOARD_W / 2, y)
  ctx.restore()
}

// 通用：把一个小块画到预览画布（next / hold 共用）
function drawPieceTo(targetCtx, piece) {
  if (!targetCtx) return
  const np = 30
  targetCtx.setTransform(dpr, 0, 0, dpr, 0, 0)
  targetCtx.clearRect(0, 0, 4 * np, 4 * np)
  if (!piece) return
  const m = piece.m
  let minR = 99, maxR = -1, minC = 99, maxC = -1
  m.forEach((row, r) => row.forEach((v, c) => {
    if (v) {
      minR = Math.min(minR, r); maxR = Math.max(maxR, r)
      minC = Math.min(minC, c); maxC = Math.max(maxC, c)
    }
  }))
  const w = (maxC - minC + 1) * np
  const h = (maxR - minR + 1) * np
  const ox = (4 * np - w) / 2
  const oy = (4 * np - h) / 2
  m.forEach((row, r) => row.forEach((v, c) => {
    if (!v) return
    targetCtx.save()
    targetCtx.shadowColor = `hsl(${piece.hue} 90% 60%)`
    targetCtx.shadowBlur = 5
    targetCtx.fillStyle = `hsl(${piece.hue} 85% 55%)`
    const x = ox + (c - minC) * np
    const y = oy + (r - minR) * np
    targetCtx.fillRect(x + 2, y + 2, np - 4, np - 4)
    targetCtx.restore()
  }))
}

function drawNext() { drawPieceTo(nextCtx, next) }
function drawHold() { drawPieceTo(holdCtx, hold) }

function frame(now) {
  const dt = Math.min(0.033, (now - last) / 1000)
  last = now

  if (state.status === 'clearing') {
    clearTimer += dt * 1000
    if (clearTimer >= CLEAR_MS) finishClear()
  } else if (state.status === 'play') {
    dropTimer += dt * 1000
    if (dropTimer >= dropInterval()) {
      dropTimer = 0
      tick()
    }
  }
  draw()
  rafId = requestAnimationFrame(frame)
}

// ---------- 键盘 ----------
function onKeyDown(e) {
  ensureAudio()
  if (['ArrowLeft', 'ArrowRight', 'ArrowDown', 'ArrowUp', 'Space'].includes(e.code)) e.preventDefault()
  if (e.code === 'Space') {
    if (state.status === 'menu' || state.status === 'over') resetGame()
    else if (state.status === 'play') hardDrop()
    return
  }
  if (e.code === 'Enter') {
    if (state.status === 'menu' || state.status === 'over') resetGame()
    return
  }
  if (e.code === 'KeyP' || e.code === 'Escape') {
    togglePause()
    return
  }
  if (e.code === 'KeyC' || e.code === 'ShiftLeft' || e.code === 'ShiftRight') {
    holdPiece()
    return
  }
  if (state.status !== 'play') return
  switch (e.code) {
    case 'ArrowLeft': case 'KeyA': moveLeft(); break
    case 'ArrowRight': case 'KeyD': moveRight(); break
    case 'ArrowDown': case 'KeyS': softDrop(); break
    case 'ArrowUp': case 'KeyX': case 'KeyW': rotatePiece(); break
  }
}

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  nextCtx = nextRef.value.getContext('2d')
  holdCtx = holdRef.value.getContext('2d')
  dpr = Math.min(2, window.devicePixelRatio || 1)
  canvasRef.value.width = BOARD_W * dpr
  canvasRef.value.height = BOARD_H * dpr
  nextRef.value.width = 120 * dpr
  nextRef.value.height = 120 * dpr
  holdRef.value.width = 120 * dpr
  holdRef.value.height = 120 * dpr
  isTouch.value =
    (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) ||
    'ontouchstart' in window
  board = emptyBoard()
  try { state.best = Number(localStorage.getItem(BEST_KEY)) || 0 } catch (e) { state.best = 0 }
  fetchLeaderboard()
  window.addEventListener('keydown', onKeyDown)
  rafId = requestAnimationFrame(frame)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<style scoped>
.game-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 72px 24px 80px;
}

.game-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  align-items: start;
}

.panel {
  background: rgba(20, 24, 50, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  color: #fff;
}

.game-panel {
  min-width: 0;
}

.hud {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.hud-item {
  font-size: 14px;
  color: #9aa4c4;
}

.hud-item b {
  color: #fff;
  font-size: 18px;
  margin-left: 4px;
}

.hud-item.combo {
  color: #ffd166;
  font-weight: 700;
}

.preview-row {
  display: flex;
  justify-content: center;
  gap: 28px;
  margin-bottom: 14px;
}

.next-box {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #9aa4c4;
}

.next-canvas {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
}

.game-canvas {
  display: block;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  border-radius: 12px;
  background: #070b16;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.touch-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 14px;
}

.ctrl-btn {
  width: 48px;
  height: 44px;
  border: 1px solid rgba(134, 59, 255, 0.35);
  border-radius: 12px;
  background: rgba(134, 59, 255, 0.1);
  color: #d9c9ff;
  font-size: 18px;
  cursor: pointer;
}

.ctrl-btn:active {
  background: rgba(134, 59, 255, 0.22);
}

.ctrl-drop {
  color: #ffd166;
  border-color: rgba(255, 209, 102, 0.35);
}

.touch-btn {
  display: block;
  margin: 14px auto 0;
  padding: 10px 26px;
  border: 1px solid rgba(134, 59, 255, 0.35);
  border-radius: 999px;
  background: rgba(134, 59, 255, 0.1);
  color: #d9c9ff;
  font-size: 15px;
  cursor: pointer;
}

.touch-btn:active {
  background: rgba(134, 59, 255, 0.18);
}

.tips {
  text-align: center;
  margin-top: 14px;
  color: #9aa4c4;
  font-size: 13px;
}

.rank-panel {
  color: #fff;
}

.rank-title {
  font-size: 18px;
  margin-bottom: 14px;
}

.me-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(134, 59, 255, 0.24);
  border: 1px solid rgba(134, 59, 255, 0.36);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 14px;
  font-size: 14px;
  color: #f0e7ff;
}

.rank-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(134, 59, 255, 0.2);
  flex-shrink: 0;
  background: #fff;
}

.me-row b {
  color: #fff;
}

.rank-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rank-list li {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.rank-list li.mine {
  background: rgba(134, 59, 255, 0.26);
  border: 1px solid rgba(134, 59, 255, 0.34);
}

.rank-no {
  width: 28px;
  font-weight: 700;
  color: #e2ccff;
}

.rank-name {
  flex: 1;
  font-size: 15px;
  color: #ffffff;
}

.rank-score {
  font-weight: 600;
  color: #ffffff;
}

.rank-empty {
  text-align: center;
  color: #b9c4dc;
  font-size: 14px;
  padding: 16px 0;
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
  .game-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .game-container {
    padding: 24px 12px 48px;
  }

  .panel {
    padding: 12px;
  }

  .tips {
    font-size: 12px;
  }
}
</style>
