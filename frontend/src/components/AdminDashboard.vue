<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="brand">
        <h2>🚀 Admin Panel</h2>
      </div>
      <div class="user-controls">
        <span>{{ authStore.user?.name }} (Admin)</span>
        <button @click="handleLogout" class="btn-logout">Salir</button>
      </div>
    </header>

    <div class="content-wrapper">
      <div class="actions-bar" style="margin-bottom: 20px;">
        <button class="btn-primary" @click="$router.push('/admin/restaurants/create')">
          🏢 Agregar Restaurante
        </button>
      </div>

      <div class="stats-cards">
        <div class="card stat-card blue">
          <h3>👥 Usuarios Totales</h3>
          <p class="number">{{ stats.total_users }}</p>
        </div>
        <div class="card stat-card green">
          <h3>🟢 Admins / Dueños / Clientes</h3>
          <p class="number">{{ stats.roles_distribution['Admin'] }} / {{ stats.roles_distribution['Dueño'] }} / {{ stats.roles_distribution['Cliente'] }}</p>
          <span class="subtext">Distribución real</span>
        </div>
        <div class="card stat-card orange">
          <h3>📅 Restaurantes</h3>
          <p class="number">{{ stats.total_restaurants }}</p>
        </div>
      </div>

      <div class="charts-container">
        <div class="card chart-card">
          <h4>📊 Actividad (Simulada)</h4>
          <div class="chart-wrapper">
             <Line v-if="loaded" :data="lineChartData" :options="chartOptions" />
          </div>
        </div>
        <div class="card chart-card">
          <h4>🍰 Distribución por Roles</h4>
          <div class="chart-wrapper">
             <Doughnut v-if="loaded" :data="doughnutChartData" :options="chartOptions" />
          </div>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-header">
          <h3>Gestionar Usuarios</h3>
          <button class="btn-primary" @click="openModal('create')">+ Nuevo Usuario</button>
        </div>

        <table class="styled-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>#{{ user.id }}</td>
              <td>
                <div class="user-profile">
                  <div class="avatar">{{ user.name?.charAt(0) }}</div>
                  <span class="name">{{ user.name }} {{ user.lastname }}</span>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="['badge', getRoleClass(user.role_id)]">
                  {{ getRoleName(user.role_id) }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="btn-icon edit" @click="openModal('edit', user)">✏️</button>
                <button class="btn-icon delete" @click="confirmDelete(user)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ modalMode === 'create' ? 'Crear Usuario' : 'Editar Usuario' }}</h3>
        <form @submit.prevent="submitUser">
          <input v-model="form.name" placeholder="Nombre" required />
          <input v-model="form.lastname" placeholder="Apellido" required />
          <input v-model="form.email" type="email" placeholder="Email" :disabled="modalMode==='edit'" required />
          <input v-if="modalMode==='create'" v-model="form.password" type="password" placeholder="Contraseña" required />
          
          <select v-model="form.role_id" required>
            <option value="1">Administrador</option>
            <option value="2">Dueño de Restaurante</option>
            <option value="3">Cliente</option>
          </select>

          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn-secondary">Cancelar</button>
            <button type="submit" class="btn-primary">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';
import { useRouter } from 'vue-router';

import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, ArcElement, Title, Tooltip, Legend
} from 'chart.js'
import { Line, Doughnut } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Title, Tooltip, Legend)

const authStore = useAuthStore();
const router = useRouter();

const users = ref([]);
const stats = ref({ total_users: 0, total_restaurants: 0, roles_distribution: { Admin: 0, Dueño: 0, Cliente: 0 } });
const loaded = ref(false);
const showModal = ref(false);
const modalMode = ref('create');
const form = ref({ name: '', lastname: '', email: '', password: '', role_id: 3 });

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  try {
    // 1. Cargar Usuarios para la tabla
    const usersRes = await axios.get('/admin/users');
    users.value = usersRes.data;

    // 2. Cargar Estadísticas para los gráficos y tarjetas
    const statsRes = await axios.get('/admin/dashboard-data');
    const d = statsRes.data.users_distribution;
    
    stats.value = {
      total_users: d.data.reduce((a, b) => a + b, 0),
      total_restaurants: statsRes.data.total_restaurants,
      roles_distribution: {
        'Admin': d.data[0] || 0,
        'Dueño': d.data[1] || 0,
        'Cliente': d.data[2] || 0
      }
    };
    
    loaded.value = true;
  } catch (error) {
    console.error("Error cargando dashboard:", error);
    if(error.response?.status === 401 || error.response?.status === 403) router.push('/login');
  }
};

const lineChartData = computed(() => ({
  labels: ['08:00', '12:00', '16:00', '20:00'],
  datasets: [{
    label: 'Actividad Hoy',
    backgroundColor: '#f87979',
    borderColor: '#f87979',
    data: [2, 10, 5, 15],
    tension: 0.4
  }]
}));

const doughnutChartData = computed(() => ({
  labels: ['Admin', 'Dueño', 'Cliente'],
  datasets: [{
    backgroundColor: ['#4f46e5', '#f59e0b', '#10b981'],
    data: [
      stats.value.roles_distribution['Admin'],
      stats.value.roles_distribution['Dueño'],
      stats.value.roles_distribution['Cliente']
    ]
  }]
}));

const chartOptions = { responsive: true, maintainAspectRatio: false };

const getRoleName = (id) => id == 1 ? 'Admin' : id == 2 ? 'Dueño' : 'Cliente';
const getRoleClass = (id) => id == 1 ? 'role-admin' : id == 2 ? 'role-owner' : 'role-client';

const openModal = (mode, user = null) => {
  modalMode.value = mode;
  form.value = user ? { ...user, password: '' } : { name: '', lastname: '', email: '', password: '', role_id: 3 };
  showModal.value = true;
};

const submitUser = async () => {
  try {
    if (modalMode.value === 'create') {
      await axios.post('/register', form.value);
    } else {
      await axios.put(`/admin/user/${form.value.id}`, form.value);
    }
    showModal.value = false;
    await loadData();
  } catch (error) {
    alert('Error: ' + (error.response?.data?.error || error.message));
  }
};

const confirmDelete = async (user) => {
  if(confirm(`¿Eliminar a ${user.name}?`)) {
    try {
      await axios.delete(`/admin/user/${user.id}`);
      await loadData();
    } catch (error) {
      alert('Error eliminando: ' + error.message);
    }
  }
};

const handleLogout = async () => {
  await authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
/* Estilos simplificados para el panel */
.admin-layout { background-color: #f4f6f9; min-height: 100vh; }
.admin-header { background: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.content-wrapper { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02); border: 1px solid #e1e4e8; margin-bottom: 1.5rem; }
.stats-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
.stat-card .number { font-size: 2.5rem; font-weight: bold; margin: 10px 0; color: #4f46e5; }
.charts-container { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }
.chart-wrapper { height: 300px; }
.styled-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.styled-table th, .styled-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
.badge { padding: 5px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
.role-admin { background: #fee2e2; color: #991b1b; }
.role-owner { background: #fef3c7; color: #92400e; }
.role-client { background: #dbeafe; color: #1e40af; }
.btn-primary { background: #4f46e5; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 15px; width: 400px; }
.modal-content input, .modal-content select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
</style>