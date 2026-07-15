import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0, left: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/tourists',
      name: 'tourist-list',
      component: () => import('../views/TouristListView.vue'),
    },
    {
      path: '/tourists/:id',
      name: 'tourist-detail',
      component: () => import('../views/TouristDetailView.vue'),
      props: true,
    },
    {
      path: '/posts',
      name: 'post-list',
      component: () => import('../views/PostListView.vue'),
    },
    {
      path: '/posts/new',
      name: 'post-create',
      component: () => import('../views/PostFormView.vue'),
    },
    {
      path: '/posts/:id',
      name: 'post-detail',
      component: () => import('../views/PostDetailView.vue'),
      props: true,
    },
    {
      path: '/posts/:id/edit',
      name: 'post-edit',
      component: () => import('../views/PostFormView.vue'),
      props: true,
    },
    {
      path: '/rocket',
      name: 'rocket-dashboard',
      component: () => import('../views/RocketDashboardView.vue'),
    },
  ],
})

export default router
