<template>
  <div class="game-container">
    <div class="game-layout">
      <section class="panel board-panel">
        <!-- 状态栏：剩余雷数 / 用时 / 最佳 -->
        <div class="hud">
          <div class="hud-item">🚩 {{ remaining }}</div>
          <div class="hud-item">⏱ {{ time }}s</div>
          <div class="hud-item">🏆 {{ bestText }}</div>
        </div>

        <!-- 控制栏：难度 / 插旗模式 / 重开 -->
        <div class="controls">
          <div class="levels">
            <button
              v-for="(lvl, key) in LEVELS"
              :key="key"
              class="level-btn"
              :class="{ active: level === key }"
              @click="changeLevel(key)"
            >
              {{ lvl.label }}
            </button>
          </div>
          <button class="mode-btn" :class="{ flag: mode === 'flag' }" @click="toggleMode">
            {{ mode === 'flag' ? '🚩 插旗' : '⛏ 挖掘' }}
          </button>
          <button class="restart-btn" @click="newGame">🔄 重开</button>
        </div>

        <!-- 棋盘 -->
        <div class="board" :style="boardStyle">
          <template v-for="(row, r) in board" :key="r">
            <button
              v-for="(cell, c) in row"
              :key="r + '-' + c"
              class="cell"
              :class="{
                open: cell.revealed,
                exploded: cell.exploded,
                flagged: cell.flagged
              }"
              @click="onCellClick(r, c)"
              @contextmenu.prevent="onRightClick(r, c)"
              @touchstart="onTouchStart($event, r, c)"
              @touchend="onTouchEnd"
            >
              <span v-if="cell.revealed && cell.mine">💣</span>
              <span v-else-if="cell.flagged">🚩</span>
              <span v-else-if="cell.revealed && cell.adjacent" :class="'n' + cell.adjacent">{{ cell.adjacent }}</span>
            </button>
          </template>
        </div>

        <!-- 胜负提示 -->
        <div v-if="status === 'win' || status === 'over'" class="result" :class="status">
          <span>{{ status === 'win' ? '🎉 恭喜扫雷成功！' : '💥 踩到雷了' }}</span>
          <em>用时 {{ time }} 秒</em>
        </div>

        <p class="tips">点按翻开 · 右键 / 长按插旗 · 也可切到插旗模式点按标旗</p>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { request } from '../api/request'
import { useAuth } from '../composables/useAuth'

const { state: authState } = useAuth()

const DEFAULT_AVATAR = '/default-avatar.svg'

function onAvatarError(e) {
  e.target.src = DEFAULT_AVATAR
}

// 三档难度：行列数、雷数、单格尺寸(px)
const LEVELS = {
  easy: { rows: 9, cols: 9, mines: 10, label: '初级', cell: 40 },
  medium: { rows: 16, cols: 16, mines: 40, label: '中级', cell: 34 },
  hard: { rows: 16, cols: 24, mines: 99, label: '高级', cell: 29 }
}

const level = ref('easy')
const board = ref([])
// ready 待首点 / play 进行中 / win 胜利 / over 踩雷失败
const status = ref('ready')
const time = ref(0)
const mode = ref('reveal') // reveal 挖掘 | flag 插旗
const flagCount = ref(0)

const leaderboard = ref([])
const me = ref(null)

let timerId = null
let pressTimer = null
let longPressed = false

const cfg = computed(() => LEVELS[level.value])
const remaining = computed(() => cfg.value.mines - flagCount.value)
const boardStyle = computed(() => ({
  gridTemplateColumns: `repeat(${cfg.value.cols}, var(--cell))`,
  '--cell': cfg.value.cell + 'px'
}))
// 后端游戏标识：按难度分榜
const gameKey = computed(() => 'minesweeper-' + level.value)
const bestText = computed(() => (me.value && me.value.best ? me.value.best + 's' : '--'))

// ---------- 排行榜接口 ----------
async function fetchLeaderboard() {
  const { data } = await request('/api/game/leaderboard/?game=' + gameKey.value)
  if (data?.code === 200) {
    leaderboard.value = data.data.top || []
    me.value = data.data.me
  }
}

async function submitScore() {
  const { data } = await request('/api/game/score/', {
    method: 'POST',
    body: JSON.stringify({ game: gameKey.value, score: time.value })
  })
  if (data?.code === 200) {
    me.value = { rank: data.data.rank, best: data.data.best, plays: data.data.plays }
  }
  fetchLeaderboard()
}

function neighbors(r, c) {
  const { rows, cols } = cfg.value
  const list = []
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue
      const nr = r + dr
      const nc = c + dc
      if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) list.push([nr, nc])
    }
  }
  return list
}

function newGame() {
  stopTimer()
  time.value = 0
  flagCount.value = 0
  status.value = 'ready'
  mode.value = 'reveal'
  const { rows, cols } = cfg.value
  board.value = Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => ({
      mine: false,
      revealed: false,
      flagged: false,
      adjacent: 0,
      exploded: false
    }))
  )
}

// 首点后再布雷，并排除首点及其周围，保证第一下不踩雷
function placeMines(safeR, safeC) {
  const { rows, cols, mines } = cfg.value
  const forbidden = new Set()
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      const r = safeR + dr
      const c = safeC + dc
      if (r >= 0 && r < rows && c >= 0 && c < cols) forbidden.add(r + ',' + c)
    }
  }
  let placed = 0
  let guard = 0
  while (placed < mines && guard < 100000) {
    guard++
    const r = Math.floor(Math.random() * rows)
    const c = Math.floor(Math.random() * cols)
    if (board.value[r][c].mine || forbidden.has(r + ',' + c)) continue
    board.value[r][c].mine = true
    placed++
  }
  // 统计每格周围雷数
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (board.value[r][c].mine) continue
      board.value[r][c].adjacent = neighbors(r, c).filter(([nr, nc]) => board.value[nr][nc].mine).length
    }
  }
}

