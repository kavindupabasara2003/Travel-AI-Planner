import { defineStore } from 'pinia'
import axios from 'axios'
import router from '../router'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: null, // JWT Access Token
        refreshToken: null,
        loading: false,
        authModalOpen: false
    }),

    actions: {
        async initializeAuth() {
            const storedToken = localStorage.getItem('access_token')
            const storedRefresh = localStorage.getItem('refresh_token')
            const storedUser = localStorage.getItem('user_data')

            if (storedToken && storedUser) {
                this.token = storedToken
                this.refreshToken = storedRefresh
                this.user = JSON.parse(storedUser)
            }
        },

        async signInWithEmail(email, password) {
            this.loading = true;
            try {
                const response = await axios.post('/api/v1/token/', {
                    username: email,
                    password: password
                });

                this.token = response.data.access;
                this.refreshToken = response.data.refresh;
                this.user = { email: email };

                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('user_data', JSON.stringify(this.user));

                this.authModalOpen = false;
                await router.push('/planner');
            } catch (error) {
                alert("Login Failed: Please check your credentials.");
                console.error(error);
            } finally {
                this.loading = false;
            }
        },

        async signUpWithEmail(email, password) {
            this.loading = true;
            try {
                await axios.post('/api/v1/register/', {
                    email: email,
                    password: password
                });

                // Immediately sign in after successful registration
                await this.signInWithEmail(email, password);
            } catch (error) {
                alert("Sign Up Failed: " + (error.response?.data?.error || "Error"));
                console.error(error);
            } finally {
                this.loading = false;
            }
        },

        async signOut() {
            this.user = null;
            this.token = null;
            this.refreshToken = null;
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_data');
            router.push('/');
        },

        toggleAuthModal(isOpen) {
            this.authModalOpen = isOpen;
        }
    }
});
