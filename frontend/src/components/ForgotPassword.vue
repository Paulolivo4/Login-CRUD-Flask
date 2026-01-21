<template>
  <div class="auth-wrapper">
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <div class="auth-card">
      <div class="back-link">
        <router-link to="/login">← Volver al login</router-link>
      </div>

      <div class="auth-header">
        <div class="logo-container">🔑</div>
        <h2>¿Olvidaste tu clave?</h2>
        <p>No te preocupes, dinos tu correo y te enviaremos un código de seguridad.</p>
      </div>

      <form @submit.prevent="handleForgot" class="auth-form">
        <div class="form-group">
          <label>Correo electrónico registrado</label>
          <div class="input-container">
            <span class="icon">✉️</span>
            <input 
              v-model="email" 
              type="email" 
              placeholder="tu@email.com" 
              required 
              :disabled="loading"
            />
          </div>
        </div>

        <button type="submit" class="btn-auth" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Enviar Código de Acceso ✉️</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const loading = ref(false);

const handleForgot = async () => {
  loading.value = true;
  try {
    // Llamada al endpoint: api_forgot_password
    await axios.post('/forgot-password', { email: email.value });
    
    alert('Código enviado. Por favor, revisa tu bandeja de entrada.');
    
    // Redirigimos a la pantalla de reset pasando el email como parámetro de consulta
    router.push({ 
      path: '/reset-password', 
      query: { email: email.value } 
    });
  } catch (error) {
    alert(error.response?.data?.error || 'No se pudo enviar el correo.');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Reutilizamos el estilo Premium del Login */
.auth-wrapper {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: #0f172a; position: relative; overflow: hidden; padding: 20px;
}
.bg-circle { position: absolute; border-radius: 50%; filter: blur(80px); z-index: 0; }
.circle-1 { width: 300px; height: 300px; background: rgba(79, 70, 229, 0.4); top: -100px; right: -50px; }
.circle-2 { width: 400px; height: 400px; background: rgba(124, 58, 237, 0.3); bottom: -150px; left: -100px; }

.auth-card {
  background: rgba(255, 255, 255, 0.95); width: 100%; max-width: 400px; padding: 40px;
  border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); text-align: center;
  z-index: 1; backdrop-filter: blur(10px);
}
.back-link { text-align: left; margin-bottom: 20px; }
.back-link a { text-decoration: none; color: #4f46e5; font-weight: 600; font-size: 0.9rem; }
.logo-container { font-size: 2.5rem; margin-bottom: 15px; }
h2 { color: #1e293b; font-weight: 800; margin-bottom: 10px; }
p { color: #64748b; font-size: 0.9rem; margin-bottom: 25px; }

.form-group { text-align: left; margin-bottom: 20px; }
.input-container { position: relative; margin-top: 8px; }
.icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); }
input { 
  width: 100%; padding: 14px 14px 14px 45px; border: 2px solid #e2e8f0; 
  border-radius: 12px; transition: 0.3s; background: #f8fafc;
}
input:focus { border-color: #6366f1; background: #fff; outline: none; }

.btn-auth {
  width: 100%; padding: 16px; background: #4f46e5; color: white; border: none;
  border-radius: 12px; font-weight: 700; cursor: pointer; transition: 0.3s;
}
.btn-auth:hover { background: #4338ca; transform: translateY(-2px); }

.spinner {
  width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%; border-top-color: #fff; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>