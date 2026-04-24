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
                this._setupAxiosInterceptor()
            }
        },

        _setupAxiosInterceptor() {
            // Attach Bearer token to every axios request automatically
            axios.interceptors.request.use(config => {
                const token = localStorage.getItem('access_token')
                if (token) config.headers['Authorization'] = `Bearer ${token}`
                return config
            })

            // On 401 response, try to refresh the token once, then retry
            axios.interceptors.response.use(
                response => response,
                async error => {
                    const original = error.config
                    const isRefreshCall = original.url?.includes('token/refresh')
                    if (error.response?.status === 401 && !original._retry && !isRefreshCall) {
                        original._retry = true
                        try {
                            const refresh = localStorage.getItem('refresh_token')
                            if (!refresh) throw new Error('No refresh token')
                            const res = await axios.post('/api/v1/token/refresh/', { refresh })
                            const newAccess = res.data.access
                            this.token = newAccess
                            localStorage.setItem('access_token', newAccess)
                            original.headers['Authorization'] = `Bearer ${newAccess}`
                            return axios(original) // retry original request
                        } catch {
                            // Refresh also failed — clear tokens and redirect to login
                            localStorage.removeItem('access_token')
                            localStorage.removeItem('refresh_token')
                            localStorage.removeItem('user_data')
                            this.token = null
                            this.user = null
                            window.location.href = '/'
                        }
                    }
                    return Promise.reject(error)
                }
            )
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
                this.user = { email: email, is_admin: response.data.is_admin };

                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('user_data', JSON.stringify(this.user));

                this._setupAxiosInterceptor()
                this.authModalOpen = false;

                if (this.user.is_admin) {
                    await router.push('/admin');
                } else {
                    await router.push('/planner');
                }
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
