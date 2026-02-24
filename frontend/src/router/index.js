import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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
            // route level code-splitting
            component: () => import('../views/PlannerView.vue')
        }
    ]
})

export default router
