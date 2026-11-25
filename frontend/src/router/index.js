import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// 二级分类页
import ConvertCategoryView from '../views/ConvertCategoryView.vue'
// 现有转换页（图片/文档复用）
import ConvertView from '../views/ConvertView.vue'
// 登录 / 注册 / 备忘录
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import MemoView from '../views/MemoView.vue'
import MemoDetailView from '../views/MemoDetailView.vue'
import ProfileView from '../views/ProfileView.vue'
import LifeView from '../views/LifeView.vue'
import BreakoutView from '../views/BreakoutView.vue'
import MinesweeperView from '../views/MinesweeperView.vue'
import TetrisView from '../views/TetrisView.vue'
import GameHubView from '../views/GameHubView.vue'
import DivinationHubView from '../views/DivinationHubView.vue'
import BaziView from '../views/BaziView.vue'
import HoroscopeView from '../views/HoroscopeView.vue'
import TarotView from '../views/TarotView.vue'
import { useAuth } from '../composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    // 生活信息：天气 + 每日一句（公开）
    {
      path: '/life',
      name: 'life',
      component: LifeView
    },
    // 摸鱼小游戏：游戏选择大厅（需登录）
    {
      path: '/game',
      name: 'game-hub',
      component: GameHubView,
      meta: { requiresAuth: true }
    },
    // 摸鱼小游戏：打砖块（需登录）
    {
      path: '/game/breakout',
      name: 'breakout',
      component: BreakoutView,
      meta: { requiresAuth: true }
    },
    // 摸鱼小游戏：经典扫雷（需登录）
    {
      path: '/game/minesweeper',
      name: 'minesweeper',
      component: MinesweeperView,
      meta: { requiresAuth: true }
    },
    // 摸鱼小游戏：俄罗斯方块（需登录）
    {
      path: '/game/tetris',
      name: 'tetris',
      component: TetrisView,
      meta: { requiresAuth: true }
    },
    // 命理测算：选择大厅（需登录）
    {
      path: '/divination',
      name: 'divination-hub',
      component: DivinationHubView,
      meta: { requiresAuth: true }
    },
    // 中式命理（需登录）
    {
      path: '/divination/bazi',
      name: 'divination-bazi',
      component: BaziView,
      meta: { requiresAuth: true }
    },
    // 西式星座（需登录）
    {
      path: '/divination/horoscope',
      name: 'divination-horoscope',
      component: HoroscopeView,
      meta: { requiresAuth: true }
    },
    // 命运塔罗（需登录）
    {
      path: '/divination/tarot',
      name: 'divination-tarot',
      component: TarotView,
      meta: { requiresAuth: true }
    },
    // 二级：格式转换分类选择页
    {
      path: '/convert',
      name: 'convert-category',
      component: ConvertCategoryView
    },
    // 三级：图片转换页
    {
      path: '/convert/image',
      name: 'convert-image',
      component: ConvertView
    },
    // 三级：文本/文档转换页
    {
      path: '/convert/document',
      name: 'convert-document',
      component: ConvertView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    // 备忘录：需要登录才能访问
    {
      path: '/memo',
      name: 'memo',
      component: MemoView,
      meta: { requiresAuth: true }
    },
    // 备忘录详情：单条查看 / 编辑 / 删除
    {
      path: '/memo/:id',
      name: 'memo-detail',
      component: MemoDetailView,
      meta: { requiresAuth: true }
    },
    // 个人中心：需要登录才能访问
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫：访问需要登录的页面时，未登录跳登录页，并记下原本要去的地址
router.beforeEach((to) => {
  const { isLogin } = useAuth()
  if (to.meta.requiresAuth && !isLogin.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
