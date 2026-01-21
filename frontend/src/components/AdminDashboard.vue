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
      <div class="actions-bar" style="margin-bottom: 20px;">
   <button class="btn-primary" @click="$router.push('/admin/restaurants/create')">
      🏢 Agregar Restaurante
   </button>
</div>
    </header>

    <div class="content-wrapper">
      
      <div class="stats-cards">
        <div class="card stat-card blue">
          <h3>👥 Usuarios Totales</h3>
          <p class="number">{{ stats.total_users }}</p>
        </div>
        <div class="card stat-card green">
          <h3>🟢 Usuarios Online</h3>
          <p class="number">{{ stats.active_sessions }}</p>
          <span class="subtext">Activos ahora mismo</span>
        </div>
        <div class="card stat-card orange">
          <h3>📅 Reservas Hoy</h3>
          <p class="number">12</p> </div>
      </div>

      <div class="charts-container">
        <div class="card chart-card">
          <h4>📊 Actividad de Usuarios (Logins/Reservas)</h4>
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
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>#{{ user.id }}</td>
              <td>
                <div class="user-profile">
                  <div class="avatar">{{ user.name.charAt(0) }}</div>
                  <div>
                    <span class="name">{{ user.name }} {{ user.lastname }}</span>
                  </div>
                </div>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="['badge', getRoleClass(user.role_id)]">
                  {{ getRoleName(user.role_id) }}
                </span>
              </td>
              <td>
                <span class="status-dot" :class="user.id % 2 === 0 ? 'online' : 'offline'"></span>
                {{ user.id % 2 === 0 ? 'Activo' : 'Desconectado' }}
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

// Importar componentes de Chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Line, Doughnut } from 'vue-chartjs'

// Registrar componentes de gráficos
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const authStore = useAuthStore();
const router = useRouter();

// DATOS
const users = ref([]);
const stats = ref({ total_users: 0, active_sessions: 0, roles_distribution: {} });
const loaded = ref(false);

// MODAL
const showModal = ref(false);
const modalMode = ref('create'); // 'create' o 'edit'
const form = ref({ name: '', lastname: '', email: '', password: '', role_id: 3 });

// --- CARGA INICIAL ---
onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  try {
    // 1. Cargar Usuarios
    const usersRes = await axios.get('/api/user/dashboard');
    users.value = usersRes.data;

    // 2. Cargar Estadísticas
    const statsRes = await axios.get('/api/user/stats');
    stats.value = statsRes.data;
    
    loaded.value = true;
  } catch (error) {
    console.error("Error cargando dashboard:", error);
    if(error.response?.status === 403) router.push('/login');
  }
};

// --- CONFIGURACIÓN DE GRÁFICOS ---

// Gráfico de Líneas (Usuarios Logueados / Actividad)
const lineChartData = computed(() => ({
  labels: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],
  datasets: [
    {
      label: 'Usuarios Activos (Tiempo Real)',
      backgroundColor: '#f87979',
      borderColor: '#f87979',
      data: [5, 12, 25, 20, 15, 30, stats.value.active_sessions + 10], // Datos simulados + real
      tension: 0.4
    }
  ]
}));

// Gráfico de Dona (Roles)
const doughnutChartData = computed(() => ({
  labels: ['Admin', 'Dueño', 'Cliente'],
  datasets: [
    {
      backgroundColor: ['#41B883', '#E46651', '#00D8FF'],
      data: [
        stats.value.roles_distribution['Admin'] || 0, 
        stats.value.roles_distribution['Dueño'] || 0, 
        stats.value.roles_distribution['Cliente'] || 0
      ]
    }
  ]
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
};

// --- LÓGICA CRUD ---

const getRoleName = (id) => {
    if(id == 1) return 'Admin';
    if(id == 2) return 'Dueño';
    return 'Cliente';
};
const getRoleClass = (id) => {
    if(id == 1) return 'role-admin';
    if(id == 2) return 'role-owner';
    return 'role-client';
};

const openModal = (mode, user = null) => {
    modalMode.value = mode;
    if (mode === 'edit' && user) {
        form.value = { ...user, password: '' }; // Copia datos
    } else {
        form.value = { name: '', lastname: '', email: '', password: '', role_id: 3 };
    }
    showModal.value = true;
};

const submitUser = async () => {
    try {
        if (modalMode.value === 'create') {
            await axios.post('/api/user/create', form.value);
            alert('Usuario creado!');
        } else {
            // Nota: Para editar necesitamos ID. Asegúrate que user_bp soporte PUT /update/ID
            await axios.put(`/api/user/update/${form.value.id}`, form.value);
            alert('Usuario actualizado!');
        }
        showModal.value = false;
        await loadData(); // Recargar tabla
    } catch (error) {
        alert('Error: ' + (error.response?.data?.error || error.message));
    }
};

const confirmDelete = async (user) => {
    if(confirm(`¿Eliminar a ${user.name}?`)) {
        try {
            await axios.delete(`/api/user/delete/${user.email}`);
            await loadData();
        } catch (error) {
            alert('Error eliminando: ' + error.message);
        }
    }
};

const handleLogout = async () => {
  await authStore.logout();
};
</script>

<style scoped>
/* ESTILOS MODERNOS Y AMIGABLES */
.admin-layout {
  background-color: #f4f6f9;
  min-height: 100vh;
  font-family: 'Segoe UI', sans-serif;
}

.admin-header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.content-wrapper {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

/* CARDS */
.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  border: 1px solid #e1e4e8;
}

/* Stats Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.stat-card h3 { font-size: 0.9rem; color: #666; margin: 0; }
.stat-card .number { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
.stat-card.blue .number { color: #3498db; }
.stat-card.green .number { color: #2ecc71; }
.stat-card.orange .number { color: #e67e22; }

/* Charts */
.charts-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.chart-wrapper {
  height: 250px;
  position: relative;
}

/* Table */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
}
.styled-table th { text-align: left; padding: 1rem; color: #666; font-size: 0.9rem; }
.styled-table td { padding: 1rem; border-top: 1px solid #eee; vertical-align: middle; }

/* User Profile in Table */
.user-profile { display: flex; align-items: center; gap: 10px; }
.avatar { 
  width: 35px; height: 35px; background: #e0e7ff; color: #4f46e5; 
  border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; 
}

/* Badges */
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.role-admin { background: #fee2e2; color: #991b1b; }
.role-owner { background: #fef3c7; color: #92400e; }
.role-client { background: #dbeafe; color: #1e40af; }

/* Status Dot */
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.status-dot.online { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
.status-dot.offline { background: #ccc; }

/* Buttons */
.btn-primary { background: #4f46e5; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; }
.btn-logout { background: transparent; border: 1px solid #ddd; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 5px; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center;
}
.modal-content {
  background: white; padding: 2rem; border-radius: 12px; width: 400px;
}
.modal-content input, .modal-content select {
  width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box;
}
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
</style>