<template>
  <div class="login-wrapper">
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <div class="login-card">
      <div class="login-header">
        <div class="logo-container">
          <span class="logo-icon">🍽️</span>
        </div>
        <h1>¡Hola de nuevo!</h1>
        <p>Ingresa tus credenciales para acceder a lo mejor de la cocina</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>Email</label>
          <div class="input-container">
            <span class="icon">✉️</span>
            <input 
              type="email" 
              v-model="email" 
              required 
              placeholder="tu@email.com"
              :disabled="isLoading"
            >
          </div>
        </div>
        
        <div class="form-group">
          <label>Contraseña</label>
          <div class="input-container">
            <span class="icon">🔒</span>
            <input 
              type="password" 
              v-model="password" 
              required 
              placeholder="••••••••"
              :disabled="isLoading"
            >
          </div>
        </div>

        <button type="submit" class="btn-login" :disabled="isLoading">
          <div v-if="isLoading" class="spinner"></div>
          <span v-else>Iniciar Sesión 🚀</span>
        </button>

        <Transition name="slide-fade">
          <div v-if="errorMessage" class="error-msg">
            <span>⚠️</span> {{ errorMessage }}
          </div>
        </Transition>
      </form>
      
      <div class="login-footer">
        <p>¿No tienes cuenta? <router-link to="/register" class="link-highlight">Regístrate aquí</router-link></p>
        <router-link to="/forgot-password" class="forgot-link">¿Olvidaste tu contraseña?</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await authStore.login(email.value, password.value);
    const role = response.user.role; 

    // Redirección profesional
    if (role === 1) router.push('/admin/dashboard');
    else if (role === 2) router.push('/owner/dashboard');
    else if (role === 3) router.push('/client/dashboard');

  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Credenciales incorrectas. Revisa e intenta de nuevo.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* Reset y Contenedor Principal */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a; /* Fondo oscuro elegante */
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* Decoración de fondo */
.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
}
.circle-1 {
  width: 300px;
  height: 300px;
  background: rgba(79, 70, 229, 0.4);
  top: -100px;
  right: -50px;
}
.circle-2 {
  width: 400px;
  height: 400px;
  background: rgba(124, 58, 237, 0.3);
  bottom: -150px;
  left: -100px;
}

/* Tarjeta Glassmorphism */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  width: 100%;
  max-width: 400px;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  text-align: center;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.logo-container {
  width: 70px;
  height: 70px;
  background: #f1f5f9;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 2.5rem;
}

.login-header h1 {
  font-size: 1.75rem;
  color: #1e293b;
  font-weight: 800;
  margin-bottom: 8px;
}

.login-header p {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 30px;
}

/* Formulario */
.form-group {
  text-align: left;
  margin-bottom: 20px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
  margin-left: 5px;
}

.input-container {
  position: relative;
  margin-top: 8px;
}

.icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.1rem;
}

input {
  width: 100%;
  padding: 14px 14px 14px 45px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s;
  background: #f8fafc;
}

input:focus {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
  outline: none;
}

/* Botón con Spinner */
.btn-login {
  width: 100%;
  padding: 16px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
}

.btn-login:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.3);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Mensaje de Error */
.error-msg {
  background: #fef2f2;
  color: #b91c1c;
  padding: 12px;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-top: 20px;
  border-left: 4px solid #ef4444;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Footer */
.login-footer {
  margin-top: 30px;
  border-top: 1px solid #f1f5f9;
  padding-top: 20px;
}

.link-highlight {
  color: #4f46e5;
  font-weight: 700;
  text-decoration: none;
}

.forgot-link {
  display: block;
  margin-top: 12px;
  color: #64748b;
  font-size: 0.85rem;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #4f46e5;
}

/* Transiciones */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-enter-from { transform: translateY(-10px); opacity: 0; }
</style>