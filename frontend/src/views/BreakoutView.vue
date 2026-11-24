<template>
  <div class="game-container">
    <div class="game-layout">
      <section class="panel game-panel">
        <canvas ref="canvasRef" class="game-canvas"></canvas>
        <button
          v-if="state.status === 'play' || state.status === 'pause'"
          class="touch-btn"
          @click="togglePause"
        >
          {{ state.status === 'pause' ? '▶ 继续' : '⏸ 暂停' }}
        </button>
        <p class="tips">{{ isTouch ? '左右拖动挡板 · 点按屏幕发球 · 下方按钮暂停' : '← → / A D 移动 · 空格发球 · P 暂停 · 回车 开始 / 再来一局' }}</p>
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

    <router-link to="/" class="back-btn">🏠 返回主页</router-link>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { request } from '../api/request'
import { useAuth } from '../composables/useAuth'

const { state: authState } = useAuth()

const DEFAULT_AVATAR = '/default-avatar.svg'

function onAvatarError(e) {
  e.target.src = DEFAULT_AVATAR
}

const canvasRef = ref(null)
const isTouch = ref(false)

// 逻辑坐标系
const W = 900
const H = 600

const state = reactive({
  score: 0,
  best: 0,
  lives: 1,
  level: 1,
  combo: 0,
  status: 'menu' // menu | play | pause | over
})

const leaderboard = ref([])
const me = ref(null)

// 游戏运行时变量
let ctx = null
let rafId = null
let dpr = 1
let last = performance.now()
let audio = null

let paddle = { x: W / 2, w: 120, h: 14, y: H - 42, expandT: 0 }
let balls = []
let bricks = []
let powerups = []
let particles = []
let stars = []
let keys = { left: false, right: false }
let touchId = null
let bannerMsg = ''
let bannerT = 0
let slowT = 0

const BRICK = { cols: 10, top: 70, side: 26, gap: 6, h: 22 }
const POWERS = [
  { id: 'expand', label: '广', hue: 145, w: 30 },
  { id: 'multi', label: '多', hue: 275, w: 25 },
  { id: 'slow', label: '慢', hue: 200, w: 25 },
  { id: 'life', label: '命', hue: 0, w: 10 },
  { id: 'points', label: '分', hue: 45, w: 10 }
]

// ---------- 接口 ----------
async function fetchLeaderboard() {
  const { data } = await request('/api/game/leaderboard/')
  if (data?.code === 200) {
    leaderboard.value = data.data.top || []
    me.value = data.data.me
    if (me.value) state.best = me.value.best
  }
}

