// 全局确认弹窗：confirmDialog({ title, message }) 返回 Promise<boolean>，点确认 resolve(true)，取消/遮罩 resolve(false)
import { reactive } from 'vue'

const state = reactive({
  visible: false,
  title: '提示',
  message: '',
  resolve: null,
})

/**
 * 弹出确认框
 * @param {{title?: string, message?: string}} options
 * @returns {Promise<boolean>} 用户是否点了确认
 */
function confirmDialog(options = {}) {
  state.title = options.title || '提示'
  state.message = options.message || ''
  state.visible = true
  return new Promise((resolve) => {
    state.resolve = resolve
  })
}

/** 内部调用：关闭弹窗并把结果回传给 Promise */
function close(result) {
  state.visible = false
  if (typeof state.resolve === 'function') state.resolve(result)
  state.resolve = null
}

export function useConfirm() {
  return { confirmDialog, confirmState: state, close }
}
