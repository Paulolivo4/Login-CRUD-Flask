<template>
  <div class="owner-layout">
    <nav class="sidebar">
      <div class="brand">
        <h3>👨‍🍳 Panel Dueño</h3>
        <small v-if="restaurant">{{ restaurant.nombre }}</small>
      </div>
      
      <ul class="nav-links">
        <li :class="{ active: currentTab === 'dashboard' }" @click="currentTab = 'dashboard'">
          📊 Resumen
        </li>
        <li :class="{ active: currentTab === 'menu' }" @click="currentTab = 'menu'">
          🍔 Mi Menú
        </li>
        <li :class="{ active: currentTab === 'reservas' }" @click="currentTab = 'reservas'">
          📅 Reservas
        </li>
      </ul>

      <div class="logout">
        <button @click="logout">Cerrar Sesión</button>
      </div>
    </nav>

    <main class="main-content">
      
      <div v-if="loading" class="loading-state">Cargando tu restaurante...</div>
      
      <div v-else>
        
        <header class="top-header">
          <h2>{{ getTitle() }}</h2>
          <div class="user-info">Hola, Dueño</div>
        </header>

        <div v-if="currentTab === 'dashboard'" class="dashboard-view">
          <div class="stats-grid">
            <div class="stat-card purple">
              <h3>Platos en Menú</h3>
              <p class="number">{{ stats.dishes_count }}</p>
            </div>
            <div class="stat-card blue">
              <h3>Reservas Totales</h3>
              <p class="number">{{ stats.reservations_count }}</p>
            </div>
            <div class="stat-card green">
              <h3>Ventas Estimadas</h3>
              <p class="number">${{ stats.total_sales }}</p>
              <small>Solo pagos con Tarjeta/Confirmados</small>
            </div>
          </div>
        </div>

        <div v-if="currentTab === 'menu'" class="menu-view">
          <div class="actions">
            <button class="btn-primary" @click="showModal = true">+ Nuevo Plato</button>
          </div>

          <div class="menu-grid">
            <div v-for="item in menus" :key="item.id" class="menu-card">
              <div class="card-img" :style="{ backgroundImage: `url(${item.foto || '/placeholder-food.jpg'})` }"></div>
              <div class="card-body">
                <h4>{{ item.nombre }}</h4>
                <p class="desc">{{ item.descripcion }}</p>
                <div class="price-row">
                  <span class="price">${{ item.precio }}</span>
                  <button class="btn-delete" @click="deleteItem(item.id)">🗑️</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="currentTab === 'reservas'" class="reservations-view">
          <div class="table-card">
            <table class="styled-table">
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Fecha</th>
                  <th>Personas</th>
                  <th>Plato Reservado</th>
                  <th>Método Pago</th>
                  <th>Estado</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="res in reservations" :key="res.id">
                  <td>
                    <div class="client-name">{{ res.cliente }}</div>
                  </td>
                  <td>{{ formatDate(res.fecha) }}</td>
                  <td>{{ res.personas }}</td>
                  <td>{{ res.plato }}</td>
                  <td>
                    <span class="payment-method">
                      {{ res.metodo_pago === 'TARJETA' ? '💳 Tarjeta' : '💵 Efectivo' }}
                    </span>
                  </td>
                  <td>
                    <span :class="['badge', res.estado_pago === 'PAGADO' ? 'paid' : 'pending']">
                      {{ res.estado_pago }}
                    </span>
                  </td>
                  <td><strong>${{ res.total }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </main>

    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nuevo Plato</h3>
        <form @submit.prevent="submitMenu">
          <input v-model="form.nombre" placeholder="Nombre del Plato" required />
          <textarea v-model="form.descripcion" placeholder="Descripción deliciosa..." required></textarea>
          <input v-model="form.precio" type="number" step="0.01" placeholder="Precio" required />
          
          <label class="file-label">
            Foto del Plato
            <input type="file" @change="handleFile" accept="image/*" />
          </label>
          
          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn-sec">Cancelar</button>
            <button type="submit" class="btn-pri">Guardar Plato</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();

const currentTab = ref('dashboard');
const loading = ref(true);
const restaurant = ref(null);
const menus = ref([]);
const reservations = ref([]);
const stats = ref({});
const showModal = ref(false);

const form = ref({ nombre: '', descripcion: '', precio: '' });
const photoFile = ref(null);

onMounted(async () => {
  await loadDashboard();
});

const loadDashboard = async () => {
  try {
    const res = await axios.get('/api/owner/dashboard-data');
    restaurant.value = res.data.restaurant;
    menus.value = res.data.menus;
    reservations.value = res.data.reservations;
    stats.value = res.data.stats;
  } catch (error) {
    if(error.response?.status === 403) router.push('/login');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleFile = (e) => { photoFile.value = e.target.files[0]; };

const submitMenu = async () => {
  const formData = new FormData();
  formData.append('nombre', form.value.nombre);
  formData.append('descripcion', form.value.descripcion);
  formData.append('precio', form.value.precio);
  if (photoFile.value) formData.append('foto', photoFile.value);

  try {
    await axios.post('/api/owner/menu/create', formData);
    showModal.value = false;
    form.value = { nombre: '', descripcion: '', precio: '' }; // Reset
    await loadDashboard(); // Recargar datos
  } catch (e) {
    alert('Error al crear plato');
  }
};

const deleteItem = async (id) => {
  if(!confirm('¿Borrar plato?')) return;
  try {
    await axios.delete(`/api/owner/menu/delete/${id}`);
    await loadDashboard();
  } catch (e) { alert('Error borrando'); }
};

const logout = () => { auth.logout(); router.push('/login'); };

const getTitle = () => {
  if (currentTab.value === 'dashboard') return 'Resumen del Negocio';
  if (currentTab.value === 'menu') return 'Gestión de Menú';
  return 'Listado de Reservas';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
};
</script>

<style scoped>
/* ESTILOS PREMIUM */
.owner-layout { display: flex; min-height: 100vh; background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }

/* SIDEBAR */
.sidebar { width: 250px; background: white; padding: 20px; display: flex; flex-direction: column; border-right: 1px solid #eee; }
.brand h3 { margin: 0; color: #333; }
.nav-links { list-style: none; padding: 0; margin-top: 40px; }
.nav-links li { padding: 12px 15px; cursor: pointer; border-radius: 8px; color: #666; margin-bottom: 5px; transition: 0.2s; }
.nav-links li:hover, .nav-links li.active { background: #e0e7ff; color: #4f46e5; font-weight: 600; }
.logout { margin-top: auto; }

/* MAIN */
.main-content { flex: 1; padding: 30px; }
.top-header { display: flex; justify-content: space-between; margin-bottom: 30px; }

/* STATS */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.stat-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.stat-card h3 { font-size: 0.9rem; color: #888; margin: 0; }
.stat-card .number { font-size: 2rem; font-weight: bold; margin: 10px 0; }
.purple .number { color: #8b5cf6; }
.blue .number { color: #3b82f6; }
.green .number { color: #10b981; }

/* MENU GRID */
.menu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
.menu-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.card-img { height: 150px; background-size: cover; background-position: center; }
.card-body { padding: 15px; }
.desc { font-size: 0.85rem; color: #666; height: 40px; overflow: hidden; }
.price-row { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.price { font-weight: bold; font-size: 1.1rem; color: #333; }
.btn-delete { background: #fee2e2; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }

/* TABLE */
.styled-table { width: 100%; background: white; border-radius: 12px; border-collapse: collapse; overflow: hidden; }
.styled-table th { background: #f3f4f6; text-align: left; padding: 15px; color: #555; }
.styled-table td { padding: 15px; border-top: 1px solid #eee; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
.paid { background: #d1fae5; color: #065f46; }
.pending { background: #fef3c7; color: #92400e; }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.modal-content { background: white; padding: 30px; border-radius: 12px; width: 400px; }
.modal-content input, .modal-content textarea { width: 100%; margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.btn-pri { background: #4f46e5; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
.btn-sec { background: #eee; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
.btn-primary { background: #4f46e5; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
</style>