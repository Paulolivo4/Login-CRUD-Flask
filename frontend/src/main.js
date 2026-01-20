// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia' // Importar Pinia
import './assets/styles.css' // <--- TU CSS ORIGINAL AQUI
import App from './App.vue'
import router from './router' // Lo crearemos en el paso 5

const app = createApp(App)

app.use(createPinia()) // Usar Pinia
app.use(router) // Usar Router (lo configuramos abajo)
app.mount('#app')