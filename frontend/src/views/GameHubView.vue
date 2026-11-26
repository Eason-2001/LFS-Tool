<template>
  <div class="hub-container">
    <h1 class="page-title">摸鱼小游戏</h1>

    <div class="game-grid">
      <router-link
        v-for="g in games"
        :key="g.path"
        :to="g.path"
        class="game-card"
      >
        <div class="card-icon">{{ g.icon }}</div>
        <h3>{{ g.name }}</h3>
        <p>{{ g.desc }}</p>
      </router-link>
    </div>

    <router-link to="/" class="back-btn">🏠 返回主页</router-link>
  </div>
</template>

<script setup>
const games = [
  {
    path: '/game/breakout',
    icon: '🧱',
    name: '霓虹打砖块',
    desc: '清屏得分 · 道具护体 · 连击加分'
  },
  {
    path: '/game/minesweeper',
    icon: '💣',
    name: '经典扫雷',
    desc: '排雷插旗 · 三档难度 · 计时挑战'
  },
  {
    path: '/game/tetris',
    icon: '🧩',
    name: '俄罗斯方块',
    desc: '堆叠消行 · 等级加速 · 冲击高分'
  },
  {
    path: '/game/spider',
    icon: '🕷️',
    name: '蜘蛛纸牌',
    desc: '接龙成组 · 八组通关 · 计时挑战'
  }
]
</script>

<style scoped>
.hub-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 72px 24px 80px;
}

.page-title {
  font-size: 40px;
  letter-spacing: 2px;
  text-align: center;
  color: #fff;
  margin-bottom: 48px;
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1080px;
  margin: 0 auto;
}

.game-card {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 32px 28px;
  text-decoration: none;
  color: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.game-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.92);
}

.card-icon {
  font-size: 36px;
  line-height: 1;
  height: 36px;
  margin-bottom: 18px;
}

.game-card h3 {
  font-size: 20px;
  line-height: 1.3;
  margin-bottom: 10px;
}

.game-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.back-btn {
  display: block;
  width: fit-content;
  margin: 32px auto 0;
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
