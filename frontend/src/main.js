import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Configurar baseURL de axios con la URL del backend + /api
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
axios.defaults.baseURL = `${apiUrl}/api`
axios.defaults.withCredentials = true

console.log('[Axios] Base URL:', axios.defaults.baseURL)

app.use(createPinia())
app.use(router)
app.mount('#app')