<template>
  <div class="login-container">
    <h2>Iniciar Sesión</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>Email:</label>
        <input type="email" v-model="email" required placeholder="tu@email.com">
      </div>
      
      <div class="form-group">
        <label>Contraseña:</label>
        <input type="password" v-model="password" required>
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Cargando...' : 'Ingresar' }}
      </button>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const email = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    // Gracias al proxy en vite.config.js, solo llamamos a /api/login
    const response = await axios.post('/api/login', {
      email: email.value,
      password: password.value
    });

    console.log('Login exitoso:', response.data);
    alert('Bienvenido! Rol: ' + response.data.role);
    // AQUÍ REDIRIGIREMOS AL DASHBOARD LUEGO
    
  } catch (error) {
    if (error.response) {
      errorMessage.value = error.response.data.error || 'Error al iniciar sesión';
    } else {
      errorMessage.value = 'Error de conexión con el servidor';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.error {
  color: red;
  margin-top: 1rem;
}
.form-group {
  margin-bottom: 1rem;
}
input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
}
</style>

