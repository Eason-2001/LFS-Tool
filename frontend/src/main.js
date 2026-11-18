import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
// 导入我们写的路由
import router from './router'

createApp(App)
  .use(router)  // 告诉Vue用这个路由
  .mount('#app')
