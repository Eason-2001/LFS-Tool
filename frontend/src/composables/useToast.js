// 全局轻提示（Toast）：模块级单例状态，任意组件调用 toast(消息, 类型) 即可弹出
import { reactive } from 'vue'

let seq = 0

const state = reactive({
  list: [] // { id, message, type }
})

/**
 * 弹出一条轻提示，到时自动消失
 * @param {string} message 提示文字
 * @param {'success'|'error'|'warning'|'info'} type 类型，决定配色和图标
 * @param {number} duration 停留毫秒数
 */
function toast(message, type = 'info', duration = 2600) {
  if (!message) return
  const id = ++seq
  state.list.push({ id, message, type })
  setTimeout(() => {
    const i = state.list.findIndex((t) => t.id === id)
    if (i > -1) state.list.splice(i, 1)
  }, duration)
}

export function useToast() {
  return { toast, toasts: state.list }
}