async function submitScore() {
  if (state.score <= 0) return
  const { data } = await request('/api/game/score/', {
    method: 'POST',
    body: JSON.stringify({ score: state.score })
  })
  if (data?.code === 200) {
    me.value = { rank: data.data.rank, best: data.data.best, plays: data.data.plays }
    state.best = data.data.best
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

function beep(freq, dur = 0.08, type = 'square', vol = 0.14, slide = 0) {
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

function arp(fs, step = 0.09, type = 'square', vol = 0.12) {
  fs.forEach((f, i) => setTimeout(() => beep(f, step * 0.9, type, vol), i * step * 1000))
}

// ---------- 初始化 ----------
function brickW() {
  return (W - BRICK.side * 2 - BRICK.gap * (BRICK.cols - 1)) / BRICK.cols
}

function buildLevel(n) {
  bricks = []
  const rows = Math.min(4 + Math.floor((n - 1) / 2), 7)
  const bw = brickW()
  const p = (n - 1) % 4
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < BRICK.cols; c++) {
      let keep = true
      if (p === 1 && (r + c) % 2 === 1) keep = false
      if (p === 2) {
        if (r % 2 === 0 ? c % 3 === 2 : c % 4 === 0 || c % 4 === 3) keep = false
      }
      if (p === 3) {
        const e = Math.floor(r * 0.9)
        keep = (c >= e && c < BRICK.cols - e) || (r === rows - 1 && c >= 1 && c < BRICK.cols - 1)
      }
      if (!keep) continue
      let hp = 1
      if (n >= 4 && r === 0) hp = 2
      if (n % 3 === 0 && r < 3) hp = 2
      const hue = (185 + r * 16 + (p === 2 ? 40 : 0)) % 360
      bricks.push({
        c, r,
        x: BRICK.side + c * (bw + BRICK.gap),
        y: BRICK.top + r * (BRICK.h + BRICK.gap),
        w: bw, h: BRICK.h, hp, maxHp: hp, hue, alive: true
      })
    }
  }
}

function spawnBall() {
  balls = [{ x: paddle.x, y: paddle.y - 8, r: 7, vx: 0, vy: -1, stuck: true }]
}

function resetGame() {
  state.score = 0
  state.level = 1
  state.lives = 1
  state.combo = 0
  slowT = 0
  paddle = { x: W / 2, w: 120, h: 14, y: H - 42, expandT: 0 }
  powerups = []
  particles = []
  buildLevel(1)
  spawnBall()
  bannerMsg = isTouch.value ? '第 1 关 · 点按发球' : '第 1 关 · 空格发球'
  bannerT = 2
  state.status = 'play'
}

function launch() {
  const stuck = balls.filter(b => b.stuck)
  if (!stuck.length) return
  state.combo = 0
  const n = stuck.length
  stuck.forEach((b, i) => {
    const a = (i - (n - 1) / 2) * 0.38 + (Math.random() - 0.5) * 0.12
    b.vx = Math.sin(a)
    b.vy = -Math.cos(a)
    b.stuck = false
  })
  beep(330, 0.07, 'square', 0.1, 200)
}

function ballSpeed() {
  return (430 + (state.level - 1) * 25) * (slowT > 0 ? 0.6 : 1)
}

// ---------- 粒子 ----------
function spawnParticles(x, y, hue, n = 14) {
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2
    const sp = 40 + Math.random() * 220
    particles.push({
      x, y,
      vx: Math.cos(a) * sp,
      vy: Math.sin(a) * sp - 40,
      life: 0.5 + Math.random() * 0.4,
      max: 0.9,
      hue,
      size: 1.5 + Math.random() * 3
    })
  }
}

// ---------- 碰撞 / 得分 ----------
function hitBrick(bk) {
  state.combo++
  state.score += 10 + (state.combo - 1) * 2
  bk.hp--
  if (bk.hp <= 0) {
    bk.alive = false
    if (bk.maxHp > 1) state.score += 15
    spawnParticles(bk.x + bk.w / 2, bk.y + bk.h / 2, bk.hue)
    maybeDrop(bk)
  }
  beep(280 + Math.min(state.combo, 14) * 22, 0.055, 'square', 0.11)
  if (!bricks.some(b => b.alive)) levelCleared()
}

function maybeDrop(bk) {
  if (Math.random() >= 0.14) return
  const roll = Math.random() * 100
  let acc = 0
  let pick = POWERS[0]
  for (const p of POWERS) {
    acc += p.w
    if (roll < acc) { pick = p; break }
  }
  powerups.push({ x: bk.x + bk.w / 2, y: bk.y + bk.h / 2, r: 11, vy: 120, p: pick })
}

function applyPower(pt) {
  if (pt.p.id === 'expand') paddle.expandT = 12
  else if (pt.p.id === 'slow') slowT = 8
  else if (pt.p.id === 'life') state.lives = Math.min(state.lives + 1, 6)
  else if (pt.p.id === 'points') state.score += 500
  else if (pt.p.id === 'multi') {
    const alive = balls.filter(b => !b.stuck)
    const src = alive.length ? alive : balls
    for (const b of src) {
      if (balls.length >= 6) break
      const a = Math.atan2(b.vx, -b.vy)
      const sp = Math.hypot(b.vx, b.vy) || 1
      for (const da of [-0.5, 0.5]) {
        if (balls.length >= 6) break
        balls.push({ x: b.x, y: b.y, r: b.r, vx: Math.sin(a + da) * sp, vy: -Math.cos(a + da) * sp, stuck: b.stuck })
      }
    }
  }
  beep(520, 0.09, 'triangle', 0.14, 300)
  setTimeout(() => beep(780, 0.1, 'triangle', 0.12), 90)
  spawnParticles(paddle.x, paddle.y, pt.p.hue, 20)
}

