<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h2>Crea tu cuenta</h2>
      <p>Únete para reservar en los mejores restaurantes</p>

      <form @submit.prevent="handleRegister">
        <div class="form-grid">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="form.name" type="text" required placeholder="Ej. Juan" />
          </div>
          <div class="form-group">
            <label>Apellido</label>
            <input v-model="form.lastname" type="text" required placeholder="Ej. Perez" />
          </div>
        </div>

        <div class="form-group">
          <label>Correo Electrónico</label>
          <input v-model="form.email" type="email" required placeholder="tu@email.com" />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" required placeholder="••••••••" />
        </div>

        <button type="submit" class="btn-auth" :disabled="loading">
          {{ loading ? 'Creando cuenta...' : 'Registrarse' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const form = ref({ name: '', lastname: '', email: '', password: '' });

const handleRegister = async () => {
  loading.value = true;
  try {
    await axios.post('/api/register', form.value);
    alert('¡Cuenta creada! Ahora puedes iniciar sesión.');
    router.push('/login');
  } catch (error) {
    alert(error.response?.data?.error || 'Error al registrarse');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.auth-card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  width: 100%;
  max-width: 450px;
  text-align: center;
}
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.form-group { text-align: left; margin-bottom: 15px; }
.form-group label { font-size: 0.8rem; font-weight: bold; color: #4a5568; }
input { width: 100%; padding: 12px; border: 1px solid #edf2f7; border-radius: 10px; margin-top: 5px; }
.btn-auth {
  width: 100%; padding: 14px; background: #4f46e5; color: white; border: none;
  border-radius: 12px; font-weight: bold; cursor: pointer; margin-top: 10px;
}
.auth-footer { margin-top: 20px; font-size: 0.9rem; }
</style>