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
import { useAuth } from '../composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
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
