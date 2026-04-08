import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue')
    },
    {
      path: '/devices',
      name: 'devices',
      component: () => import('../views/DevicesView.vue')
    },
    {
      path: '/devices/add',
      name: 'add-device',
      component: () => import('../views/AddDeviceView.vue')
    },
    {
      path: '/devices/fetch',
      name: 'fetch-configs',
      component: () => import('../views/FetchConfigsView.vue')
    },
    {
      path: '/configs',
      name: 'configs',
      component: () => import('../views/ConfigsView.vue')
    },
    {
      path: '/devices/scan',
      name: 'scan-network',
      component: () => import('../views/ScansView.vue')
    },
    {
      path: '/logs',
      name: 'logs',
      component: () => import('../views/LogsView.vue')
    }
  ]
})

export default router