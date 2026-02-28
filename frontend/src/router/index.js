import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/planner',
            name: 'planner',
            component: () => import('../views/PlannerView.vue')
        },
        {
            path: '/profile',
            name: 'profile',
            component: () => import('../views/ProfileView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/admin',
            component: () => import('../views/admin/AdminLayout.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
            children: [
                {
                    path: '',
                    name: 'admin_dashboard',
                    component: () => import('../views/admin/AdminDashboard.vue')
                },
                {
                    path: 'users',
                    name: 'admin_users',
                    component: () => import('../views/admin/AdminUsers.vue')
                },
                {
                    path: 'trips',
                    name: 'admin_trips',
                    component: () => import('../views/admin/AdminTrips.vue')
                },
                {
                    path: 'cache',
                    name: 'admin_cache',
                    component: () => import('../views/admin/AdminCache.vue')
                }
            ]
        }
    ]
})

// Route Guards
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // Ensure auth is loaded from localStorage on direct hits
    if (!authStore.token && localStorage.getItem('access_token')) {
        await authStore.initializeAuth()
    }

    if (to.meta.requiresAuth && !authStore.token) {
        next('/')
    } else if (to.meta.requiresAdmin && !authStore.user?.is_admin) {
        // Bounce non-admins back to the home page to preserve security
        console.warn("Unauthorized access attempt to Admin Dashboard")
        next('/')
    } else {
        next()
    }
})

export default router