function levelCleared() {
  state.score += 500 + state.level * 100
  state.level++
  buildLevel(state.level)
  balls = [{ x: paddle.x, y: paddle.y - 8, r: 7, vx: 0, vy: -1, stuck: true }]
  powerups = []
  state.combo = 0
  bannerMsg = `第 ${state.level - 1} 关 通关！进入第 ${state.level} 关`
  bannerT = 2.4
  arp([523, 659, 784, 1047], 0.09)
}

function loseLastBall() {
  beep(180, 0.35, 'sawtooth', 0.16, -140)
  if (state.lives <= 0) { gameOver(); return }
  state.lives--
  state.combo = 0
  spawnBall()
  bannerMsg = `剩余 ${state.lives} 条命`
  bannerT = 1.4
}

function gameOver() {
  state.status = 'over'
  submitScore()
}

// ---------- 更新 ----------
function update(dt) {
  bannerT = Math.max(0, bannerT - dt)
  slowT = Math.max(0, slowT - dt)

  // 挡板
  const tw = 120 + (paddle.expandT > 0 ? 70 : 0)
  paddle.w += (tw - paddle.w) * Math.min(1, dt * 8)
  if (keys.left) paddle.x -= 520 * dt
  if (keys.right) paddle.x += 520 * dt
  paddle.x = Math.max(paddle.w / 2 + 8, Math.min(W - paddle.w / 2 - 8, paddle.x))
  paddle.expandT = Math.max(0, paddle.expandT - dt)

  // 球
  const sp = ballSpeed()
  for (const b of balls) {
    if (b.stuck) { b.x = paddle.x; b.y = paddle.y - b.r - 1; continue }
    const m = Math.hypot(b.vx, b.vy) || 1
    let dx = b.vx / m
    let dy = b.vy / m
    const move = sp * dt
    const steps = Math.max(1, Math.ceil(move / b.r))
    const step = move / steps
    for (let s = 0; s < steps; s++) {
      b.x += dx * step
      b.y += dy * step
      if (b.x < b.r) { b.x = b.r; dx = Math.abs(dx) }
      else if (b.x > W - b.r) { b.x = W - b.r; dx = -Math.abs(dx); beep(190, 0.03, 'sine', 0.05) }
      if (b.y < b.r) { b.y = b.r; dy = Math.abs(dy) }
      if (dy > 0 && b.y + b.r >= paddle.y && b.y < paddle.y + paddle.h && Math.abs(b.x - paddle.x) <= paddle.w / 2 + b.r) {
        const rel = Math.max(-1, Math.min(1, (b.x - paddle.x) / (paddle.w / 2)))
        const ang = rel * (Math.PI / 3)
        dx = Math.sin(ang)
        dy = -Math.cos(ang)
        b.y = paddle.y - b.r
        state.combo = 0
        beep(220, 0.05, 'square', 0.09)
      }
      for (const bk of bricks) {
        if (!bk.alive) continue
        const nx = Math.max(bk.x, Math.min(b.x, bk.x + bk.w))
        const ny = Math.max(bk.y, Math.min(b.y, bk.y + bk.h))
        const ddx = b.x - nx
        const ddy = b.y - ny
        if (ddx * ddx + ddy * ddy <= b.r * b.r) {
          if (ddx === 0 && ddy === 0) dy = -dy
          else if (Math.abs(ddx) > Math.abs(ddy)) dx = ddx > 0 ? Math.abs(dx) : -Math.abs(dx)
          else dy = ddy > 0 ? Math.abs(dy) : -Math.abs(dy)
          b.x = nx + dx * (b.r + 0.5)
          b.y = ny + dy * (b.r + 0.5)
          hitBrick(bk)
          break
        }
      }
      if (b.y - b.r > H + 8) { b.dead = true; break }
    }
    b.vx = dx
    b.vy = dy
  }
  balls = balls.filter(b => !b.dead)
  if (balls.length === 0 && state.status === 'play') loseLastBall()

  // 道具
  for (const p of powerups) {
    p.y += p.vy * dt
    if (Math.abs(p.x - paddle.x) <= paddle.w / 2 + p.r && p.y + p.r >= paddle.y && p.y < paddle.y + paddle.h + p.r) {
      p.got = true
      applyPower(p)
    }
    if (p.y > H + 24) p.got = true
  }
  powerups = powerups.filter(p => !p.got)

  // 粒子
  for (const pt of particles) {
    pt.x += pt.vx * dt
    pt.y += pt.vy * dt
    pt.vy += 160 * dt
    pt.life -= dt
  }
  particles = particles.filter(p => p.life > 0)
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

function centerText(txt, y, size, fill, blur = 0) {
  ctx.save()
  ctx.font = `700 ${size}px "Segoe UI","Microsoft YaHei",sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  if (blur) { ctx.shadowColor = fill; ctx.shadowBlur = blur }
  ctx.fillStyle = fill
  ctx.fillText(txt, W / 2, y)
  ctx.restore()
}

function overlay(dim) {
  ctx.fillStyle = `rgba(4,7,15,${dim})`
  ctx.fillRect(0, 0, W, H)
}

function draw(t) {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.fillStyle = '#070b16'
  ctx.fillRect(0, 0, W, H)

  // 星空
  for (const s of stars) {
    ctx.globalAlpha = 0.25 + 0.45 * Math.abs(Math.sin(t * 0.001 * s.tw))
    ctx.fillStyle = '#9fb8ff'
    ctx.fillRect(s.x, s.y, s.r, s.r)
  }
  ctx.globalAlpha = 1

  // 砖块
  for (const bk of bricks) {
    if (!bk.alive) continue
    const light = 46 + 14 * (bk.hp / bk.maxHp)
    ctx.save()
    ctx.shadowColor = `hsl(${bk.hue} 90% 60%)`
    ctx.shadowBlur = 9
    ctx.fillStyle = `hsl(${bk.hue} 85% ${light}%)`
    roundRect(bk.x, bk.y, bk.w, bk.h, 4)
    ctx.fill()
    ctx.restore()
    if (bk.maxHp > 1) {
      ctx.fillStyle = 'rgba(255,255,255,.85)'
      ctx.font = '600 11px "Segoe UI",sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(bk.hp, bk.x + bk.w / 2, bk.y + bk.h / 2 + 1)
    }
  }

  // 道具
  for (const p of powerups) {
    ctx.save()
    ctx.shadowColor = `hsl(${p.p.hue} 95% 62%)`
    ctx.shadowBlur = 14
    ctx.fillStyle = `hsl(${p.p.hue} 90% 58%)`
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.r, 0, 7)
    ctx.fill()
    ctx.restore()
    ctx.fillStyle = '#08111f'
    ctx.font = '700 12px "Microsoft YaHei",sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(p.p.label, p.x, p.y + 1)
  }

  // 挡板
  ctx.save()
  const ph = paddle.expandT > 0 ? 145 : 190
  ctx.shadowColor = `hsl(${ph} 95% 60%)`
  ctx.shadowBlur = 16
  const grad = ctx.createLinearGradient(paddle.x - paddle.w / 2, 0, paddle.x + paddle.w / 2, 0)
  grad.addColorStop(0, `hsl(${ph} 95% 55%)`)
  grad.addColorStop(1, `hsl(${(ph + 60) % 360} 95% 62%)`)
  ctx.fillStyle = grad
  roundRect(paddle.x - paddle.w / 2, paddle.y, paddle.w, paddle.h, 7)
  ctx.fill()
  ctx.restore()

  // 球
  for (const b of balls) {
    ctx.save()
    ctx.shadowColor = '#00e5ff'
    ctx.shadowBlur = 14
    ctx.fillStyle = '#eaffff'
    ctx.beginPath()
    ctx.arc(b.x, b.y, b.r, 0, 7)
    ctx.fill()
    ctx.restore()
  }

  // 粒子（加色混合）
  ctx.save()
  ctx.globalCompositeOperation = 'lighter'
  for (const pt of particles) {
    ctx.globalAlpha = Math.max(0, pt.life / pt.max)
    ctx.fillStyle = `hsl(${pt.hue} 95% 65%)`
    ctx.fillRect(pt.x - pt.size / 2, pt.y - pt.size / 2, pt.size, pt.size)
  }
  ctx.restore()

  // HUD
  ctx.save()
  ctx.font = '600 15px "Segoe UI","Microsoft YaHei",sans-serif'
  ctx.fillStyle = '#8fb4e8'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'top'
  ctx.fillText('得分 ' + state.score, 18, 16)
  ctx.textAlign = 'center'
  ctx.fillText('最高 ' + state.best, W / 2, 16)
  ctx.textAlign = 'right'
  ctx.fillText('第 ' + state.level + ' 关', W - 70, 16)
  for (let i = 0; i < state.lives; i++) {
    ctx.fillStyle = '#ff5d8f'
    ctx.beginPath()
    ctx.arc(W - 52 + i * 16, 24, 5, 0, 7)
    ctx.fill()
  }
  if (state.combo >= 3 && state.status === 'play') {
    ctx.textAlign = 'center'
    ctx.fillStyle = '#ffd166'
    ctx.font = '700 18px "Segoe UI",sans-serif'
    ctx.fillText('连击 ×' + state.combo, W / 2, 40)
  }
  ctx.restore()

  // 横幅
  if (bannerT > 0 && state.status === 'play') {
    ctx.save()
    ctx.globalAlpha = Math.min(1, bannerT)
    centerText(bannerMsg, H / 2 - 40, 30, '#bfe9ff', 18)
    ctx.restore()
  }

  // 覆盖层
  if (state.status === 'menu') {
    overlay(0.72)
    centerText('霓 虹 打 砖 块', H / 2 - 70, 52, '#e6fbff', 26)
    centerText('清屏得分 · 道具护体 · 连击加分', H / 2 - 16, 17, '#9fd8ff', 8)
    centerText(isTouch.value ? '拖动挡板 · 点按发球' : '← → 移动 · 空格 发球 · P 暂停', H / 2 + 22, 14, '#5f7ba6')
    centerText(isTouch.value ? '点按屏幕开始' : '按 空格 开始', H / 2 + 78, 20, '#00e5ff', 12)
  } else if (state.status === 'pause') {
    overlay(0.6)
    centerText('已 暂 停', H / 2 - 20, 42, '#cfe3ff', 16)
    centerText(isTouch.value ? '点按屏幕继续' : '按 P 继续', H / 2 + 36, 16, '#5f7ba6')
  } else if (state.status === 'over') {
    overlay(0.78)
    centerText('游 戏 结 束', H / 2 - 64, 46, '#ff5d8f', 22)
    centerText('本局得分 ' + state.score, H / 2 - 6, 24, '#e6fbff', 10)
    if (state.score >= state.best && state.score > 0) centerText('★ 新纪录 ★', H / 2 + 34, 18, '#ffd166', 12)
    centerText(isTouch.value ? '点按再来一局' : '按 回车 再来一局', H / 2 + 82, 18, '#00e5ff', 10)
  }
}

function frame(now) {
  const dt = Math.min(0.033, (now - last) / 1000)
  last = now
  if (state.status === 'play') update(dt)
  draw(now)
  rafId = requestAnimationFrame(frame)
}

// ---------- 输入 ----------
function onKeyDown(e) {
  ensureAudio()
  if (e.code === 'ArrowLeft' || e.code === 'KeyA') keys.left = true
  if (e.code === 'ArrowRight' || e.code === 'KeyD') keys.right = true
  if (e.code === 'Space' || e.code === 'Enter') {
    if (state.status === 'menu' || state.status === 'over') resetGame()
    else if (state.status === 'play') launch()
    e.preventDefault()
  }
  if (e.code === 'KeyP' || e.code === 'Escape') {
    if (state.status === 'play') state.status = 'pause'
    else if (state.status === 'pause') state.status = 'play'
  }
}

function onKeyUp(e) {
  if (e.code === 'ArrowLeft' || e.code === 'KeyA') keys.left = false
  if (e.code === 'ArrowRight' || e.code === 'KeyD') keys.right = false
}

// ---------- 触屏输入 ----------
function clampPaddleX(x) {
  return Math.max(paddle.w / 2 + 8, Math.min(W - paddle.w / 2 - 8, x))
}

function clientToGameX(clientX) {
  const rect = canvasRef.value.getBoundingClientRect()
  return (clientX - rect.left) * (W / rect.width)
}

function togglePause() {
  ensureAudio()
  if (state.status === 'play') state.status = 'pause'
  else if (state.status === 'pause') state.status = 'play'
}

function onTouchStart(e) {
  e.preventDefault()
  ensureAudio()
  const t = e.changedTouches[0]
  touchId = t.identifier
  const gx = clientToGameX(t.clientX)

  if (state.status === 'menu' || state.status === 'over') {
    resetGame()
    return
  }
  if (state.status === 'pause') {
    state.status = 'play'
    return
  }
  // 进行中：挡板跟随触点，有黏滞球则发球
  paddle.x = clampPaddleX(gx)
  launch()
}

function onTouchMove(e) {
  e.preventDefault()
  const t = [...e.changedTouches].find(x => x.identifier === touchId)
  if (!t) return
  paddle.x = clampPaddleX(clientToGameX(t.clientX))
}

function onTouchEnd() {
  touchId = null
}

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  dpr = Math.min(2, window.devicePixelRatio || 1)
  canvasRef.value.width = W * dpr
  canvasRef.value.height = H * dpr
  isTouch.value =
    (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) ||
    'ontouchstart' in window
  for (let i = 0; i < 90; i++) {
    stars.push({ x: Math.random() * W, y: Math.random() * H, r: Math.random() * 1.6 + 0.3, tw: Math.random() * 6.28 + 0.6 })
  }
  fetchLeaderboard()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('keyup', onKeyUp)
  // 触屏事件：passive:false 才能 preventDefault 阻止页面滚动/缩放
  canvasRef.value.addEventListener('touchstart', onTouchStart, { passive: false })
  canvasRef.value.addEventListener('touchmove', onTouchMove, { passive: false })
  canvasRef.value.addEventListener('touchend', onTouchEnd, { passive: false })
  canvasRef.value.addEventListener('touchcancel', onTouchEnd, { passive: false })
  rafId = requestAnimationFrame(frame)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('keyup', onKeyUp)
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('touchstart', onTouchStart)
    canvasRef.value.removeEventListener('touchmove', onTouchMove)
    canvasRef.value.removeEventListener('touchend', onTouchEnd)
    canvasRef.value.removeEventListener('touchcancel', onTouchEnd)
  }
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
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 20px;
  color: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.game-panel {
  min-width: 0;
}

.game-canvas {
  display: block;
  width: 100%;
  margin: 0 auto;
  border-radius: 12px;
  background: #070b16;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  touch-action: none;
  user-select: none;
  -webkit-user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.touch-btn {
  display: block;
  margin: 14px auto 0;
  padding: 10px 26px;
  border: 1px solid rgba(134, 59, 255, 0.3);
  border-radius: 999px;
  background: rgba(134, 59, 255, 0.08);
  color: #7a34e8;
  font-size: 15px;
  cursor: pointer;
}

.touch-btn:active {
  background: rgba(134, 59, 255, 0.16);
}

.tips {
  text-align: center;
  margin-top: 14px;
  color: #666;
  font-size: 13px;
}

.rank-panel {
  color: #1a1a1a;
}

.rank-title {
  font-size: 18px;
  margin-bottom: 14px;
}

.me-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(134, 59, 255, 0.08);
  border: 1px solid rgba(134, 59, 255, 0.2);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 14px;
  font-size: 14px;
  color: #444;
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
  color: #863bff;
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
  background: rgba(0, 0, 0, 0.03);
}

.rank-list li.mine {
  background: rgba(134, 59, 255, 0.1);
  border: 1px solid rgba(134, 59, 255, 0.25);
}

.rank-no {
  width: 28px;
  font-weight: 700;
  color: #863bff;
}

.rank-name {
  flex: 1;
  font-size: 15px;
}

.rank-score {
  font-weight: 600;
  color: #333;
}

.rank-empty {
  text-align: center;
  color: #888;
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