function revealCell(r, c) {
  if (status.value === 'win' || status.value === 'over') return
  const cell = board.value[r][c]
  if (cell.revealed || cell.flagged) return

  // 首点：布雷并开始计时
  if (status.value === 'ready') {
    placeMines(r, c)
    status.value = 'play'
    startTimer()
  }

  if (cell.mine) {
    cell.exploded = true
    status.value = 'over'
    stopTimer()
    revealAllMines()
    return
  }

  floodReveal(r, c)
  checkWin()
}

// 洪水填充：翻开空白区域及其相邻数字
function floodReveal(r, c) {
  const stack = [[r, c]]
  while (stack.length) {
    const [cr, cc] = stack.pop()
    const cell = board.value[cr][cc]
    if (cell.revealed || cell.flagged || cell.mine) continue
    cell.revealed = true
    if (cell.adjacent === 0) {
      neighbors(cr, cc).forEach(([nr, nc]) => {
        const n = board.value[nr][nc]
        if (!n.revealed && !n.flagged && !n.mine) stack.push([nr, nc])
      })
    }
  }
}

function revealAllMines() {
  board.value.forEach(row => row.forEach(cell => {
    if (cell.mine) cell.revealed = true
  }))
}

function toggleFlag(r, c) {
  if (status.value === 'win' || status.value === 'over') return
  const cell = board.value[r][c]
  if (cell.revealed) return
  cell.flagged = !cell.flagged
  flagCount.value += cell.flagged ? 1 : -1
}

function checkWin() {
  const { rows, cols, mines } = cfg.value
  let safeRevealed = 0
  board.value.forEach(row => row.forEach(cell => {
    if (!cell.mine && cell.revealed) safeRevealed++
  }))
  if (safeRevealed === rows * cols - mines) {
    status.value = 'win'
    stopTimer()
    // 剩余未标的雷自动插旗
    board.value.forEach(row => row.forEach(cell => {
      if (cell.mine && !cell.flagged) {
        cell.flagged = true
        flagCount.value++
      }
    }))
    submitScore()
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

function changeLevel(key) {
  level.value = key
  newGame()
  fetchLeaderboard()
}

function toggleMode() {
  mode.value = mode.value === 'reveal' ? 'flag' : 'reveal'
}

function onCellClick(r, c) {
  // 长按触发过插旗，忽略随后的 click
  if (longPressed) {
    longPressed = false
    return
  }
  if (mode.value === 'flag') toggleFlag(r, c)
  else revealCell(r, c)
}

function onRightClick(r, c) {
  toggleFlag(r, c)
}

function onTouchStart(e, r, c) {
  longPressed = false
  clearTimeout(pressTimer)
  pressTimer = setTimeout(() => {
    longPressed = true
    toggleFlag(r, c)
    if (navigator.vibrate) navigator.vibrate(30)
  }, 450)
}

function onTouchEnd() {
  clearTimeout(pressTimer)
}

newGame()
onMounted(fetchLeaderboard)
onBeforeUnmount(stopTimer)
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
  padding: 24px;
  color: #fff;
}

.board-panel {
  min-width: 0;
  overflow-x: auto;
}

.hud {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 18px;
  font-size: 18px;
  font-weight: 600;
}

.hud-item {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 8px 18px;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.levels {
  display: flex;
  gap: 8px;
}

.level-btn,
.mode-btn,
.restart-btn {
  border: 1px solid rgba(134, 59, 255, 0.35);
  background: rgba(134, 59, 255, 0.1);
  color: #d9c9ff;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}

.level-btn.active {
  background: #863bff;
  color: #fff;
}

.mode-btn.flag {
  background: rgba(224, 82, 82, 0.18);
  border-color: rgba(224, 82, 82, 0.4);
  color: #ffb3b3;
}

.board {
  display: grid;
  gap: 4px;
  margin: 0 auto;
  width: max-content;
  max-width: 100%;
}

.cell {
  width: var(--cell);
  height: var(--cell);
  aspect-ratio: 1;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.16);
  color: #fff;
  font-weight: 700;
  font-size: clamp(11px, 2.4vw, 16px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  padding: 0;
}

.cell:not(.open):hover {
  background: rgba(255, 255, 255, 0.26);
}

.cell.open {
  background: rgba(0, 0, 0, 0.35);
  cursor: default;
}

.cell.exploded {
  background: #e05252;
}

.cell.flagged {
  background: rgba(255, 255, 255, 0.16);
}

.n1 { color: #7ab8ff; }
.n2 { color: #7ee08a; }
.n3 { color: #ff8a8a; }
.n4 { color: #c79bff; }
.n5 { color: #ffc46b; }
.n6 { color: #6fd6d6; }
.n7 { color: #eeeeee; }
.n8 { color: #aaaaaa; }

.result {
  margin-top: 18px;
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result.win { color: #7ee08a; }
.result.over { color: #ff8a8a; }
.result em { font-style: normal; font-size: 14px; color: #c9d2e8; }

.tips {
  margin-top: 16px;
  text-align: center;
  color: #9aa4c4;
  font-size: 13px;
}

/* ---------- 排行榜 ---------- */
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

/* ---------- 返回按钮：全站统一浅色款 ---------- */
.back-btn {
  display: block;
  width: fit-content;
  margin: 28px auto 0;
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

  .hud {
    gap: 14px;
    font-size: 15px;
  }

  .tips {
    font-size: 12px;
  }
}
</style>
