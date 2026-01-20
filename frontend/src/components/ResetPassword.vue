<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo-container">🔒</div>
        <h2>Nueva Contraseña</h2>
        <p>Estás a un paso de recuperar tu cuenta para <strong>{{ email }}</strong></p>
      </div>

      <form @submit.prevent="handleReset" class="auth-form">
        <div class="form-group">
          <label>Código de 6 dígitos</label>
          <input 
            v-model="form.code" 
            type="text" 
            maxlength="6" 
            class="code-input" 
            placeholder="000000" 
            required
          />
        </div>

        <div class="form-group">
          <label>Nueva Contraseña</label>
          <input v-model="form.newPassword" type="password" placeholder="Mínimo 8 caracteres" required />
        </div>

        <div class="form-group">
          <label>Confirmar Nueva Contraseña</label>
          <input v-model="form.confirmPassword" type="password" placeholder="Repite tu clave" required />
        </div>

        <button type="submit" class="btn-auth" :disabled="loading">
          {{ loading ? 'Actualizando...' : 'Cambiar y Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const email = ref('');
const loading = ref(false);

const form = ref({
  code: '',
  newPassword: '',
  confirmPassword: ''
});

onMounted(() => {
  email.value = route.query.email || '';
  if (!email.value) {
    alert("Falta el correo electrónico para continuar");
    router.push('/forgot-password');
  }
});

const handleReset = async () => {
  if (form.value.newPassword !== form.value.confirmPassword) {
    alert("Las contraseñas no coinciden.");
    return;
  }

  loading.value = true;
  try {
    await axios.post('/api/reset-password', {
      email: email.value,
      code: form.value.code,
      newPassword: form.value.newPassword
    });
    alert('¡Excelente! Contraseña actualizada. Ahora inicia sesión.');
    router.push('/login');
  } catch (error) {
    alert(error.response?.data?.error || 'Código inválido o error en el servidor.');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Reutilizamos los mismos estilos de ForgotPassword.vue */
.code-input {
  text-align: center;
  font-size: 1.8rem;
  letter-spacing: 8px;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  color: #4f46e5;
}
/* ... resto de estilos idénticos al anterior ... */
</style>