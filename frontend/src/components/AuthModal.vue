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
  padding: 2rem;
  position: relative;
  background: rgba(20, 30, 46, 0.9); /* Darker opacity for readability */
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.5rem;
  color: var(--color-text-muted);
}

.close-btn:hover {
  color: white;
}

h2 {
  text-align: center;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

input {
  width: 100%;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
  color: white;
  outline: none;
  transition: border-color 0.2s;
}

input:focus {
  border-color: var(--color-primary);
}

.full-width {
  width: 100%;
  padding: 1rem;
}

.switch-mode {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.switch-mode a {
  color: var(--color-primary-light);
  font-weight: 600;
}

.error {
  color: #ef4444;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.9rem;
}
</style>
