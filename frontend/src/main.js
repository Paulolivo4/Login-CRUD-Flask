// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios' // <--- Importamos axios
import './assets/styles.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// --- CONFIGURACIÓN DE AXIOS (Hacer esto ANTES de montar la app) ---
axios.defaults.baseURL = import.meta.env.VITE_API_URL || '';
axios.defaults.withCredentials = true; // <--- Importante ponerlo aquí
// ------------------------------------------------------------------

app.use(createPinia())
app.use(router)

app.mount('#app') // <--- Esto siempre va al final