<template>
  <transition name="modal">
    <div v-if="confirmState.visible" class="modal-mask" @click.self="close(false)">
      <div class="modal-card">
        <h3 class="modal-title">{{ confirmState.title }}</h3>
        <p class="modal-message">{{ confirmState.message }}</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="close(false)">取消</button>
          <button class="btn-ok" @click="close(true)">确认</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { useConfirm } from '../composables/useConfirm'

const { confirmState, close } = useConfirm()
</script>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(20, 26, 48, 0.42);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}
.modal-card {
  width: 340px;
  max-width: calc(100vw - 40px);
  padding: 26px 24px 22px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 12px 36px rgba(20, 30, 60, 0.22);
}
.modal-title {
  font-size: 18px;
  color: #1a1a1a;
  margin-bottom: 10px;
}
.modal-message {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  margin-bottom: 22px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
}
.btn-cancel:hover {
  background: #f3f5f9;
}
.btn-ok {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  background: linear-gradient(180deg, rgba(96, 140, 245, 0.95), rgba(92, 112, 224, 0.95));
}
.btn-ok:hover {
  box-shadow: 0 6px 16px rgba(80, 120, 237, 0.3);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-card {
  transform: translateY(14px) scale(0.97);
}
.modal-enter-active,
.modal-leave-active {
  transition: all 0.22s ease;
}
.modal-enter-active .modal-card,
.modal-leave-active .modal-card {
  transition: all 0.22s ease;
}
</style>
