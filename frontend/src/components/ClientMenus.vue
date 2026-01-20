<template>
  <div class="dashboard-layout">
    <header>
      <h1>Menús Disponibles (Cliente)</h1>
      <div class="user-info">
        <span>Hola, {{ authStore.user?.name }}</span>
        <button @click="logout" class="btn-logout">Cerrar Sesión</button>
      </div>
    </header>

    <main>
      <div class="card">
        <h3>Lista de Menús</h3>
        <p>Aquí se mostrarán las fotos y precios de los menús.</p>
        </div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const logout = async () => {
    await authStore.logout();
};
</script>

<style scoped>
header {
    background: #42b983; /* Verde Vue para diferenciar del admin */
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.btn-logout {
    background: #2c3e50;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 4px;
}
.card {
    border: 1px solid #ccc;
    padding: 20px;
    margin: 20px;
    border-radius: 5px;
}
</style>