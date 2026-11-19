import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// 新增：二级分类页
import ConvertCategoryView from '../views/ConvertCategoryView.vue'
// 现有转换页（以后按图片/文档拆，先复用这一个）
import ConvertView from '../views/ConvertView.vue'

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
    }
  ]
})

export default router
