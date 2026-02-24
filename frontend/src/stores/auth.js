import { defineStore } from 'pinia'
import { supabase } from '../supabase'
import router from '../router'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        session: null,
        loading: false,
        authModalOpen: false
    }),

    actions: {
        async initializeAuth() {
            // Mock Initialization - Check Local Storage or default to null
            const storedUser = localStorage.getItem('demo_user')
            if (storedUser) {
                this.user = JSON.parse(storedUser)
                // Ensure session exists so route guards pass
                this.session = { access_token: 'mock_token', user: this.user }
            }
        },

        async signInWithEmail(email, password) {
            this.loading = true

            // SUPERVISOR DEMO BYPASS
            if (email === 'kavindu.pabasaraz12@gmail.com' && password === 'kav1') {
                // Success
                this.user = {
                    id: 'supervisor_123',
                    email: email,
                    role: 'authenticated'
                }
                this.session = { access_token: 'mock_token_123', user: this.user }

                // Persist locally so refresh works
                localStorage.setItem('demo_user', JSON.stringify(this.user))

                this.loading = false
                this.authModalOpen = false
                // Force redirect
                await router.push('/planner')
                return
            }

            // Fail for others
            this.loading = false
            alert("Supervisor Demo Access Only")
        },

        async signUpWithEmail(email, password) {
            alert("Sign Up disabled for Supervisor Demo. Please Log In.")
        },

        async signOut() {
            this.user = null
            this.session = null
            localStorage.removeItem('demo_user')
            router.push('/')
        },

        toggleAuthModal(isOpen) {
            this.authModalOpen = isOpen
        }
    }
})
