import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

import App from './App.vue'
import router from './router'

// PrimeVue 기본 스타일
import 'primeicons/primeicons.css'

// 전역 스타일
import './assets/global.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue)

app.mount('#app')