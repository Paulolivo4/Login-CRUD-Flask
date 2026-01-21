import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// IMPORTANTE: baseURL ya incluye /api desde la variable de entorno
axios.defaults.baseURL = import.meta.env.VITE_API_URL;
axios.defaults.withCredentials = true; 

app.use(createPinia())
app.use(router)
app.mount('#app')