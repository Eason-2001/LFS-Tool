<template>
  <div class="toast-wrap">
    <transition-group name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast-item" :class="t.type">
        <span class="toast-icon">{{ iconOf(t.type) }}</span>
        <span class="toast-msg">{{ t.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts } = useToast()

const iconMap = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'i',
}

const iconOf = (type) => iconMap[type] || iconMap.info
</script>

<style scoped>
.toast-wrap {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  pointer-events: none;
}
.toast-item {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 420px;
  padding: 12px 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 6px 20px rgba(20, 30, 60, 0.16);
  font-size: 14px;
  color: #2b2f3a;
  pointer-events: auto;
}
.toast-icon {
  flex: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}
.toast-item.success .toast-icon { background: #3cb371; }
.toast-item.error .toast-icon { background: #e06c6c; }
.toast-item.warning .toast-icon { background: #e8a33d; }
.toast-item.info .toast-icon { background: #5c70e0; }
.toast-msg { line-height: 1.4; }

/* 进出动画：从上方滑入、淡入 */
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
</style>
