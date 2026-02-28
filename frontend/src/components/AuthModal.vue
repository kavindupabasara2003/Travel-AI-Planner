<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isLogin = ref(true)
const email = ref('')
const password = ref('')
const errorMsg = ref('')

const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMsg.value = ''
}

const handleSubmit = async () => {
  errorMsg.value = ''
  if (!email.value || !password.value) {
    errorMsg.value = 'Please fill in all fields.'
    return
  }
  
  try {
    if (isLogin.value) {
      await authStore.signInWithEmail(email.value, password.value)
      // On success, store watcher redirects, close modal
      authStore.toggleAuthModal(false)
    } else {
      await authStore.signUpWithEmail(email.value, password.value)
      alert("Check your email for confirmation!")
      authStore.toggleAuthModal(false)
    }
  } catch (e) {
    errorMsg.value = e.message
  }
}

const adminLogin = async () => {
  email.value = 'admin@gmail.com'
  password.value = 'kav1'
  isLogin.value = true
  await handleSubmit()
}
</script>

<template>
  <div v-if="authStore.authModalOpen" class="modal-overlay" @click.self="authStore.toggleAuthModal(false)">
    <div class="modal-content glass-panel">
      <button class="close-btn" @click="authStore.toggleAuthModal(false)">&times;</button>
      
      <h2>{{ isLogin ? 'Welcome Back' : 'Start Your Journey' }}</h2>
      <p class="subtitle">{{ isLogin ? 'Login to continue planning' : 'Create an account to get started' }}</p>
      
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" placeholder="you@example.com" required />
        </div>
        
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" placeholder="••••••••" required />
        </div>
        
        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
        
        <button type="submit" class="btn btn-primary full-width" :disabled="authStore.loading">
          {{ authStore.loading ? 'Processing...' : (isLogin ? 'Login' : 'Sign Up') }}
        </button>
      </form>
      
      <p class="switch-mode">
        {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
        <a href="#" @click.prevent="toggleMode">{{ isLogin ? 'Sign Up' : 'Login' }}</a>
      </p>
      
      <div class="admin-divider">
        <span>OR</span>
      </div>
      
      <button class="btn btn-secondary full-width admin-btn" @click="adminLogin" :disabled="authStore.loading">
        🔑 Login as Administrator
      </button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  position: relative;
  background: var(--color-bg-card);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  color: var(--color-text-main);
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  font-size: 1.8rem;
  color: var(--color-text-muted);
  background: none;
  border: none;
  cursor: pointer;
}

.close-btn:hover {
  color: var(--color-text-main);
}

h2 {
  text-align: center;
  margin-bottom: 0.5rem;
  font-weight: 700;
  color: var(--color-text-main);
}

.subtitle {
  text-align: center;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-main);
}

input {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-light);
  color: var(--color-text-main);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.full-width {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
}

.switch-mode {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.switch-mode a {
  color: var(--color-primary);
  font-weight: 600;
  margin-left: 0.3rem;
  text-decoration: none;
}

.switch-mode a:hover {
  text-decoration: underline;
}

.error {
  color: #ef4444;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.9rem;
  background: #fef2f2;
  padding: 0.5rem;
  border-radius: 6px;
}

.admin-divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0;
  color: var(--color-text-muted);
}

.admin-divider::before,
.admin-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--color-border);
}

.admin-divider span {
  padding: 0 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.admin-btn {
  background-color: var(--color-bg-light);
  border: 1px dashed var(--color-border);
  color: var(--color-text-muted);
  transition: all 0.2s;
}

.admin-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}
</style>
